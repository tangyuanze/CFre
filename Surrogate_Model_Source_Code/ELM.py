# -*- coding: UTF-8 -*-
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import data
import Draw
from sklearn import preprocessing
import warnings
warnings.filterwarnings("ignore")


class ELM():  # 快，精度一般
    def __init__(self, input_nums, hidden_nums, output_nums):
        self.input_nums = input_nums
        self.hidden_nums = hidden_nums
        self.output_nums = output_nums
        self.is_inited = False
        # 隐层权重矩阵
        self.W = np.array([[np.random.uniform(-1, 1) for _ in range(self.hidden_nums)] for i in range(self.input_nums)])
        # 隐层偏置项
        self.bias = np.array([np.random.uniform(-1, 1) for _ in range(self.hidden_nums)])
        # 输出层权重
        self.beta = np.zeros(shape=[self.hidden_nums, self.output_nums])
        # (H^{T}H)^{-1}
        self.P = np.zeros(shape=[self.hidden_nums, self.hidden_nums])

    def predict(self, x):
        return np.dot(self.activation(np.dot(x, self.W) + self.bias), self.beta)

    def init_train(self, x, target):
        # output matrix
        H = self.activation(np.dot(x, self.W) + self.bias)
        HT = np.transpose(H)
        HTH = np.dot(HT, H)
        self.P = np.linalg.inv(HTH)
        pHT = np.dot(self.P, HT)
        self.beta = np.dot(pHT, target)
        self.is_inited = True

    def seq_train(self, x, target):
        batch_size = x.shape[0]
        H = self.activation(np.dot(x, self.W) + self.bias)
        HT = np.transpose(H)
        I = np.eye(batch_size)
        Hp = np.dot(H, self.P)
        HpHT = np.dot(Hp, HT)
        temp = np.linalg.inv(I + HpHT)
        pHT = np.dot(self.P, HT)
        self.P -= np.dot(np.dot(pHT, temp), Hp)
        pHT = np.dot(self.P, HT)
        Hbeta = np.dot(H, self.beta)
        self.beta += np.dot(pHT, target - Hbeta)

    def activation(self, x):
        return 1 / (1 + np.exp(-x))


def elm(xlsname, num, CV, distr, fig, sensi):
    # 数据集
    if num == 0:
        indata, outdata, ninput, noutput, variable = data.load_data(xlsname)
    else:
        indata, outdata, ninput, noutput, variable = data.sample_expansion(xlsname, num, CV, distr)
    print('ELM BEGIN')
    scaler = preprocessing.MinMaxScaler()
    x = scaler.fit_transform(indata)
    train_X, test_X, train_Y, test_Y = train_test_split(x, outdata, test_size=0.2)
    # ELM训练
    oselm = ELM(input_nums=ninput, hidden_nums=128, output_nums=noutput)
    oselm.init_train(train_X, train_Y)

    # OS-ELM测试
    prediction_list = []
    for X, Y in zip(test_X, test_Y):
        prediction = oselm.predict(X)
        prediction_list.append(prediction)
        oselm.seq_train(X[np.newaxis, :], Y)  # 在线ELM,来一个测试数据，更新一次
    prediction_arr = np.reshape(np.array(prediction_list), newshape=(-1, noutput))
    # joblib.dump(oselm, 'elm.pkl')

    R2 = r2_score(test_Y, prediction_arr)
    n = len(outdata)  # 样本总数
    p = noutput  # 输出维数
    Adjust_R2 = 1 - (1 - R2) * (n - 1) / (n - p - 1)
    print("Adjust_R2: ", Adjust_R2)
    MAPE = np.mean(np.abs((prediction_arr - test_Y) / test_Y))
    print("MAPE: ", MAPE)

    Draw.draw(indata[0], outdata[0], oselm, variable, CV, distr, fig, sensi, xlsname)

