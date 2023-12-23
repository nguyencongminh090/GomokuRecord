from selenium import webdriver
import re
from abc import ABC
from threading import Thread
from customtkinter import CTk


class BoardABC(ABC, CTk):
    def setSize(self, size):
        ...

    def sendPos(self, pos: str):
        ...

    def resetBoard(self):
        ...


class Website:
    def __init__(self,
                 username: str,
                 password: str,
                 board   : BoardABC):
        self.__board    = board
        self.__username = username
        self.__password = password
        self.__driver   = webdriver.Chrome()

    def connect(self):
        self.__driver.get('https://www.playok.com/vi/cocaro/')
        self.__driver.find_element('css selector', 'body > div.oa.ltbg > div.fl >'
                                   ' div > table > tbody > tr > td:nth-child(1) > button').click()
        self.__driver.find_element('css selector', '#id').send_keys(self.__username)
        self.__driver.find_element('css selector', '#lbox > form > p:nth-child(3)'
                                   ' > input[type=password]:nth-child(2)').send_keys(self.__password)
        self.__driver.find_element('css selector', '#lbox > form > p:nth-child(4) > button').click()
        self.__driver.find_element('css selector', '#bast > p:nth-child(1) > button').click()
        self.__driver.switch_to.window(self.__driver.window_handles[1])

    def realtimeRecord(self):
        listMove = []
        tableNum = 0
        while True:
            # Connect to table
            curLink = re.findall(r'#\d{1,3}', self.__driver.current_url)
            curLink = 0 if not curLink else curLink[0]
            if tableNum != curLink and curLink != 0:
                print('Current Link:', curLink)
                tableNum = curLink
            if tableNum == 0 or \
                    self.__driver.find_element('css selector',
                                               '#precont > div.gview.sbfixed > div.bsbb.tsb.sbclrd > div >'
                                               ' div.tcrdcont > div.tcrdtabcont > div > div:nth-child(2) >'
                                               ' button').get_attribute('class') != 'active':
                listMove.clear()
                continue
            tableMove = self.__driver.find_element('css selector',
                                                   '#precont > div.gview.sbfixed > div.bsbb.tsb.sbclrd >'
                                                   ' div > div.tcrdcont > div.tcrdpan > div:nth-child(1)'
                                                   ' > div.mb1s > table')
            curMove = re.findall(r'[a-z]+\d{1,2}', tableMove.text)

            if (not listMove and curMove) or (curMove and len(curMove) < len(listMove))\
                    or (curMove and listMove[-1] != curMove[-1]):
                listMove = curMove
                self.__board.sendPos(curMove)
                print('Current Line:', listMove)
                print('Length:', len(listMove))

    def quit(self):
        self.__driver.quit()
