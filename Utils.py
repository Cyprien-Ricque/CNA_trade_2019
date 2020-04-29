#!/usr/bin/python3.7

import os


# WIP : should be able to pass a file path
def d_print(s, fd_passed=-1):
    if fd_passed == -1:
        fd = os.open("/home/Cyprien/Documents/tek2/CNA/CNA_trade_2019/tmp.txt", os.O_WRONLY | os.O_CREAT)
    else:
        fd = fd_passed
    os.write(fd, s.decode())
    if fd_passed == -1:
        os.close(fd)
