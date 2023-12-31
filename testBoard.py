from Board import Board
from Engine import Engine
import time


board = Board()
engine = Engine(board.showAnalyze)
board.connectEngine(engine)
board.sendPos('m3l4k5')
board.mainloop()
# noinspection PyProtectedMember
engine._Engine__engine.kill()
