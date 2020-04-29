#!/usr/bin/python3.7

import os


# WIP : should be able to pass a file path
def d_print(s, fd_passed=-1):
    with open("/home/Cyprien/Documents/tek2/CNA/CNA_trade_2019/tmp.txt", "a") as file:
        file.write(s)
