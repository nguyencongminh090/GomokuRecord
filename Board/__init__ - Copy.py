from tkinter import *
import tomllib
from abc import ABC


def roundNum(number, places=0):
    place = 10 ** places
    rounded = (int(number * place + 0.5 if number >= 0 else -0.5)) / place
    if rounded == int(rounded):
        rounded = int(rounded)
    return rounded


def removeDup(a: list, b: list):
    a = a[:]
    for i in list(set(a) & set(b)):
        a.remove(i)
    return a


class EngineABC(ABC):
    def waitEngineReady(self) -> BooleanVar:
        ...

    def setInfo(self):
        ...

    def yxBoard(self, opening):
        ...

    def getAllMessage(self):
        ...

    def send(self, command):
        ...

    def startCalc(self):
        ...

    def stop(self):
        ...


class ParseMove:
    @staticmethod
    def __valid(move):
        if len(move) < 2:
            return False

        x = ord(move[0]) - 96
        y = int(move[1:])
        return 0 < x < 16 and 0 < y < 16

    def get(self, string):
        if string and string[0]:
            cur = string[0]
            string = string[1:]
            while string:
                if string[0].isnumeric():
                    cur += string[0]
                    string = string[1:]
                else:
                    break
            if self.__valid(cur):
                return [cur] + [*self.get(string)]
            else:
                return [*self.get(string)]
        else:
            return ''


class Board(Tk):
    CONFIG = tomllib.load(open('board.toml', 'rb'))

    def __init__(self):
        super().__init__()
        # BOARD PROPERTIES
        self.__size = self.CONFIG['size']
        self.__background = self.CONFIG['background_color']

        self.title('Board')
        self.geometry(f'{self.__size}x{self.__size}')
        self.resizable(0, 0)

        # SETUP BOARD
        self.__canvas   = Canvas(self, width=self.__size, height=self.__size,
                                 bg=self.__background, highlightthickness=0)
        self.__canvas.grid(column=0, row=0, sticky='news')

        self.__boardGap = self.__size * 0.05
        self.__distance = self.__size * 0.9 / 14
        self.__radius   = roundNum(self.__distance * 0.5 * 0.90)

        # COORDINATES
        self.__history     = []
        self.__redoHistory = []
        self.__lastMove    = ''
        self.__curPos      = []

        # COLOR
        self.__blackColor    = '#000000'
        self.__whiteColor    = '#ffffff'
        self.__lastMoveColor = '#ff0000'

        self.__drawBoard()

        # Engine
        self.__engine: EngineABC = ...
        self.__engineStatus      = False
        self.__nbestObj          = [False] * self.CONFIG['nbest']

    def __convertStr2Coord(self, move: str) -> (int, int):
        move = [ord(move[0]) - 97, 15 - int(move[1:])]
        x    = move[0] * self.__distance + self.__boardGap
        y    = move[1] * self.__distance + self.__boardGap
        return x, y

    def __drawBoard(self):
        self.__canvas.create_rectangle(self.__boardGap,
                                       self.__boardGap,
                                       self.__boardGap * 19,
                                       self.__boardGap * 19,
                                       width=2)

        for i in range(0, 15):
            self.__canvas.create_line(self.__boardGap,
                                      self.__boardGap + i * self.__distance,
                                      self.__boardGap * 19,
                                      self.__boardGap + i * self.__distance)
            self.__canvas.create_text(self.__boardGap * 19.5,
                                      self.__boardGap + i * self.__distance,
                                      text=f'{15 - i}',
                                      font=f"Helvetica {int(self.__boardGap * 0.3)} bold")

        for i in range(0, 15):
            self.__canvas.create_line(self.__boardGap + i * self.__distance,
                                      self.__boardGap,
                                      self.__boardGap + i * self.__distance,
                                      self.__boardGap * 19)

            self.__canvas.create_text(self.__boardGap + i * self.__distance,
                                      self.__boardGap * 19.5,
                                      text=f'{chr(65 + i)}',
                                      font=f"Helvetica {int(self.__boardGap * 0.3)} bold")

        self.__canvas.create_rectangle(self.__boardGap * 1.1 + 7 * self.__distance,
                                       self.__boardGap * 1.1 + 7 * self.__distance,
                                       self.__boardGap * 0.85 + 7 * self.__distance,
                                       self.__boardGap * 0.85 + 7 * self.__distance,
                                       fill='black')

    def __setLastMove(self, x, y, idx):
        # Show red spot for best move
        # self.__lastMove = self.__canvas.create_oval(x - self.__radius * 0.2, y - self.__radius * 0.2,
        #                                             x + self.__radius * 0.2, y + self.__radius * 0.2,
        #                                             fill=self.__lastMoveColor)
        color = self.__blackColor if idx % 2 == 1 else self.__whiteColor
        self.__canvas.itemconfig(self.__lastMove, fill=color)
        self.__lastMove = self.__canvas.create_text(x, y,
                                                    text=idx,
                                                    font=f"Helvetica {int(self.__boardGap * 0.3)}",
                                                    fill=self.__lastMoveColor)

    def __drawCircle(self, x, y, color=0):
        color = self.__blackColor if color == 0 else self.__whiteColor
        move = self.__canvas.create_oval(x - self.__radius, y - self.__radius,
                                         x + self.__radius, y + self.__radius, fill=color)
        return move

    def __addCoord(self, listCoord: [str]):
        curIdx = len(self.__curPos)
        for idx, move in enumerate(listCoord):
            # Debug number and color
            # print(f'Move: {move.ljust(5)} | {str(idx + curIdx + 1).ljust(5)} | {(idx + curIdx) % 2}')
            x, y = self.__convertStr2Coord(move)
            self.__drawCircle(x, y, (idx + curIdx) % 2)
            self.__setLastMove(x, y, (idx + curIdx) + 1)

    def setSize(self, size: int):
        self.__size = size
        self.__boardGap = self.__size * 0.05
        self.__distance = self.__size * 0.9 / 14
        self.__canvas.delete('all')
        self.__drawBoard()

    def sendPos(self, newPos: list):
        # Use in case newPos is string
        newPos = ParseMove().get(newPos)
        rePos = removeDup(newPos, self.__curPos)
        if not self.__curPos:
            self.__addCoord(newPos)
            self.__curPos = newPos
        elif len(newPos) > len(self.__curPos) and len(rePos) < len(newPos):
            self.__addCoord(rePos)
            self.__curPos = newPos
        elif len(newPos) < len(self.__curPos) or \
                (len(newPos) >= len(self.__curPos) and newPos != self.__curPos):
            self.resetBoard()
            self.__addCoord(newPos)
            self.__curPos = newPos
        if self.__engineStatus:
            # Send pos to analyze
            self.__engine.send('stop')
            self.resetAnalyze()
            self.__engine.yxBoard(newPos)
            self.__engine.startCalc()

    def resetBoard(self):
        self.resetAnalyze()
        self.__canvas.delete('all')
        self.__curPos.clear()
        self.__nbestObj = [False] * self.CONFIG['nbest']
        self.__drawBoard()

    def resetAnalyze(self):
        for idx, item in enumerate(self.__nbestObj):
            self.__canvas.delete(item)
            self.__nbestObj[idx] = False

    def connectEngine(self, engine: EngineABC):
        # Add draw func -> engine
        self.__engine       = engine
        self.__engineStatus = self.__engine.waitEngineReady()
        self.__engine.setInfo()
        self.__engineStatus = True

    def showAnalyze(self, move: str, ev: int, nbest: int = 0):
        x, y = self.__convertStr2Coord(move)
        if not self.__nbestObj[nbest]:
            self.__nbestObj[nbest] = self.__canvas.create_text(x, y,
                                                               text=ev,
                                                               font=f"Helvetica {int(self.__boardGap * 0.225)} bold",
                                                               fill='#C6FFF9', justify='center')
        else:
            try:
                self.__canvas.moveto(self.__nbestObj[nbest], x, y)
                x1, y1 = self.__canvas.coords(self.__nbestObj[nbest])
                self.__canvas.move(self.__nbestObj[nbest], x-x1, y-y1)
                self.__canvas.itemconfig(self.__nbestObj[nbest], text=ev)
            except:
                return


# TEST BOARD
# board = Board()
# board.sendPos('h2')
# board.sendPos('h2h3h4')
# board.sendPos('h2h3h4h5')
# board.sendPos('h3e8m5')
# board.sendPos('h3e7m5')
# board.sendPos('h2b3c7d8')
# board.mainloop()

# TEST PARSE_MOVE
# pos = 'h3e8m5'
# print(ParseMove().get(pos))
