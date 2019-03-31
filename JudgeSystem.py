# encoding = utf-8
"""
@version: 0.1
@author: JackWang
@file: JudgeSystem
@time: 2019/03/25 上午10:41
"""

from ReadInput import *


def read_all(path):
    data_car = read(path + 'car' + '.txt')
    data_cross = read(path + 'cross' + '.txt')
    data_road = read(path + 'road' + '.txt')
    return data_car, data_cross, data_road


def judge():
    map = '1'
    path = 'data/' + map + '/'
    data_car, data_cross, data_road = read_all(path)


# todo(JackWang): complete this code


if __name__ == '__main__':
    judge()
