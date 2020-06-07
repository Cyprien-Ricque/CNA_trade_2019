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
    def __init__(self, pairs, updateModel=False):
        self.indicatorsLongPeriod_ = 24
        self.indicatorsShortPeriod_ = 12
        self.LSTMPeriod_ = 30
        self.YPeriod_ = 8
        self.pairs_ = pairs
        self.indicators_ = {p[0] + '_' + p[1]: Indicators(self.indicatorsShortPeriod_, self.indicatorsLongPeriod_, ['MMA', 'MME', 'MMP', 'MACD', 'evolution', 'BLG_UP', 'BLG_DOWN']) for p in pairs}

        self.dir_ = dirname(dirname(os.path.realpath(__file__))) + '/tradeModel'
        self.model_ = None
        self.updateModel_ = updateModel
        if path.exists(self.dir_):
            self.model_ = tf.keras.models.load_model(self.dir_)

        self.tmp = True

    def newData(self, data):
        for p in self.pairs_:
            self.indicators_[p[0] + '_' + p[1]].newData(data[p[0] + '_' + p[1]])

    def calcIndicators(self):
        for p in self.pairs_:
            self.indicators_[p[0] + '_' + p[1]].calcIndicators()

    def createModel(self, x, y):
        print("CREATE MODEL", x, y, file=sys.stderr)
        inputLSTM = Input(shape=(x, y), name='input')

        x = LSTM(self.LSTMPeriod_, name='LSTM_0')(inputLSTM)
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
        print("MODEL REMOVED", file=sys.stderr)

    def train(self):

        if self.indicators_[self.pairs_[0][0] + '_' + self.pairs_[0][1]].isFirstActionPassed() is False:
            self.indicators_[self.pairs_[0][0] + '_' + self.pairs_[0][1]].preprocess()

        # === X === #
        X = self.indicators_[self.pairs_[0][0] + '_' + self.pairs_[0][1]].getIndicators_PP().values

        # for i in range(0, self.indicators_.getIndicators_PP().shape[1], 3):
        #     print(self.indicators_.getIndicators_PP().iloc[:5, i:i+3], flush=True)

        X = np.array([X[i:i + self.LSTMPeriod_].copy() for i in range(self.LSTMPeriod_, X.shape[0] - self.LSTMPeriod_ - self.YPeriod_)])
        # X = np.array([X[i:i + self.period_].copy() for i in range(self.period_, X.shape[0] - self.period_)])

        # === Y === #
        y = self.indicators_[self.pairs_[0][0] + '_' + self.pairs_[0][1]].getIndicators(['evolution_PP']).evolution_PP.values

        y = np.array([y[i + self.LSTMPeriod_:i + self.LSTMPeriod_ + self.YPeriod_].mean() for i in range(self.LSTMPeriod_, y.shape[0] - self.LSTMPeriod_ - self.YPeriod_)])
        # y = np.array([y[i + self.period_] for i in range(self.period_, y.shape[0] - self.period_)])

        # === SHAPE === #
        print("Shape: ", self.LSTMPeriod_, " | ", X.shape, " | ", y.shape, file=sys.stderr)

        # === CREATE MODEL === #
        if self.model_ is None:
            self.createModel(self.LSTMPeriod_, X.shape[2])

        # === FIT MODEL === #
        self.model_.fit(x=X, y=y, batch_size=32, epochs=55, validation_split=0.1)
        print("FIT MODEL", file=sys.stderr)

        # === SAVE MODEL === #
        self.removeTrainedModel()

        self.model_.save(self.dir_)

    def predict(self, wallet):

        # DO NOT PRINT on stdout in this function !

        for p in self.pairs_:
            if self.indicators_[p[0] + '_' + p[1]].isFirstActionPassed() is False:
                self.indicators_[p[0] + '_' + p[1]].preprocess()

        # print(self.indicators_.getIndicators_PP().iloc[:, :5], file=sys.stderr, flush=True)
        # print(self.indicators_.getIndicators_PP().iloc[:, 5:], file=sys.stderr, flush=True)

        y_pred = []

        for p in self.pairs_:
            X = self.indicators_[p[0] + '_' + p[1]].getIndicators_PP().values
            X = np.array(X[X.shape[0] - self.LSTMPeriod_:X.shape[0]].copy())
            y = self.model_.predict(np.array([X]))
            y_pred.append([np.abs(y - 0.5), y, p])

        y_pred.sort(reverse=True)

        for p in y_pred:
            if wallet.isEmpty(buy=True, pair=p[2]) is False and p[1] > 0.5:
                return wallet.buy(pair=p[2], percent=10)
            elif wallet.isEmpty(buy=False, pair=p[2]) is False and p[1] < 0.5:
                return wallet.sell(pair=p[2], percent=25)

        return 'pass\n'
