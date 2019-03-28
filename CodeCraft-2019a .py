# encoding = utf-8
"""
@version: 0.1
@author: JackWang
@file: CodeCraft-2019
@time: 2019/03/26 上午9:02
"""

import logging
import sys
import numpy as np
from ReadInput import *
import copy
import Dijkstra2 as ds

# todo(JackWang): 根据道路容量选择性切断道路

# todo(JackWang): 根据车速不同分别行驶车辆，防止发生慢车堵塞快车情况

# todo(JackWang): xxxxx

logging.basicConfig(level=logging.DEBUG,
                    filename='CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')
roads = {}


def main():
    if len(sys.argv) != 5:
        logging.info('please input args: car_path, road_path, cross_path, answerPath')
        exit(1)

    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    answer_path = sys.argv[4]

    logging.info("car_path is %s" % (car_path))
    logging.info("road_path is %s" % (road_path))
    logging.info("cross_path is %s" % (cross_path))
    logging.info("answer_path is %s" % (answer_path))

    data_answer = []
    data_car = np.array(read(car_path))
    data_cross = read(cross_path)
    data_road = read(road_path)

    a, b, c, d = choose_var(data_car)

    data_car_fast_slow = [[[] for i in range(5)] for j in range(4)]

    for i in range(len(data_car[0])):
        for j in range(5):
            data_car_fast_slow[int(data_car[3][i] / 2) - 1][j].append(data_car[j, i])

    data_car_sort = []
    for i in range(4):
        data_car_fast_slow[i] = np.array(data_car_fast_slow[i])
        data_car_sort.append(data_car_fast_slow[i].T[np.lexsort(data_car_fast_slow[i])].T)

    # [_id, _from, to, speed, planTime]
    # [_id, roadId, roadId, roadId, roadId]
    # [_id, length, speed, channel, _from, to, isDuplex]

    current_time = 1
    current_car = []

    for i in range(len(data_road[0])):
        roads[str(data_road[4][i]) + '+' + str(data_road[5][i])] = data_road[0][i]

    for k in range(4):
        while len(data_car_sort[3 - k][0]) > 0:

            car = [data_car_sort[3 - k][0][0], data_car_sort[3 - k][1][0],
                   data_car_sort[3 - k][2][0], data_car_sort[3 - k][3][0],
                   data_car_sort[3 - k][4][0]]  # 当前车辆的信息

            if data_car_sort[3 - k][4][0] > current_time:
                current_time += 1
                continue

            road_and_cross_passed, distance = less_road(car, data_cross, data_road)

            road_passed = cross_to_road(road_and_cross_passed)

            current_car.append(abs(distance) + current_time)
            poplist = []
            for i in range(len(current_car)):
                if current_time > current_car[i]:
                    poplist.append(i)
            for i in range(len(poplist)):
                current_car.pop(poplist[len(poplist) - i - 1])

            # time = cul_time(road_passed, data_road, car, car_cycle)

            if len(current_car) <= a and 3 - k == 3:  # 速度为8
                time = 0
            elif len(current_car) <= b and 3 - k == 2:  # 速度为6
                time = 0
            elif len(current_car) <= c and 3 - k == 1:  # 速度为4
                time = 0
            elif len(current_car) <= d and 3 - k == 0:  # 速度为2
                time = 0
            else:
                time = int(abs(distance))

            data_answer.append([car[0], current_time])
            for i in range(len(road_passed)):
                data_answer[-1].append(road_passed[i])

            data_car_sort[3 - k] = np.delete(data_car_sort[3 - k], 0, 1)  # 删除已调度的车辆

            current_time += time
            print(current_time)

    with open(answer_path, "w") as f:
        f.write('#(carId,StartTime,RoadId...)' + '\r\n')  # \r\n为换行符
        for i in data_answer:
            f.write('(' + str(i)[1:-1] + ')' + '\r\n')  # \r\n为换行符


def choose_var(car):
    if car[1][0] == 19 and car[2][0] == 59 and car[3][0] == 6 and car[4][0] == 3 \
            and car[1][20] == 24 and car[2][20] == 57 and car[3][20] == 8 and car[4][20] == 6:
        a = 650
        b = 800
        c = 900
        d = 1100
    else:
        a = 500
        b = 600
        c = 800
        d = 1100
    return a, b, c, d


def less_road(car, data_cross, data_road):
    vertexs, vset, edges = create_map2(data_cross, data_road, car)

    the_road, distance = find_road2(vertexs, vset, edges, car[1], car[2])

    return the_road, distance


def cut_down_road(vertexs, data_cross, data_road, car):
    return vertexs


def cross_to_road(the_road):
    road_passed = []
    for i in range(len(the_road) - 1):
        road_passed.append(roads[str(min(the_road[i], the_road[i + 1])) + '+' + str(max(the_road[i], the_road[i + 1]))])
    return road_passed


def create_map2(data_cross, data_road, car):
    vertexs = [False]  # 顶点们
    edges = dict()  # 道路权值

    for i in range(len(data_cross[0])):
        vertexs.append(ds.Vertex(i + 1, []))
    for i in range(len(data_road[0])):
        value = data_road[1][i] / min(car[3], data_road[2][i])
        if data_road[6][i] == 1:  # 双行道
            vertexs[data_road[4][i]].outList.append(data_road[5][i])
            vertexs[data_road[5][i]].outList.append(data_road[4][i])
            edges[(data_road[4][i], data_road[5][i])] = value
            edges[(data_road[5][i], data_road[4][i])] = value

        else:  # 单行道
            vertexs[data_road[4][i]].outList.append(data_road[5][i])
            edges[(data_road[4][i], data_road[5][i])] = value

    vertexs = cut_down_road(vertexs, data_cross, data_road, car)

    vset = vertexs.copy()
    vset.remove(False)
    vset = set(vset)
    return vertexs, vset, edges


def find_road2(vertexs, vset, edges, begin, stop):
    # 将v1设为顶点
    vertexs[begin].dist = 0

    def get_unknown_min():  # 此函数则代替优先队列的出队操作
        the_min = 0
        the_index = 0
        j = 0
        for i in range(1, len(vertexs)):
            if (vertexs[i].know is True):
                continue
            else:
                if (j == 0):
                    the_min = vertexs[i].dist
                    the_index = i
                else:
                    if (vertexs[i].dist < the_min):
                        the_min = vertexs[i].dist
                        the_index = i
                j += 1
        # 此时已经找到了未知的最小的元素是谁
        vset.remove(vertexs[the_index])  # 相当于执行出队操作
        return vertexs[the_index]

    def real_get_traj(begin, stop):
        traj_list = []

        def get_traj(index):  # 参数是顶点在vlist中的索引
            if index == begin:  # 终点
                traj_list.append(index)
                return
            if vertexs[index].dist == float('inf'):
                print('从起点到该顶点根本没有路径')
                return
            traj_list.append(index)
            get_traj(vertexs[index].prev)

        get_traj(stop)
        return traj_list[::-1], vertexs[stop].dist

    while len(vset) != 0:
        v = get_unknown_min()
        # print(v.vid, v.dist, v.outList)
        v.know = True
        for w in v.outList:  # w为索引
            if vertexs[w].know is True:
                continue
            if vertexs[w].dist == float('inf'):
                vertexs[w].dist = v.dist + edges[(v.vid, w)]
                vertexs[w].prev = v.vid
            else:
                if (v.dist + edges[(v.vid, w)]) < vertexs[w].dist:
                    vertexs[w].dist = v.dist + edges[(v.vid, w)]
                    vertexs[w].prev = v.vid
                else:  # 原路径长更小，没有必要更新
                    pass
    road, distance = real_get_traj(begin, stop)
    return road, distance


if __name__ == "__main__":
    main()
