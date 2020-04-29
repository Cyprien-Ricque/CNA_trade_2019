#!/usr/bin/python3.7

import pandas as pd


class Strategy:
    def __init__(self):
        self.data = pd.DataFrame()

    def newData(self, data):
        pass

    def train(self):
        pass

    def predict(self):
        return 'pass\n'
