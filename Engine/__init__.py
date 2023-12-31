from queue import Queue, Empty
from threading import Thread
import subprocess
import tomllib
import psutil
import math


def roundNum(number, places=0):
    place = 10 ** places
    rounded = (int(number * place + 0.5 if number >= 0 else -0.5)) / place
    if rounded == int(rounded):
        rounded = int(rounded)
    return rounded


class NonBlockingStreamReader:
    """
    stdout -> string
    Read output from engine
    Output include 2 types:
        - Message (start with MESSAGE ...)
        - No prefix (ex: "OK", ...)
        - Coord ("7,7", ...)
    """

    def __init__(self, stream):
        self.__stream = stream
        self.__queueMessage = Queue()
        self.__queueOutput = Queue()
        self.__queueCoord = Queue()

        self.__thread = Thread(target=self.__populateQueue)
        self.__thread.daemon = True
        self.__thread.start()

    def __populateQueue(self):
        while True:
            line = self.__stream.readline().strip()
            if line == '':
                continue
            elif self.isMessage(line):
                self.__queueMessage.put(line)
            elif self.isCoord(line):
                self.__queueCoord.put(line)
            elif not self.isError(line):
                self.__queueOutput.put(line)
            elif line is None:
                break

    def isOutputQueueEmpty(self):
        return self.__queueOutput.empty()

    def isMessageQueueEmpty(self):
        return self.__queueMessage.empty()

    def isCoordQueueEmpty(self):
        return self.__queueCoord.empty()

    @staticmethod
    def isMessage(line):
        return line.lower().startswith('message')

    @staticmethod
    def isError(line: str):
        return line.lower().startswith('error')

    @staticmethod
    def isCoord(line):
        if line.lower() == 'swap':
            return True
        for coord in line.split():
            if not coord.split(',')[0].isnumeric() or not coord.split(',')[1].isnumeric():
                return False
        return True

    def getMessage(self, timeout=0.0):
        try:
            output = self.__queueMessage.get(block=True, timeout=timeout)
            return output if output is not None else ''
        except Empty:
            return None

    def getOutput(self, timeout=0.0):
        try:
            output = self.__queueOutput.get(block=True, timeout=timeout)
            return output if output is not None else ''
        except Empty:
            return None

    def getCoord(self, timeout=0.0):
        try:
            output = self.__queueCoord.get(block=True, timeout=timeout)
            return output.removesuffix('\n') if output is not None else ''
        except Empty:
            return None


class Engine:
    CONFIG = tomllib.load(open('board.toml', 'rb'))

    def __init__(self, func):
        self.__engine = subprocess.Popen(self.CONFIG['engine'],
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         bufsize=1, universal_newlines=True)
        self.stdoutEngine = NonBlockingStreamReader(self.__engine.stdout)
        self.info_dict = {
            'timeout_match': 0,
            'timeout_turn' : 0,
            'game_type'    : 1,
            'rule'         : 1,
            'usedatabase'  : 1}
        self.__nbest    = self.CONFIG['nbest']
        self.__drawFunc = func

    @staticmethod
    def __waitFor(func):
        output = func()
        while output is None:
            output = func()
            continue
        return output

    def setInfo(self, info=None):
        # Send game info to engine
        if info is None:
            info = {}

        self.info_dict.update(info)
        for i in self.info_dict:
            self.send('INFO', i, self.info_dict[i])

    def __isRunning(self):
        return psutil.Process(self.__engine.pid).is_running()

    def send(self, *command):
        # Send command to engine
        new_command = []
        for i in range(len(command)):
            new_command.append(str(command[i]).upper() if i == 0 else str(command[i]))
        # print(f'<- {" ".join(new_command)}\n')
        self.__engine.stdin.write(' '.join(new_command) + '\n')

    def getAllMessage(self):
        while not self.stdoutEngine.isMessageQueueEmpty():
            self.stdoutEngine.getMessage()

    def isReady(self):
        output = self.stdoutEngine.getOutput(1)
        return output.upper() == 'OK' if output is not None else False

    def waitEngineReady(self):
        self.send('start 15')
        while not self.isReady():
            if not self.__isRunning():
                return False
            continue
        self.getAllMessage()
        return True

    def board(self, opening):
        # Send BOARD command (Set board position)
        self.send('board')
        for move in range(len(opening)):
            if len(opening) % 2 == move % 2:
                self.send(opening[move] + ',' + '1')
            else:
                self.send(opening[move] + ',' + '2')
        self.send('done')

    def yxBoard(self, opening):
        self.send('yxboard')
        for i, move in enumerate(opening):
            _move = f'{ord(move[0]) - 97},{int(move[1:]) - 1}'
            if len(opening) % 2 == i % 2:
                self.send(_move + ',' + '1')
            else:
                self.send(_move + ',' + '2')
        self.send('done')

    def startCalc(self):
        self.send(f'yxnbest {self.CONFIG["nbest"]}')
        Thread(target=self.__display, daemon=True).start()

    def __display(self):
        def calcWinrate(ev):
            x = int(ev) / 200
            return f'{roundNum(((math.e ** x) / (math.e ** x + 1)) * 100, 1)}%'

        def extractMessage(string: str) -> [str]:
            string  = string.strip().split()
            pv      = string[string.index('pv') + 1]
            ev      = string[string.index('ev') + 1]
            ev      = calcWinrate(ev) if ev.removeprefix('-').isnumeric() else ev
            multiPv = int(string[string.index('multipv') + 1]) - 1 if 'multipv' in message else 0
            return pv, ev, multiPv

        while self.stdoutEngine.isCoordQueueEmpty():
            if not self.stdoutEngine.isMessageQueueEmpty():
                message = ' '.join(self.stdoutEngine.getMessage().split()[1:]).lower()
                # print('Message:', message)
                if 'depth' in message and 'pv' in message:
                    _pv, _ev, _multiPv = extractMessage(message)
                    self.__drawFunc(_pv, _ev, _multiPv)
        self.stdoutEngine.getCoord()
        self.getAllMessage()
