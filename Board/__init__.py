from customtkinter import *
import tomllib


def roundNum(number, places=0):
    place = 10 ** places
    rounded = (int(number * place + 0.5 if number >= 0 else -0.5)) / place
    if rounded == int(rounded):
        rounded = int(rounded)
    return rounded


def removeDup(a: list, b: list):
    for i in list(set(a) & set(b)):
        a.remove(i)
    return a


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


class Board(CTk):
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
        self.__canvas = CTkCanvas(self, width=self.__size, height=self.__size,
                                  bg=self.__background, highlightthickness=0)
        self.__canvas.grid(column=0, row=0, sticky='news')

        self.__boardGap = self.__size * 0.05
        self.__distance = self.__size * 0.9 / 14
        self.__radius = roundNum(self.__distance * 0.5 * 0.90)

        # COORDINATES
        self.__history = []
        self.__redoHistory = []
        self.__lastMove = ''
        self.curPos = []

        # COLOR
        self.__blackColor = '#000000'
        self.__whiteColor = '#ffffff'
        self.__lastMoveColor = '#ff0000'

        self.__drawBoard()
        # self.sendPos(['a1' ,'a2'])
        # self.sendPos(['a1'])

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
        # self.__lastMove = self.__canvas.create_oval(x - self.__radius * 0.2, y - self.__radius * 0.2,
        #                                             x + self.__radius * 0.2, y + self.__radius * 0.2,
        #                                             fill=self.__lastMoveColor)
        color = self.__blackColor if idx % 2 == 1 else self.__whiteColor
        self.__canvas.itemconfig(self.__lastMove, fill=color)
        self.__lastMove = self.__canvas.create_text(x, y, text=idx,
                                                    font=f"Helvetica {int(self.__boardGap * 0.3)}",
                                                    fill=self.__lastMoveColor)

    def __drawCircle(self, x, y, color=0):
        color = self.__blackColor if color == 0 else self.__whiteColor
        move = self.__canvas.create_oval(x - self.__radius, y - self.__radius,
                                         x + self.__radius, y + self.__radius, fill=color)
        return move

    def __addCoord(self, listCoord: list):
        for idx, move in enumerate(listCoord):
            move = [ord(move[0]) - 97, 15 - int(move[1:])]
            x = move[0] * self.__distance + self.__boardGap
            y = move[1] * self.__distance + self.__boardGap
            self.__drawCircle(x, y, idx % 2)
            self.__setLastMove(x, y, idx + 1)

    def setSize(self, size: int):
        self.__size = size
        self.__boardGap = self.__size * 0.05
        self.__distance = self.__size * 0.9 / 14
        self.__canvas.delete('all')
        self.__drawBoard()

    def sendPos(self, newPos: list):
        # Use in case newPos is string
        # newPos = ParseMove().get(newPos)
        self.resetBoard()
        self.__addCoord(newPos)

    def resetBoard(self):
        self.__canvas.delete('all')
        self.__drawBoard()


# TEST BOARD
# board = Board()
# board.mainloop()

# TEST PARSE_MOVE
# pos = 'h3e8m5'
# print(ParseMove().get(pos))
