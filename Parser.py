#!/usr/bin/python3.7

import os


class Parser:
    def __init__(self, readSize):
        self._readSize = readSize

    def getNextLine(self):
        result = os.read(0, self._readSize)
        return str(result)

    def getCandles(self, line):
        pass

