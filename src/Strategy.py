#!/usr/bin/python3.7

from src.Indicators import Indicators
import pandas as pd
import numpy as np
import keras
from keras.models import Model
from keras.layers import Dense, Dropout, LSTM, Input, Activation
from keras import optimizers
from sklearn import preprocessing
import sys


class Strategy:
    def __init__(self):
        self.data_ = None
        self.indicators_ = Indicators(40)
        self.period_ = 30
        self.model_ = None

    def newData(self, data):
        if self.data_ is None:
            self.data_ = pd.DataFrame(data)
        else:
            self.data_ = pd.concat([self.data_, pd.DataFrame(data)], ignore_index=True)

    def calcIndicators(self):
        self.indicators_.calcIndicators(self.data_, ['current', 'MMA', 'MME'])

    def train(self):
        self.calcIndicators()

        X = self.indicators_.getIndicators().values
        X = np.array([X[i:i + self.period_].copy() for i in range(self.indicators_.getPeriod(), X.shape[0] - self.period_)])
        y = self.indicators_.getIndicators().current_PP.values
        y = np.array([y[i + self.period_] for i in range(self.indicators_.getPeriod(), y.shape[0] - self.period_)])

        # print('X', X)
        # print('y', y)
        inputLSTM = Input(shape=(self.period_, X.shape[2]), name='input')

        print("INPUT SIZE ", inputLSTM)
        print("INPUT SIZE2 ", X.shape)
        print("OUTPUT SIZE ", y.shape)
        x = LSTM(self.period_, name='LSTM_0')(inputLSTM)
        x = Dropout(0.1, name='LSTM_dropout_0')(x)
        x = Dense(64, name='dense_0')(x)
        x = Activation('sigmoid', name='sigmoid_0')(x)
        x = Dense(1, name='dense_1')(x)
        output = Activation('linear', name='linear_output')(x)

        self.model_ = Model(inputs=inputLSTM, outputs=output)
        adam = optimizers.Adam(lr=0.0005)
        self.model_.compile(optimizer=adam, loss='mse')
        self.model_.fit(x=X, y=y, batch_size=32, epochs=50, shuffle=True, validation_split=0.1)

    def predict(self, wallet):
        X = self.indicators_.getIndicators().values
        dataNormalizer = preprocessing.MinMaxScaler()
        X = dataNormalizer.fit_transform(X)
        X = np.array([X[i:i + self.period_].copy() for i in range(self.indicators_.getPeriod(), X.shape[0] - self.period_)])
        y_pred = self.model_.predict(X)
        pred = (y_pred[-1] * self.indicators_.getScaleValues()['current_max']) + self.indicators_.getScaleValues()['current_min']
        print("prediction ", pred[0], file=sys.stderr)

        if wallet.haveEnough(buy=True, pair=['USDT', 'ETH'], amount=0.01) and pred[0] > self.data_.loc[:, 'close'].iloc[-1]:
            return 'buy USDT_ETH ' + wallet.buy(pair=['USDT', 'ETH']) + '\n'
        elif wallet.haveEnough(buy=False, pair=['USDT', 'ETH'], amount=0.01):
            return 'sell USDT_ETH ' + wallet.sell(pair=['USDT', 'ETH'], percent=50) + '\n'

        return 'pass\n'





