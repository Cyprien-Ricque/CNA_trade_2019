import os
import sys
import pandas as pd
import numpy as np


class Indicators:
    def __init__(self, short_period, long_period, indicators):
        self.data_ = None
        self.periods_ = np.sort([short_period, long_period])
        self.fctList_ = indicators
        self.indUPList_ = ['current', 'evolution', 'MACD']
        self.indList_ = [i + '_' + str(p) for p in self.periods_ for i in list(set(indicators) - set(self.indUPList_))] + self.indUPList_
        self.indicators_ = pd.DataFrame([[0 for i in self.indList_]], columns=self.indList_)
        self.data_ = pd.DataFrame()
        self.iter_ = 1
        self.actionsStarted_ = False
        self.scaleValues_ = {}
        self.series0_ = pd.Series([0 for i in self.indicators_.columns], index=self.indicators_.columns)

    def newData(self, data):
        if self.data_ is None:
            data = {**{item: [data[item]] for item in data}}
            self.data_ = pd.DataFrame(data)
        else:
            self.data_ = self.data_.append(pd.Series(data), ignore_index=True)

    def getPeriod(self):
        return self.periods_

    def getScaleValues(self):
        return self.scaleValues_

    def getIndicatorsList(self):
        return self.indList_

    def getIndicators(self, cols):
        df = pd.DataFrame(self.indicators_)
        return df.loc[:, cols]

    def getIndicators_PP(self):
        return self.indicators_.iloc[:, list(pd.Series(list(self.indicators_.columns)).str.contains('PP'))]

    def indUnknown(self, ind):
        print("Indicator \"" + ind + "\" unknown", flush=True, file=sys.stderr)
        print("Indicators available : ", file=sys.stderr, end='')
        for ind in self.indList_:
            print(ind, file=sys.stderr, end='')
            if ind != self.indList_[-1]:
                print(', ', file=sys.stderr, end='')
        print("\n", end='', file=sys.stderr)

    def preprocess(self):
        self.actionsStarted_ = True

        for c in self.indicators_.columns:
            self.scaleValues_[c + '_min'] = self.indicators_.loc[:, c].min()
            self.scaleValues_[c + '_max'] = self.indicators_.loc[:, c].max()
            self.indicators_.loc[:, c + '_PP'] = self.indicators_.loc[:, c].apply(lambda x: (x - self.scaleValues_[c + '_min']) / self.scaleValues_[c + '_max'])
        print(self.scaleValues_['MACD' + '_min'])
        print(self.scaleValues_['MACD' + '_max'])

    def isFirstActionPassed(self):
        return self.actionsStarted_

    def calcIndicators(self):
        self.iter_ += 1
        self.indicators_ = self.indicators_.append(self.series0_, ignore_index=True)
        if self.data_.shape[0] < 2:
            return

        for ind in self.fctList_:
            for p in self.periods_:
                getattr(self, ind, self.indUnknown)(p, ind + '_' + str(p))

        if self.actionsStarted_ is True:
            for ind in self.indList_:
                self.indicators_.loc[:, ind + '_PP'].iloc[-1] = (self.indicators_.loc[:, ind].iloc[-1] - self.scaleValues_[ind + '_min']) / self.scaleValues_[ind + '_max']

    def current(self, period, ind):
        self.indicators_.current.iloc[-1] = self.data_.close.iloc[-1]

    def evolution(self, period, ind):
        self.indicators_.evolution.iloc[-1] = self.data_.close.iloc[-1] - self.data_.close.iloc[-2]

    def MMA(self, period, ind):
        self.indicators_.loc[:, ind].iloc[-1] = self.data_.close.iloc[-period:].mean()

    def MME(self, period, ind):
        C = self.data_.close.iloc[-1]
        K = 2 / (period + 1)
        self.indicators_.loc[:, ind].iloc[-1] = C - (self.indicators_.loc[:, ind].iloc[-2]) * K + (self.indicators_.loc[:, ind].iloc[-2])

    def MMP(self, period, ind):
        P = period if self.data_.close.__len__() >= period else self.data_.close.__len__()
        S = np.array([(P - i) * self.data_.close.iloc[-i] for i in range(1, P)]).sum()
        self.indicators_.loc[:, ind].iloc[-1] = S / (P * (P + 1) / 2)

    def MML(self, period, ind):
        self.indicators_.loc[:, ind].iloc[-1] = self.data_.close.iloc[-1] - (self.indicators_.loc[:, ind].iloc[-2]) * (1 / period) + (self.indicators_.loc[:, ind].iloc[-2])

    def MACD(self, period, ind):
        self.indicators_.MACD.iloc[-1] = self.indicators_.loc[:, 'MME_' + str(self.periods_[1])].iloc[-1] - self.indicators_.loc[:, 'MME_' + str(self.periods_[0])].iloc[-1]

    def RSI(self, period, ind):
        S = self.indicators_.evolution.iloc[-period:]
        H = S[S > 0].mean()
        B = S[S < 0].mean()
        self.indicators_.loc[:, ind].iloc[-1] = 100 * H / (H - B)

    # TODO Faire la diff entre les 2

    def BLG_UP(self, period, ind):
        std = self.data_.close.iloc[-period:].std()
        self.indicators_.loc[:, ind].iloc[-1] = self.indicators_.loc[:, 'MME_' + str(period)].iloc[-1] + std * 2

    def BLG_DOWN(self, period, ind):
        std = self.data_.close.iloc[-period:].std()
        self.indicators_.loc[:, ind].iloc[-1] = self.indicators_.loc[:, 'MME_' + str(period)].iloc[-1] - std * 2
