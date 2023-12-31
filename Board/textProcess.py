from queue import Queue, Empty


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


def removeDup(a: list, b: list):
    a = a[:]
    for i in list(set(a) & set(b)):
        a.remove(i)
    return a


class TextComparison:
    @staticmethod
    def removeDup(a: list, b: list):
        a = a[:]
        for i in list(set(a) & set(b)):
            a.remove(i)
        return a

    @staticmethod
    def compareList(a, b):
        # Assume len(a) > len(b)
        c = removeDup(a, b)

        ...


class Position:
    def __init__(self):
        self.__curPos: list[str] = []
        self.__index : int       = 0
        self.__queue : Queue     = Queue()

    def addCoord(self, listCoord: list[str]):
        ...

    def sendPos(self, stringPos: str):
        ...


p = Position()
p.sendPos('h3e8m5')
p.sendPos('h3e7m5')
p.sendPos('h2e3')
p.sendPos('h3f3c2d7')