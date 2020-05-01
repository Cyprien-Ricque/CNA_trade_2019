#!/usr/bin/python3.7

import os
import sys
from Utils import d_print
from enum import Enum


class Parser:

    def __init__(self, readSize):
        self._readSize = readSize
        self._line = ''
        self._buffer = ''
        self._dataTypeStr = ['setting', 'candle', 'stack', 'action']
        self._settings = {}
        self._stacks = {}
        self._order = -1

    def getNextLine(self):
        #print("getnextline\n", file=sys.stderr, flush=True)
        #self._buffer += os.read(0, self._readSize).decode()
        #while self._buffer.find('\n') == -1:
        #    print("getnextline 2\n", file=sys.stderr, flush=True)
        #    self._buffer += os.read(0, self._readSize).decode()
        #self._line = self._buffer[:self._buffer.find('\n')]
        #self._buffer = self._buffer[self._buffer.find('\n') + 1:]
        #print("getnextline END\n", file=sys.stderr, flush=True)
        self._line = input()
        return self._line

    def getDataType(self):
        for t in self._dataTypeStr:
            if t in self._line:
                return t
        return ''

    def getData(self):
        return getattr(self, self.getDataType(), self.dataUnknown)()

    def dataUnknown(self):
        print('data \"' + self._line + '\" unrecognized', file=sys.stderr, flush=True)
        return ''

    def setting(self):
        var = self._line.split(' ')[1]
        value = self._line[len("settings ") + len(var) + 1:].split(',')
        self._settings[var] = value
        # Debug
        print(self._settings, flush=True, file=sys.stderr)
        return self._settings

    def candle(self):
        rawData = self._line[len("update game next_candles "):].split(';')
        data = {}

        for t in rawData:
            values = t.split(',')
            data[values[0]] = dict()
            for i, v in enumerate(values[1:]):
                data[values[0]][self._settings['candle_format'][i]] = [float(v)]
        # Debug
        print(data, file=sys.stderr, flush=True)
        return data

    def stack(self):
        rawData = self._line[len("update game stacks "):].split(',')

        for r in rawData:
            self._stacks[r.split(':')[0]] = float(r.split(':')[1])
        # Debug
        print(self._stacks, file=sys.stderr, flush=True)
        return self._stacks

    def action(self):
        self._order = int(self._line[len('action order '):])
        # Debug
        print(self._order, file=sys.stderr, flush=True)
        return self._order
