# -*- coding: UTF-8 -*-
import numpy as np
from scipy.stats import norm, lognorm, exponweib
import random
import sys


def lhs(X, choose, ST, D, C):
    Y = np.zeros((len(X), ST), dtype=np.float_)
    if D != 'CONST':
        for i in range(len(X)):
            if choose[i]:
                l = norm.cdf(X[i] - 3 * C * X[i], X[i], abs(C * X[i]))
                h = norm.cdf(X[i] + 3 * C * X[i], X[i], abs(C * X[i]))
                delta = (h - l) / ST
                for j in range(ST):
                    if D == 'LND':
                        Y[i, j] = lognorm.ppf(l + delta * j + random.random() * delta, 1, X[i], abs(C * X[i]))
                    elif D == '2WD':
                        Y[i, j] = exponweib.ppf(l + delta * j + random.random() * delta, 1, 0.5, X[i], abs(C * X[i]))
                    else:
                        Y[i, j] = norm.ppf(l + delta * j + random.random() * delta, X[i], abs(C * X[i]))
                Y[i, :] = np.random.permutation(Y[i, :])
            else:
                Y[i, :] = X[i]
    else:
        for i in range(len(X)):
            Y[i, :] = X[i]
    Y = np.insert(Y, 0, X, axis=1)
    return Y


# 含温度相关的抽样，保持每个点的数值偏离趋势一致，带入代理模型用每组的最后一个点。
def temp_lhs(mat_data, ST, D, C):
    num_temp = len(mat_data)
    Y = np.zeros((num_temp, ST), dtype=np.float_)
    if D != 'CONST':
        for i in range(num_temp):
            l = norm.cdf(mat_data[i] - 3 * C * mat_data[i], mat_data[i], abs(C * mat_data[i]))
            h = norm.cdf(mat_data[i] + 3 * C * mat_data[i], mat_data[i], abs(C * mat_data[i]))
            delta = (h - l) / ST
            for j in range(ST):
                if D == 'LND':
                    Y[i, j] = lognorm.ppf(l + delta * j + random.random() * delta, 1, mat_data[i], abs(C * mat_data[i]))
                elif D == '2WD':
                    Y[i, j] = exponweib.ppf(l + delta * j + random.random() * delta, 1, 0.5, mat_data[i], abs(C * mat_data[i]))
                else:
                    Y[i, j] = norm.ppf(l + delta * j + random.random() * delta, mat_data[i], abs(C * mat_data[i]))
    else:
        for i in range(num_temp):
            Y[i, :] = mat_data[i]
    Y = np.insert(Y, 0, mat_data, axis=1)
    return Y


def str2list(range_list):
    range_list = range_list.split(',')
    for i in range(len(range_list)):
        range_list[i] = float(range_list[i])
    return range_list

temp = sys.argv[1]
if temp == '0':
    X = sys.argv[2]
    X = str2list(X)

    choose = sys.argv[3]
    choose = str2list(choose)

    ST = int(sys.argv[4])
    D = sys.argv[5]
    C = float(sys.argv[6])
    Y = lhs(X, choose, ST, D, C)
else:
    mat_data = sys.argv[2]
    mat_data = str2list(mat_data)

    ST = int(sys.argv[3])
    D = sys.argv[4]
    C = float(sys.argv[5])
    Y = temp_lhs(mat_data, ST, D, C)
np.save("lhs_data.npy", Y)
