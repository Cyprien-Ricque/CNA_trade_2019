#!/usr/bin/python3.7

import logging
import os
from src.Indicators import Indicators
import pandas as pd
import numpy as np
import keras
import tensorflow as tf
from keras.models import Model
from keras.layers import Dense, Dropout, LSTM, Input, Activation
from keras import optimizers
from sklearn import preprocessing
from os import path
from os.path import dirname
import sys
import shutil
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
# logging.getLogger('tensorflow').setLevel(logging.FATAL)


class Strategy:
    def __init__(self, updateModel=True):
        self.data_ = None
        self.indicators_ = Indicators(18)
        self.period_ = 30
        self.dir_ = dirname(dirname(os.path.realpath(__file__))) + '/tradeModel'
        self.model_ = None
        if path.exists(self.dir_):
            self.model_ = tf.keras.models.load_model(self.dir_)
        self.updateModel_ = updateModel
        self.tmp = True

    def newData(self, data):
        if self.data_ is None:
            data = {**{item: [data[item]] for item in data}}
            self.data_ = pd.DataFrame(data)
        else:
            self.data_ = self.data_.append(pd.Series(data), ignore_index=True)

    def calcIndicators(self):
        print("Calcul des Indicateurs")
        self.indicators_.calcIndicators(self.data_, ['current', 'MMA', 'MME', 'MMP', 'MACD', 'evolution', 'BLG_UP', 'BLG_DOWN'])
#        self.indicators_.calcIndicators(self.data_, ['current', 'MMA', 'MME', 'MMP', 'evolution', 'MACD', 'RSI', 'BLG_UP', 'BLG_DOWN'])

    def createModel(self, x, y):
        print("CREATE MODEL", x, y)
        inputLSTM = Input(shape=(x, y), name='input')

        # print("INPUT SIZE ", inputLSTM)
        # print("INPUT SIZE2 ", X.shape)
        # print("OUTPUT SIZE ", y.shape)

        x = LSTM(self.period_, name='LSTM_0')(inputLSTM)
        x = Dropout(0.05, name='LSTM_dropout_0')(x)
        x = Dense(64, name='dense_0')(x)
        x = Activation('sigmoid', name='sigmoid_0')(x)
        x = Dense(1, name='dense_1')(x)
        output = Activation('linear', name='linear_output')(x)

        self.model_ = Model(inputs=inputLSTM, outputs=output)
        adam = optimizers.Adam(lr=0.0003)
        self.model_.compile(optimizer=adam, loss='mse')

    def removeTrainedModel(self):
        try:
            if path.exists(self.dir_):
                os.remove(self.dir_)
        except IsADirectoryError:
            shutil.rmtree(self.dir_)
        print("MODEL REMOVED")

    def train(self):
        self.calcIndicators()

        X = self.indicators_.getIndicators().values
        X = np.array([X[i:i + self.period_].copy() for i in range(self.period_, X.shape[0] - self.period_)])
        y = self.indicators_.getIndicators().current_PP.values
        y = np.array([y[i + self.period_] for i in range(self.period_, y.shape[0] - self.period_)])

        print('X', X)
        print('y', y)
        print("Shape: ", self.period_, " | ", X.shape, " | ", y.shape)

        if self.model_ is None:
            self.createModel(self.period_, X.shape[2])
            print("CREATE MODEL")

        self.model_.fit(x=X, y=y, batch_size=32, epochs=55, validation_split=0.1)
        print("FIT MODEL")

        self.removeTrainedModel()

        self.model_.save(self.dir_)

    def predict(self, wallet):
        # print('predict', file=sys.stderr)
        X = self.indicators_.getIndicators().values
        X = np.array([X[i:i + self.period_].copy() for i in range(X.shape[0] - self.period_ - 1, X.shape[0] - self.period_)])
        y_pred = self.model_.predict(np.array([X[-1]]))
        pred = (y_pred[-1] * self.indicators_.getScaleValues()['current_max']) + self.indicators_.getScaleValues()['current_min']
        # print("prediction ", pred[0], file=sys.stderr)

        # if self.tmp:
        #     self.tmp = False
        #     return 'buy USDT_ETH ' + wallet.buy(['USDT', 'ETH'], 100)

        if wallet.haveEnough(buy=True, pair=['USDT', 'ETH'], amount=0.01) and pred[0] > self.data_.loc[:, 'close'].iloc[-1]:
            return 'buy USDT_ETH ' + wallet.buy(pair=['USDT', 'ETH'], percent=5)
        elif wallet.haveEnough(buy=False, pair=['USDT', 'ETH'], amount=0.01):
            return 'sell USDT_ETH ' + wallet.sell(pair=['USDT', 'ETH'], percent=50)

        return 'pass\n'

