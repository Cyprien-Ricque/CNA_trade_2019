import os
import sys
import pandas as pd


class Indicators:
    def __init__(self, period):
        self._indicators = {}
        self._period = period
        self._indList = ['mean', 'current']
        self._data = pd.DataFrame()
    
    def addData(self, newData):
        self._data.append(pd.DataFrame(newData))

    def getIndicatorsList(self):
        return self._indList

    def getIndicators(self):
        return self._indicators

    def indUnknown(self, ind):
        print("Indicator " + ind + " unknown", flush=True, file=sys.stderr)
        print("Indicators available : ", file=sys.stderr, end='')
        for ind in self._indList:
            print(ind, file=sys.stderr, end='')
            if ind != self._indList[-1]:
                print(', ', file=sys.stderr, end='')

    def calcIndicators(self, data, indList):
        self._data = data
        for ind in indList:
            getattr(self, ind, self.indUnknown)(ind)

    def current(self, ind):
        self._indicators['current'] = self._data.iloc[-1:, :].loc[:, 'open'].squeeze()
        print("current", self._data.head(), file=sys.stderr)

    def mean(self, ind):
        self._indicators['mean'] = self._data.iloc[-self._period:, :].loc[:, 'open'].mean()
        print(self._indicators['mean'], file=sys.stderr)


