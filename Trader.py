#!/usr/bin/python3.7

from Parser import Parser
from Strategy import Strategy
from Utils import d_print
import os


class Trader:
    def __init__(self):
        self._parser = Parser(2000)
        self._strategy = Strategy()

    def run(self):
        line = self._parser.getNextLine()
        d_print(line + '\n')
        data = self._parser.getData()
        self._strategy.newData(data)
        os.write(1, self._strategy.predict().encode())
