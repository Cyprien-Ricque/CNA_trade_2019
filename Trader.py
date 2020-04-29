#!/usr/bin/python3.7

from Parser import Parser
from Strategy import Strategy


class Trader:
    def __init__(self):
        self._parser = Parser(1000)
        self._strategy = Strategy()

    def run(self):
        pass