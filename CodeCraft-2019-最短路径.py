import logging
import sys
import numpy as np
from ReadInput import *
import copy
import Dijkstra as ds

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

    data_car_sort = data_car.T[np.lexsort(data_car)].T

    # [_id, _from, to, speed, planTime]
    # [_id, roadId, roadId, roadId, roadId]
    # [_id, length, speed, channel, _from, to, isDuplex]

    # map_info_c = create_map(data_cross, data_road)[1]

    current_time = 1
    car_cycle = 128 # 每个周期街道上的总车辆（可以理解为这样，但是因为种种原因并不是实时的总车辆）（这里可以调参）

    for i in range(len(data_road[0])):
        roads[str(data_road[4][i]) + '+' + str(data_road[5][i])] = data_road[0][i]

    while len(data_car_sort[0]) > 0:

        car = [data_car_sort[0][0], data_car_sort[1][0], data_car_sort[2][0], data_car_sort[3][0],
               data_car_sort[4][0]]  # 当前车辆的信息

        road_and_cross_passed = less_road(car, data_cross, data_road)

        road_passed = cross_to_road(road_and_cross_passed)

        time = cul_time(road_passed, data_road, car, car_cycle)
        if car_cycle < 0:
            car_cycle = 128
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
    start = [2 * (int((car[1] - 1) / np.sqrt(len(data_cross[0])))) + 1,
             2 * (int((car[1] - 1) % np.sqrt(len(data_cross[0])))) + 1]

    end = [2 * (int((car[2] - 1) / np.sqrt(len(data_cross[0])))) + 1,
           2 * (int((car[2] - 1) % np.sqrt(len(data_cross[0])))) + 1]

    # # data_cross[start]
    #
    # location = start
    # cross_history = [start]  # 记录走过的点
    # map_info_1 = create_map(data_cross, data_road)[0]

    vertexs, vset, edges = create_map2(data_cross, data_road, car)

    the_road = find_road2(vertexs, vset, edges, car[1], car[2])

    # the_road = find_road(map_info_1, start, end)

    return the_road


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
        return traj_list[::-1]

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
    road = real_get_traj(begin, stop)
    return road

#
# def create_map(data_cross, data_road):
#     # *不通
#     # ↕ ↔ ← → ↑ ↓
#     n = 2 * int(np.sqrt(len(data_cross[0]))) + 1
#     map_info = [(['*'] * n) for i in range(n)]
#     for i in range(n):
#         for j in range(n):
#             if i == 0 or i == n - 1 or j == 0 or j == n - 1:  # 迷宫周围设障碍
#                 map_info[i][j] = "*"
#             if i % 2 == 0 and j % 2 == 0:
#                 map_info[i][j] = "*"
#             if i % 2 != 0 and j % 2 != 0:
#                 map_info[i][j] = "+"
#
#     map_info_copy = copy.deepcopy(map_info)
#     for i in range(len(data_road[0])):
#         start = [2 * (int((data_road[4][i] - 1) / np.sqrt(len(data_cross[0])))) + 1,
#                  2 * (int((data_road[4][i] - 1) % np.sqrt(len(data_cross[0])))) + 1]
#         end = [2 * (int((data_road[5][i] - 1) / np.sqrt(len(data_cross[0])))) + 1,
#                2 * (int((data_road[5][i] - 1) % np.sqrt(len(data_cross[0])))) + 1]
#         index = [int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2)]
#
#         map_info[index[0]][index[1]] = '0'
#         map_info_copy[index[0]][index[1]] = data_road[0][i]
#
#         if data_road[6][i] == 0:
#             if index[0] % 2 != 0:
#                 map_info[index[0]][index[1]] = '3'
#             else:
#                 map_info[index[0]][index[1]] = '4'
#
#     # for i in range(len(map_info)):
#     #     for j in range(len(map_info[i])):
#     #         print(map_info[i][j], " ", end="")
#     #     print("")
#
#     return map_info, map_info_copy
#
#
# def find_road(maze, begin, stop):
#     road = []  # 将road作为栈,road[-1]代表栈顶
#     old_road = []
#     road.append(begin)  # 将起点入栈
#     old_road.append(begin)
#     global last_node_tag
#     last_node_tag = 0
#     while road != []:
#         if road[-1] == stop:
#             return road
#         tag = 1  # 判断标识
#
#         while tag != 5:
#             next_node = []
#             if road[-1][0] >= stop[0] and road[-1][1] >= stop[1]:
#                 next_node = next_node1(maze, road, tag)  # 寻找下一个点
#             elif road[-1][0] >= stop[0] and road[-1][1] <= stop[1]:
#                 next_node = nextNode2(maze, road, tag)  # 寻找下一个点
#             elif road[-1][0] <= stop[0] and road[-1][1] >= stop[1]:
#                 next_node = nextNode3(maze, road, tag)  # 寻找下一个点
#             elif road[-1][0] <= stop[0] and road[-1][1] <= stop[1]:
#                 next_node = nextNode4(maze, road, tag)  # 寻找下一个点
#
#             if next_node == None or is_old(next_node, old_road) == 0:  # 若下一点走过了或要碰壁了尝试别的方向
#                 tag += 1
#             else:
#                 road.append(next_node)
#                 old_road.append(next_node)
#                 tag = 1
#                 break
#         if tag == 5:  # 若路都不通，栈顶元素抛出
#             a = road[-1][0]
#             b = road[-1][1]
#             maze[a][b] = "*"
#             road.pop(-1)
#
#     return road
#
#
# def is_old(next_node, oldlist):  # 判断该点是否走过（改进版 ）
#     for i in range(len(oldlist)):
#         if next_node == oldlist[i]:
#             return 0
#     return 1
#
#
# def next_node1(maze, road, i):
#     global last_node_tag
#     if i == 1:
#         a = road[-1][0]  # 往左走的坐标
#         b = road[-1][1] - 1
#         if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
#             last_node_tag = 1
#             return [a, b]
#         return None
#     if i == 2:
#         a = road[-1][0] - 1  # 往上走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
#             last_node_tag = 2
#             return [a, b]
#         return None
#     if i == 3:
#         a = road[-1][0]  # 往右走的坐标
#         b = road[-1][1] + 1
#         if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
#             last_node_tag = 3
#             return [a, b]
#         return None
#     if i == 4:
#         a = road[-1][0] + 1  # 往下走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
#             last_node_tag = 4
#             return [a, b]
#         return None
#
#
# def nextNode2(maze, road, i):
#     global last_node_tag
#     if i == 1:
#         a = road[-1][0] - 1  # 往上走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
#             last_node_tag = 2
#             return [a, b]
#         return None
#     if i == 2:
#         a = road[-1][0]  # 往右走的坐标
#         b = road[-1][1] + 1
#         if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
#             last_node_tag = 3
#             return [a, b]
#         return None
#     if i == 3:
#         a = road[-1][0] + 1  # 往下走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
#             last_node_tag = 4
#             return [a, b]
#         return None
#     if i == 4:
#         a = road[-1][0]  # 往左走的坐标
#         b = road[-1][1] - 1
#         if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
#             last_node_tag = 1
#             return [a, b]
#         return None
#
#
# def nextNode3(maze, road, i):
#     global last_node_tag
#     if i == 1:
#         a = road[-1][0]  # 往左走的坐标
#         b = road[-1][1] - 1
#         if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
#             last_node_tag = 1
#             return [a, b]
#         return None
#     if i == 2:
#         a = road[-1][0] + 1  # 往下走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
#             last_node_tag = 4
#             return [a, b]
#         return None
#     if i == 3:
#         a = road[-1][0]  # 往右走的坐标
#         b = road[-1][1] + 1
#         if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
#             last_node_tag = 3
#             return [a, b]
#         return None
#     if i == 4:
#         a = road[-1][0] - 1  # 往上走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
#             last_node_tag = 2
#             return [a, b]
#         return None
#
#
# def nextNode4(maze, road, i):
#     global last_node_tag
#     if i == 1:
#         a = road[-1][0]  # 往右走的坐标
#         b = road[-1][1] + 1
#         if maze[a][b] != "*" and maze[a][b] != "1" and last_node_tag != 1:
#             last_node_tag = 3
#             return [a, b]
#         return None
#     if i == 2:
#         a = road[-1][0] + 1  # 往下走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "2" and last_node_tag != 2:
#             last_node_tag = 4
#             return [a, b]
#         return None
#     if i == 3:
#         a = road[-1][0]  # 往左走的坐标
#         b = road[-1][1] - 1
#         if maze[a][b] != "*" and maze[a][b] != "3" and last_node_tag != 3:
#             last_node_tag = 1
#             return [a, b]
#         return None
#     if i == 4:
#         a = road[-1][0] - 1  # 往上走的坐标
#         b = road[-1][1]
#         if maze[a][b] != "*" and maze[a][b] != "4" and last_node_tag != 4:
#             last_node_tag = 2
#             return [a, b]
#         return None


if __name__ == "__main__":
    main()
