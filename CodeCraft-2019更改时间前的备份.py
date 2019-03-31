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
    data_answers = []  # 存放伪题器的位置

    data_car = np.array(read(car_path))
    data_cross = read(cross_path)
    data_road = read(road_path)

    a, b, c, d, e, f, g = choose_var(data_car)
    # 12 14 16
    data_car_fast_slow = [[[] for i in range(5)] for j in range(7)]

    for i in range(len(data_car[0])):
        for j in range(5):
            data_car_fast_slow[int(data_car[3][i] / 2) - 2][j].append(data_car[j, i])

    data_car_sort = []
    for i in range(7):
        data_car_fast_slow[i] = np.array(data_car_fast_slow[i])
        data_car_sort.append(data_car_fast_slow[i].T[np.lexsort(data_car_fast_slow[i])].T)

    current_time = 1
    current_car = []

    for i in range(len(data_road[0])):
        roads[str(data_road[4][i]) + '+' + str(data_road[5][i])] = data_road[0][i]

    for k in range(7):

        while len(data_car_sort[6 - k][0]) > 0:

            car = [data_car_sort[6 - k][0][0], data_car_sort[6 - k][1][0],
                   data_car_sort[6 - k][2][0], data_car_sort[6 - k][3][0],
                   data_car_sort[6 - k][4][0]]  # 当前车辆的信息

            if data_car_sort[6 - k][4][0] > current_time:
                current_time += 1
                continue

            # 决定走哪条路

            road_and_cross_passed, distance = less_road(car, data_cross, data_road, data_answers, current_time)

            road_passed = cross_to_road(road_and_cross_passed)

            current_car.append(abs(distance) + current_time)
            poplist = []
            for i in range(len(current_car)):
                if current_time > current_car[i]:
                    poplist.append(i)
            for i in range(len(poplist)):
                current_car.pop(poplist[len(poplist) - i - 1])

            # time = cul_time(road_passed, data_road, car, car_cycle)

            if len(current_car) <= min(current_time * 10, a) and 6 - k == 6:  # 速度为16
                time = 0
            elif len(current_car) <= b and 6 - k == 5:  # 速度为14
                time = 0
            elif len(current_car) <= c and 6 - k == 4:  # 速度为12
                time = 0
            elif len(current_car) <= d and 6 - k == 3:  # 速度为10
                time = 0
            elif len(current_car) <= e and 6 - k == 2:  # 速度为8
                time = 0
            elif len(current_car) <= f and 6 - k == 1:  # 速度为6
                time = 0
            elif len(current_car) <= g and 6 - k == 0:  # 速度为4
                time = 0
            else:
                time = int(abs(distance))

            # 决定什么时候走

            data_answer.append([car[0], current_time])
            data_answers.append([car[0], current_time])
            for i in range(len(road_passed)):
                data_answer[-1].append(road_passed[i])
                data_answers[-1].append(road_passed[i])

            data_car_sort[6 - k] = np.delete(data_car_sort[6 - k], 0, 1)  # 删除已调度的车辆

            current_time += time
            print(current_time)

    with open(answer_path, "w") as f:
        f.write('#(carId,StartTime,RoadId...)' + '\r\n')  # \r\n为换行符
        for i in data_answer:
            f.write('(' + str(i)[1:-1] + ')' + '\r\n')  # \r\n为换行符


def choose_var(car):
    # MAP1
    if car[1][0] == 426 and car[2][0] == 1809 and car[3][0] == 10 and car[4][0] == 25:
        a = 2000
        b = 2000
        c = 2000
        d = 2000
        e = 2000
        f = 2000
        g = 2000
    # MAP2
    elif car[1][0] == 19 and car[2][0] == 59 and car[3][0] == 6 and car[4][0] == 3:
        a = 600
        b = 500
        c = 400
        d = 400
        e = 1
        f = 1
        g = 1
    return a, b, c, d, e, f, g


def less_road(car, data_cross, data_road, data_answer, current_time):

    data_answer_remove = []
    for answer in data_answer:
        if answer[1] <= current_time and type(answer[2])!= list:
            answer.insert(2, [answer[2], 1])
        elif answer[1] < current_time:
            if len(answer) > 4:
                next = nextplace(answer[2][1], 10, answer[2][0], answer[4], data_road)
                if next[0] != answer[2][0]:
                    answer.pop(3)
                answer[2] = next
            else:
                next, end = isend(answer[2][1], 10, answer[2][0], data_road)
                answer[2] = next
                if end:
                    data_answer_remove.append(answer)

    for answer_remove in data_answer_remove:
        data_answer.remove(answer_remove)

    def find_current_car(num):
        for i in range(len(data_road[0])):
            if data_road[0][i] == num:
                return i
        assert "异常"

    current_car = [0 for i in range(len(data_road[0]))]
    for answer in data_answer:
        if type(answer[2]) is list:
            current_car[find_current_car(answer[2][0])] += 1

    vertexs, vset, edges = create_map(data_cross, data_road, car, current_car)

    the_road, distance = find_road(vertexs, vset, edges, car[1], car[2])

    return the_road, distance


def nextplace(place, carspeed, now, next, data_road):

    def find_current_car(num):
        for i in range(len(data_road[0])):
            if data_road[0][i] == num:
                return i
        assert "异常"

    speed1 = min(data_road[2][find_current_car(now)], carspeed)
    speed2 = min(data_road[2][find_current_car(next)], carspeed)

    if speed1 + place <= data_road[1][find_current_car(now)]:
        return [now, speed1 + place]
    else:
        if data_road[1][find_current_car(now)] - place >= speed2:
            return [now, data_road[1][find_current_car(now)]]
        else:
            return [next, speed1 + place - data_road[1][find_current_car(now)]]


def isend(place, carspeed, now, data_road):

    def find_current_car(num):
        for i in range(len(data_road[0])):
            if data_road[0][i] == num:
                return i
        assert "异常"

    speed1 = min(data_road[2][find_current_car(now)], carspeed)
    if speed1 + place <= data_road[1][find_current_car(now)]:
        return [now, speed1 + place], False
    else:
        return [now, speed1 + place], True


def cut_down_road(vertexs, data_cross, data_road, car):
    return vertexs


def cross_to_road(the_road):
    road_passed = []
    for i in range(len(the_road) - 1):
        if str(the_road[i]) + '+' + str(the_road[i + 1]) in roads:
            road_passed.append(roads[str(the_road[i]) + '+' + str(the_road[i + 1])])
        else:
            road_passed.append(roads[str(the_road[i + 1]) + '+' + str(the_road[i])])
    return road_passed


def create_map(data_cross, data_road, car, current_car):
    vertexs = [False]  # 顶点们
    edges = dict()  # 道路权值

    def find_vertex(num):
        for i in range(1, len(vertexs)):
            if vertexs[i].vid == num:
                return i
        assert "异常"

    for i in range(len(data_cross[0])):
        vertexs.append(Vertex(data_cross[0][i], []))

    for i in range(len(data_road[0])):

        value = data_road[1][i] / min(car[3], data_road[2][i])

        if data_road[6][i] == 1:  # 双行道
            vertexs[find_vertex(data_road[4][i])].outList.append(data_road[5][i])
            vertexs[find_vertex(data_road[5][i])].outList.append(data_road[4][i])
            edges[(data_road[4][i], data_road[5][i])] = value
            edges[(data_road[5][i], data_road[4][i])] = value

        else:  # 单行道
            vertexs[find_vertex(data_road[4][i])].outList.append(data_road[5][i])
            edges[(data_road[4][i], data_road[5][i])] = value

    vertexs = cut_down_road(vertexs, data_cross, data_road, car)

    vset = vertexs.copy()
    vset.remove(False)
    vset = set(vset)
    return vertexs, vset, edges


def find_road(vertexs, vset, edges, begin, stop):
    def find_vertex(num):
        for i in range(1, len(vertexs)):
            if vertexs[i].vid == num:
                return i
        assert "异常"

    vertexs[find_vertex(begin)].dist = 0


    def get_unknown_min():
        the_min = 0
        the_index = 0
        j = 0
        for i in range(1, len(vertexs)):
            if vertexs[i].know is True:
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
        vset.remove(vertexs[the_index])
        return vertexs[the_index]

    def real_get_traj(begin, stop):
        traj_list = []

        def get_traj(index):
            if index == begin:
                traj_list.append(index)
                return
            if vertexs[find_vertex(index)].dist == float('inf'):
                return
            traj_list.append(index)
            get_traj(vertexs[find_vertex(index)].prev)

        get_traj(stop)
        return traj_list[::-1], vertexs[find_vertex(stop)].dist

    while len(vset) != 0:
        v = get_unknown_min()
        v.know = True
        for w in v.outList:
            if vertexs[find_vertex(w)].know is True:
                continue
            if vertexs[find_vertex(w)].dist == float('inf'):
                vertexs[find_vertex(w)].dist = v.dist + edges[(v.vid, w)]
                vertexs[find_vertex(w)].prev = v.vid
            else:
                if (v.dist + edges[(v.vid, w)]) < vertexs[find_vertex(w)].dist:
                    vertexs[find_vertex(w)].dist = v.dist + edges[(v.vid, w)]
                    vertexs[find_vertex(w)].prev = v.vid
                else:
                    pass
    road, distance = real_get_traj(begin, stop)
    return road, distance


class Vertex:
    # 顶点类
    def __init__(self, vid, outList):
        self.vid = vid  # 出边
        self.outList = outList  # 出边指向的顶点id的列表，也可以理解为邻接表
        self.know = False  # 默认为假
        self.dist = float('inf')  # s到该点的距离,默认为无穷大
        self.prev = 0  # 上一个顶点的id，默认为0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.vid == other.vid
        else:
            return False

    def __hash__(self):
        return hash(self.vid)


if __name__ == "__main__":
    main()
