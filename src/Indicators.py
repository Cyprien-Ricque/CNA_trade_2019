import os
import sys
import pandas as pd
import numpy as np


class Indicators:
    def __init__(self, period):
        self.indicators_ = {}
        self.period_ = period
        self.indList_ = ['current', 'MMA']
        self.data_ = pd.DataFrame()
        self.iter_ = 1
    
    def addData(self, newData):
        self.data_.append(pd.DataFrame(newData))

    def getIndicatorsList(self):
        return self.indList_

    def getIndicators(self):
        return self.indicators_

    def indUnknown(self, ind):
        print("Indicator " + ind + " unknown", flush=True, file=sys.stderr)
        print("Indicators available : ", file=sys.stderr, end='')
        for ind in self.indList_:
            print(ind, file=sys.stderr, end='')
            if ind != self.indList_[-1]:
                print(', ', file=sys.stderr, end='')

    def calcIndicators(self, data, indList):
        self.iter_ += 1
        self.data_ = data
        for ind in indList:
            getattr(self, ind, self.indUnknown)(ind)

    def current(self, ind):
        if 'current' not in self.indicators_:
            self.indicators_['current'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['current']):
            return None
        self.indicators_['current'].append(self.data_.iloc[-1:, :].loc[:, 'close'].squeeze())

    def increase(self):
        if 'increase' not in self.indicators_:
            self.indicators_['increase'] = [self.data_.iloc[-1:, :].loc[:, 'increase'].squeeze()]
            self.indicators_['increase%'] = [self.data_.iloc[-1:, :].loc[:, 'increase%'].squeeze()]
        if self.iter_ == len(self.indicators_['increase']):
            return None

        self.indicators_['increase'].append(0)

    def decrease(self):
        pass

    def MMA(self, ind):
        if 'MMA' not in self.indicators_:
            self.indicators_['MMA'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['MMA']):
            return None

        self.indicators_['MMA'].append(self.data_.iloc[-self.period_:, :].loc[:, 'close'].mean())

    def MME(self, ind=None, period=-1):
        if 'MME' not in self.indicators_:
            self.indicators_['MME'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['MME']):
            return None
        P = self.period_ if period == -1 else period

        C = self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()
        K = 2 / (P + 1)
        R = C - (self.indicators_['MME'][-1]) * K + (self.indicators_['MME'][-1])
        if period != -1:
            return R
        self.indicators_['MME'].append(R)

    def MMP(self, ind):
        if 'MMP' not in self.indicators_:
            self.indicators_['MMP'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['MMP']):
            return None

        S = np.array([(self.period_ - i) * self.data_.iloc[-(i + 1):-(i + 1), :].loc[:, 'close'].squeeze() for i in range(self.period_)]).sum()
        self.indicators_['MMP'].append(S / (self.period_ * (self.period_ + 1) / 2))

    def MML(self, ind):
        if 'MML' not in self.indicators_:
            self.indicators_['MML'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['MML']):
            return None

        C = self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()
        self.indicators_['MML'].append(C - (self.indicators_['MML'][-1]) * (1 / self.period_) + (self.indicators_['MML'][-1]))

    def MACD(self, ind):
        if 'MACD' not in self.indicators_:
            self.indicators_['MACD'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['MACD']):
            return None

        R = self.MME(period=26) - self.MME(period=12)
        self.indicators_['MACD'].append(R)

    def RSI(self, ind):
        # RSI= 100 - [100/(1+H/B)]
        # H qui est la moyenne des hausses pendant les X dernières Unités de Temps (UT).
        # B qui est la moyenne des baisses pendant les X dernières Unités de Temps (UT).
        # X= la valeur du RSI

        if 'RSI' not in self.indicators_:
            self.indicators_['RSI'] = [self.data_.iloc[-1:, :].loc[:, 'close'].squeeze()]
        if self.iter_ == len(self.indicators_['RSI']):
            return None

        B = 0
        H = 0
        R = 100 - (100 / (1 + H / B))



