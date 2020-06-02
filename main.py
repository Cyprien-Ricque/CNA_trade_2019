#!/usr/bin/python3.7

import sys
import os

from src.Trader import Trader


def main():
    trader = Trader()
    while True:
        trader.run()


if __name__ == '__main__':
    main()
    exit(0)
