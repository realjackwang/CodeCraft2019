import logging
import sys
import numpy as np
from ReadInput import *
import copy

logging.basicConfig(level=logging.DEBUG,
                    filename='CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


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

    data_car_sort = data_car.T[np.lexsort(data_car)].T

    # [_id, _from, to, speed, planTime]
    # [_id, roadId, roadId, roadId, roadId]
    # [_id, length, speed, channel, _from, to, isDuplex]
    map_info_c = create_map(data_cross, data_road)[1]
    current_time = 1
    car_cycle = 125
    while len(data_car_sort[0]) > 0:

        car = [data_car_sort[0][0], data_car_sort[1][0], data_car_sort[2][0], data_car_sort[3][0],
               data_car_sort[4][0]]  # 当前车辆的信息

        road_and_cross_passed = less_road(car, data_cross, data_road)
        road_passed = []
        for road in road_and_cross_passed:
            if not (road[0] % 2 != 0 and road[1] % 2 != 0):
                road_passed.append(map_info_c[road[0]][road[1]])
                # if road[0] % 2 == 0:
                #     road_passed.append(int((road[0] / 2) * 15 - 8 + (road[1] - 1) / 2) + 5000)
                # else:
                #     road_passed.append(int(((road[0] - 1) / 2) * 15 + (road[1]) / 2) + 4999)

        time = cul_time(road_passed, data_road, car, car_cycle)
        if car_cycle < 0:
            car_cycle = 125
        car_cycle -= 1

        data_answer.append([car[0], current_time])
        for i in range(len(road_passed)):
            data_answer[-1].append(road_passed[i])

        data_car_sort = np.delete(data_car_sort, 0, 1)  # 删除已调度的车辆
        current_time += time
        print(current_time)

    with open(answer_path, "w") as f:
        f.write('#(carId,StartTime,RoadId...)' + '\r\n')  # \r\n为换行符
        for i in data_answer:
            f.write('(' + str(i)[1:-1] + ')' + '\r\n')  # \r\n为换行符


def cul_time(road_passed, data_road, car, car_cycle):
    if car_cycle == 0:
        time = 10
    else:
        time = 0

    return time


def less_road(car, data_cross, data_road):
    road_passed = []  # 当前车辆的行驶路线
    start = [2 * (int((car[1] - 1) / np.sqrt(len(data_cross[0])))) + 1,
             2 * (int((car[1] - 1) % np.sqrt(len(data_cross[0])))) + 1]

    end = [2 * (int((car[2] - 1) / np.sqrt(len(data_cross[0])))) + 1,
           2 * (int((car[2] - 1) % np.sqrt(len(data_cross[0])))) + 1]

    # data_cross[start]

    location = start
    cross_history = [start]  # 记录走过的点
    map_info_1 = create_map(data_cross, data_road)[0]
    the_road = find_road(map_info_1, start, end)

    return the_road


def create_map(data_cross, data_road):
    # *不通
    # ↕ ↔ ← → ↑ ↓
    n = 2 * int(np.sqrt(len(data_cross[0]))) + 1
    map_info = [(['*'] * n) for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i == 0 or i == n - 1 or j == 0 or j == n - 1:  # 迷宫周围设障碍
                map_info[i][j] = "*"
            if i % 2 == 0 and j % 2 == 0:
                map_info[i][j] = "*"
            if i % 2 != 0 and j % 2 != 0:
                map_info[i][j] = "+"

    map_info_copy = copy.deepcopy(map_info)
    for i in range(len(data_road[0])):
        start = [2 * (int((data_road[4][i] - 1) / np.sqrt(len(data_cross[0])))) + 1,
                 2 * (int((data_road[4][i] - 1) % np.sqrt(len(data_cross[0])))) + 1]
        end = [2 * (int((data_road[5][i] - 1) / np.sqrt(len(data_cross[0])))) + 1,
               2 * (int((data_road[5][i] - 1) % np.sqrt(len(data_cross[0])))) + 1]
        index = [int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2)]

        map_info[index[0]][index[1]] = '0'
        map_info_copy[index[0]][index[1]] = data_road[0][i]

        if data_road[6][i] == 0:
            if index[0] % 2 != 0:
                map_info[index[0]][index[1]] = '3'
            else:
                map_info[index[0]][index[1]] = '4'

    # for i in range(len(map_info)):
    #     for j in range(len(map_info[i])):
    #         print(map_info[i][j], " ", end="")
    #     print("")

    return map_info, map_info_copy


def find_road(maze, begin, stop):
    road = []  # 将road作为栈,road[-1]代表栈顶
    old_road = []
    road.append(begin)  # 将起点入栈
    old_road.append(begin)
    global last_node_tag
    last_node_tag = 0
    while road != []:
        if road[-1] == stop:
            return road
        tag = 1  # 判断标识

        while tag != 5:
            next_node = []
            if road[-1][0] >= stop[0] and road[-1][1] >= stop[1]:
                next_node = next_node1(maze, road, tag)  # 寻找下一个点
            elif road[-1][0] >= stop[0] and road[-1][1] <= stop[1]:
                next_node = nextNode2(maze, road, tag)  # 寻找下一个点
            elif road[-1][0] <= stop[0] and road[-1][1] >= stop[1]:
                next_node = nextNode3(maze, road, tag)  # 寻找下一个点
            elif road[-1][0] <= stop[0] and road[-1][1] <= stop[1]:
                next_node = nextNode4(maze, road, tag)  # 寻找下一个点

            if next_node == None or is_old(next_node, old_road) == 0:  # 若下一点走过了或要碰壁了尝试别的方向
                tag += 1
            else:
                road.append(next_node)
                old_road.append(next_node)
                tag = 1
                break
        if tag == 5:  # 若路都不通，栈顶元素抛出
            a = road[-1][0]
            b = road[-1][1]
            maze[a][b] = "*"
            road.pop(-1)

    return road


def is_old(next_node, oldlist):  # 判断该点是否走过（改进版 ）
    for i in range(len(oldlist)):
        if next_node == oldlist[i]:
            return 0
    return 1




def next_node1(maze, road, i):
    global last_node_tag
    if i == 1:
        a = road[-1][0]  # 往左走的坐标
        b = road[-1][1] - 1
        if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
            last_node_tag = 1
            return [a, b]
        return None
    if i == 2:
        a = road[-1][0] - 1  # 往上走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
            last_node_tag = 2
            return [a, b]
        return None
    if i == 3:
        a = road[-1][0]  # 往右走的坐标
        b = road[-1][1] + 1
        if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
            last_node_tag = 3
            return [a, b]
        return None
    if i == 4:
        a = road[-1][0] + 1  # 往下走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
            last_node_tag = 4
            return [a, b]
        return None


def nextNode2(maze, road, i):
    global last_node_tag
    if i == 1:
        a = road[-1][0] - 1  # 往上走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
            last_node_tag = 2
            return [a, b]
        return None
    if i == 2:
        a = road[-1][0]  # 往右走的坐标
        b = road[-1][1] + 1
        if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
            last_node_tag = 3
            return [a, b]
        return None
    if i == 3:
        a = road[-1][0] + 1  # 往下走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
            last_node_tag = 4
            return [a, b]
        return None
    if i == 4:
        a = road[-1][0]  # 往左走的坐标
        b = road[-1][1] - 1
        if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
            last_node_tag = 1
            return [a, b]
        return None


def nextNode3(maze, road, i):
    global last_node_tag
    if i == 1:
        a = road[-1][0]  # 往左走的坐标
        b = road[-1][1] - 1
        if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
            last_node_tag = 1
            return [a, b]
        return None
    if i == 2:
        a = road[-1][0] + 1  # 往下走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
            last_node_tag = 4
            return [a, b]
        return None
    if i == 3:
        a = road[-1][0]  # 往右走的坐标
        b = road[-1][1] + 1
        if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
            last_node_tag = 3
            return [a, b]
        return None
    if i == 4:
        a = road[-1][0] - 1  # 往上走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
            last_node_tag = 2
            return [a, b]
        return None


def nextNode4(maze, road, i):
    global last_node_tag
    if i == 1:
        a = road[-1][0]  # 往右走的坐标
        b = road[-1][1] + 1
        if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
            last_node_tag = 3
            return [a, b]
        return None
    if i == 2:
        a = road[-1][0] + 1  # 往下走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
            last_node_tag = 4
            return [a, b]
        return None
    if i == 3:
        a = road[-1][0]  # 往左走的坐标
        b = road[-1][1] - 1
        if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
            last_node_tag = 1
            return [a, b]
        return None
    if i == 4:
        a = road[-1][0] - 1  # 往上走的坐标
        b = road[-1][1]
        if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
            last_node_tag = 2
            return [a, b]
        return None


if __name__ == "__main__":
    main()
