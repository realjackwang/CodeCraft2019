# encoding = utf-8
"""
@version: 0.1
@author: JackWang
@file: ReadInput
@time: 2019/03/25 上午10:48
"""


def read(path):
    data = []
    with open(path) as input_file:
        input_data = input_file.readlines()
        if input_data[0][5] == 'f':
            data = [_id, _from, to, speed, planTime] = [[], [], [], [], []]
        elif input_data[0][5] == 'r':
            data = [_id, roadId, roadId, roadId, roadId] = [[], [], [], [], []]
        elif input_data[0][5] == "l":
            data = [_id, length, speed, channel, _from, to, isDuplex] = [[], [], [], [], [], [], []]

    for eachline in input_data:
        if eachline.startswith("#"):
            continue
        eachline = eachline.strip('\n').strip('()')
        data_t = eachline.split(",")
        for i in range(len(data_t)):
            data[i].append(int(data_t[i]))

    return data
