import time
import numpy as np
import sys
from line_profiler import LineProfiler
from functools import wraps

def func_line_time(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        func_return = f(*args, **kwargs)
        lp = LineProfiler()
        lp_wrap = lp(f)
        lp_wrap(*args, **kwargs)
        lp.print_stats()
        return func_return
    return decorator

# @func_line_time
def get_max_val_indexs(point_value): # 02100
    last_max = False
    len_max = False
    max = 0
    tmp_max = 0
    tmp_index = 0
    max_values = []
    max_indexs = []
    for i in range(len(point_value)-1, -1, -1):
        val = point_value[i]
        if val > max:
            max = val
            if len_max == False:
                tmp_max = val
                tmp_index = i
                last_max = True
                if i == 0:
                    max_indexs.append(i)
                    max_values.insert(0,val)
            else:
                max_indexs.append(i)
                max_values.insert(0,val)
        else:
            if len_max==True:
                max_values.insert(0, 0)
            elif last_max==True:
                max_indexs.append(tmp_index)
                max_values.insert(0, tmp_max)
                len_max = True
                max_values.insert(0, 0)


    for j in range(max_indexs[0]+1, len(point_value)):
        if point_value[j] != 0:
            max_indexs.insert(0,j)
        max_values.append(point_value[j])

    return max_values, max_indexs

# @func_line_time






def get_son_value(max_values, max_indexs, index_):
    son_dict = {}
    indexs_dict = {}
    cluster = {}
    # index_ = len(max_values)
    brother = max_values
    max_indexs.append(-1)
    tmp1 = len(max_indexs)

    # print(2333333, max_values, brother, tmp1, index_, max_indexs)  #  2333333 [4] [4] 2 2 [0, -1]
    if max(max_values) != 1:
        for i in range(tmp1):
            if i == 0:
                brother = [j-1 if j != 0 else 0 for j in brother]
            else:
                brother[max_indexs[i-1]] = brother[max_indexs[i-1]]+1


            # 能不能加一个逻辑条件 避免全部都计算一次最大值
            max_values_, max_indexs_ = get_max_val_indexs(brother)
            # print(244444, brother, max_values_, max_indexs_)
            son_dict[tuple(max_values_)] = [ix for ix in range(max_indexs[i]+1, index_)]
            indexs_dict[tuple(max_values_)] = max_indexs_
            index_ = max_indexs[i]+1

            # if max_values[max_indexs[i]] == max_values[0]:
            #     break

    else:

        # print(2333, max_values, max_indexs, index_, range(max_indexs[0], index_)) # 2333 (0, 0, 1, 0, 0) [2, -1] 6    345
        son_dict['ONE'] = [ix for ix in range(max_indexs[0]+1, index_)]
        # if max_values[0] > 1:
        #     max_values[0] = max_values[0]-1
        #     max_values_, max_indexs_ = get_max_val_indexs(brother)
        #     # print(2333, brother, max_indexs, max_values_, max_indexs_)
        #     son_dict[tuple(max_values_)] = [ix for ix in range(0, max_indexs[-1]+1)]
        #     indexs_dict[tuple(max_values_)] = max_indexs_
            # cluster[tuple(max_values_[1:])]

    cluster[tuple(max_values)] = son_dict
    return cluster, indexs_dict


def generate_grap_by_cluster(layer, max_values, cluster):
    grap = {}
    tmp_son_max = max(max_values)
    for i in range(layer, 0, -1):
        father = (i,) + tuple(max_values)
        tmp_grap = {}

        if i == tmp_son_max:
            if i != 1:
                # print('当前节点值和剩余位最大值相同，涉及图结构变化，移除第一条边，且此簇递归结束', i, tmp_son_max)
                first_root = list(cluster[tuple(max_values)].keys())[-1]
                for key, value in cluster[tuple(max_values)].items():
                    if key != first_root:
                        tmp_point = (i-1,) + key
                        tmp_grap[tmp_point] = value
                grap[father] = tmp_grap
                break
            else:
                grap[father] = cluster[tuple(max_values)]
                break

        else:
            # print(233, father, cluster)
            for key, value in cluster[tuple(max_values)].items():
                # print(2333, cluster[tuple(max_values)])
                if key != 'ONE':
                    tmp_point = (i - 1,) + key
                    tmp_grap[tmp_point] = value
                else:
                    tmp_grap = cluster[tuple(max_values)].copy()

            grap[father] = tmp_grap

            if tmp_son_max == 1:
                # 对此类特殊的补边
                tmp_point = (i - 1,) +tuple(max_values)
                tmp_grap[tmp_point] = [i for i in range(0, min(min(cluster[tuple(max_values)].values())))]
                grap[father] = tmp_grap

    return grap



def cal_singel_grap(point_value):

    pending_point = {}
    processed_point = ['ONE']
    indexs_dict_all = {}
    grap_all = {}

    index_ = len(point_value)
    layer = point_value[0]
    point_value = point_value[1:]

    max_values, max_indexs = get_max_val_indexs(point_value)
    cluster, indexs_dict = get_son_value(max_values, max_indexs, index_)
    processed_point.append(tuple(max_values))
    indexs_dict_all.update(indexs_dict)
    # 将簇的子图添加到待计算列表中
    new_point = list(cluster[tuple(max_values)].keys())
    pending_point[layer-1] = new_point
    # 先计算一个节点的最大值和对应的簇结构，默认所有节点都需要计算簇结构，然后再填充节点的实际子数据

    grap = generate_grap_by_cluster(layer, max_values, cluster)
    # print('根据相似图簇生成子图：', grap)
    grap_all.update(grap)

    # 临时通过是否处理过来判断新节点是否需要处理，规律上发现，最后一个不用处理


    while len(pending_point)>0:
        # 获取当前层的层数，以及当前层的待计算节点
        layer = list(pending_point.keys())[0]
        pending_point_layer = pending_point[layer]
        pending_point = {}
        # print('当前层数:', layer)
        new_point = []
        while len(pending_point_layer)>0:
            point_value = pending_point_layer[-1]
            pending_point_layer.pop()

            if point_value in processed_point:
                continue
            else:
                processed_point.append(tuple(point_value))
                max_indexs = indexs_dict_all[point_value]
                # print('-------------开始递归计算新节点:', layer, point_value)

                cluster, indexs_dict = get_son_value(point_value, max_indexs, index_)

                indexs_dict_all.update(indexs_dict)
                new_point_ = list(cluster[tuple(point_value)].keys())
                new_point += new_point_
                # print('new_point:', new_point)
                # print('cluster:', cluster)
                grap = generate_grap_by_cluster(layer, point_value, cluster)
                # print('根据相似图簇生成子图：', grap)
                grap_all.update(grap)

                pending_point[layer-1] = new_point


        # print('查看下一层节点：', len(new_point), new_point)
        # print('查看已处理节点：', len(processed_point), processed_point)
        # print('查看已生成节点数：', len(grap_all), grap_all)

    # print('查看已处理节点：', len(processed_point), processed_point)
    # print('查看已生成节点数：', len(grap_all))
    # print(grap_all)


    return grap_all


def compute_node_pr(node, MDD, Pr_MDD):
    if node in Pr_MDD:
        return Pr_MDD[node]
    else:
        childs = MDD[node]
        node_pr = 0
        comp = node[0] - 1
        for child_key in childs:
            child_value = childs[child_key]
            node_edge = 0
            for edge in child_value:
                node_edge += P[comp][edge]
            if child_key == "ONE":
                Pr_MDD[node] = node_edge
                node_pr += node_edge
            else:
                node_pr += node_edge * compute_node_pr(child_key, MDD, Pr_MDD)
        Pr_MDD[node] = node_pr
        return node_pr

grap = []
input = [100,15,10,5]
n = input[0]
M = len(input)-1

start = time.perf_counter()

tmp1 = len(input)
for i in range(tmp1,1,-1):
    point_value = input[:i]
    grap_all = cal_singel_grap(point_value)
    grap.append(grap_all)
end = time.perf_counter()

print('construct_time = ','%.4f'%((end-start)*1000),'ms')
# print(grap)
P = []
for i in range(n):
    component = np.random.dirichlet(np.ones(M + 1), size=1)
    component = np.around(component, M + 1).tolist()
    component = component[0]
    component = component

    P.append(component)
start_ = time.perf_counter()
j = M
for i in range(0,M):
    Pr_node = {}
    for k in range(n):
        if j < M:
            P[k][j] += P[k][j + 1]
    j -= 1
    root = list(grap[i].keys())
    Pr = compute_node_pr(root[0], grap[i], Pr_node)
end_ = time.perf_counter()
print('evaluate_time = ','%.4f'%((end_ - start_)*1000),'ms')


