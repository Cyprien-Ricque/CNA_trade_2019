#!/usr/bin/python3.7

import os
import sys
from enum import Enum


class Parser:

    def __init__(self):
        self.line_ = ''
        self.buffer_ = ''
        self.dataTypeStr_ = ['setting', 'candle', 'stack', 'action']
        self.settings_ = {}
        self.stacks_ = {}
        self.order_ = -1

    def getNextLine(self):
        self.line_ = input()

    def getDataType(self):
        for t in self.dataTypeStr_:
            if t in self.line_:
                return t
        return ''

    def getData(self):
        return getattr(self, self.getDataType(), self.dataUnknown)()

    def dataUnknown(self):
        print('data \"' + self.line_ + '\" unrecognized', file=sys.stderr, flush=True)
        return ''

    def setting(self):
        var = self.line_.split(' ')[1]
        value = self.line_[len("settings ") + len(var) + 1:].split(',')
        self.settings_[var] = value
        return self.settings_

    def candle(self):
        rawData = self.line_[len("update game next_candles "):].split(';')
        data = {}

        for t in rawData:
            values = t.split(',')
            data[values[0]] = dict()
            for i, v in enumerate(values[1:]):
                data[values[0]][self.settings_['candle_format'][i + 1]] = float(v)
        return data

    def stack(self):
        rawData = self.line_[len("update game stacks "):].split(',')

        for r in rawData:
            self.stacks_[r.split(':')[0]] = float(r.split(':')[1])
        return self.stacks_

    def action(self):
        self.order_ = int(self.line_[len('action order '):])
        return self.order_
