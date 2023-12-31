from Board import Board
from Website import Website
from Engine import Engine
from threading import Thread


# noinspection PyProtectedMember
def main():
    username = 'user'
    password = 'pass'
    board    = Board()
    engine   = Engine(board.showAnalyze)
    board.connectEngine(engine)
    website  = Website(username, password, board=board)
    website.connect()
    Thread(target=website.realtimeRecord, daemon=True).start()
    board.mainloop()
    engine._Engine__engine.kill()
    website.quit()


if __name__ == '__main__':
    main()
