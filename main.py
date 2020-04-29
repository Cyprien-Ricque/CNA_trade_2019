#!/usr/bin/python3.7

import sys
import os
from Trader import Trader
from Utils import d_print


def main():
    trader = Trader()
    while 1:
        trader.run()


if __name__ == '__main__':
    main()
    exit(0)
