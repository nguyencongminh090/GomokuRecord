from Board import Board
from Website import Website
from threading import Thread


def main():
    username = 'bongma'
    password = 'xxxxx'
    board = Board()

    website = Website(username, password, board=board)
    website.connect()
    Thread(target=website.realtimeRecord, daemon=True).start()
    board.mainloop()
    website.quit()


if __name__ == '__main__':
    main()
