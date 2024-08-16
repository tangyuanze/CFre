# -*- coding: UTF-8 -*-
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from sklearn import preprocessing
import xlrd
import random
from scipy.stats import norm, lognorm, exponweib
from sklearn.metrics import make_scorer


def load_data(xls_path):
    ninput = 0
    noutput = 0
    book = xlrd.open_workbook(xls_path)
    sheet = book.sheet_by_index(0)
    ST = sheet.nrows - 1
    ncol = sheet.ncols - 1
    for i in sheet.row_values(1):
        if i != '':
            ninput += 1
        else:
            noutput = ncol - ninput
            break
    indata = np.zeros((ST, ninput), dtype=np.float_)
    outdata = np.zeros((ST, noutput), dtype=np.float_)
    for j in range(ST):
        data = sheet.row_values(j + 1)
        indata[j] = data[0:ninput]
        outdata[j] = data[ninput + 1:ncol + 1]
    variable = sheet.row_values(0)[0:ninput]
    return indata, outdata, ninput, noutput, variable


def sample_expansion(xls_path, n_sample, CV, distr):
    indata, outdata, ninput, noutput, variable = load_data(xls_path)  # all data used to train
    scaler = preprocessing.MinMaxScaler()
    x_train = scaler.fit_transform(indata)
    def my_loss_func(y_true, y_pred):
        mape = np.mean(np.abs((y_pred - y_true) / y_true))
        return mape
    mape = make_scorer(my_loss_func, greater_is_better=False)
    # 训练SVR#
    sv = GridSearchCV(SVR(tol=0.0001), param_grid={"kernel": ('rbf', 'sigmoid'), "C": np.linspace(1, 64, 40),
                                        "gamma": np.linspace(0.00001, 1, 40)}, cv=5, scoring=mape)  # start,stop,num
    wrapper = MultiOutputRegressor(sv)
    wrapper.fit(x_train, outdata)
    print(wrapper.estimators_[0].best_params_)
    print('MAPE:', -wrapper.estimators_[0].best_score_)

    # MCS抽样#
    X = indata[0]  # 数据第一行为均值
    X1 = np.zeros((n_sample, ninput), dtype=np.float_)
    Y = np.zeros((n_sample, noutput), dtype=np.float_)
    for i in range(n_sample):
        for j in range(ninput):
            l = norm.cdf(X[j] - 3 * CV[j] * X[j], X[j], CV[j] * abs(X[j]))
            h = norm.cdf(X[j] + 3 * CV[j] * X[j], X[j], CV[j] * abs(X[j]))
            if distr[j] == 'LND':
                X1[i, j] = lognorm.ppf((random.uniform(l, h)), 1, loc=X[j], scale=CV[j] * abs(X[j]))
            elif distr[j] == '2WD':
                X1[i, j] = exponweib.ppf((random.uniform(l, h)), 1, 0, loc=X[j], scale=CV[j] * abs(X[j]))
            else:
                X1[i, j] = norm.ppf((random.uniform(l, h)), loc=X[j], scale=CV[j] * abs(X[j]))
    X11 = scaler.fit_transform(X1)

    for j in range(n_sample):
        Y[j] = wrapper.predict(X11[j].reshape(1, -1))
    X1 = X1[(Y > 0).all(1)]
    Y = Y[(Y > 0).all(1)]
    #print('expansion num:', len(Y))

    X_data = np.concatenate((indata, X1), axis=0)  # 未归一化
    Y_data = np.concatenate((outdata, Y), axis=0)
    return X_data, Y_data, ninput, noutput, variable





