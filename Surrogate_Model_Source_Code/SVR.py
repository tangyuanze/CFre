# -*- coding: UTF-8 -*-
import warnings
warnings.filterwarnings("ignore")
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from sklearn import preprocessing
import Draw
import data


def svr(xlsname, CV, distr, fig, sensi):
    print('SVR BEGIN')
    def my_loss_func(y_true, y_pred):
        mape = np.mean(np.abs((y_pred - y_true) / y_true))
        return mape
    mape = make_scorer(my_loss_func, greater_is_better=False)  # true是得分，false是损失 打印出来会反号

    # 数据集#
    indata, outdata, ninput, noutput, variable = data.load_data(xlsname)
    # Draw.correlation(indata, outdata, variable)  # 和经过代理模型之后对比

    # 训练
    x_train = indata
    y_train = outdata  # 交叉验证无测试集
    scaler = preprocessing.MinMaxScaler()  # StandardScaler,MinMaxScaler
    x_train = scaler.fit_transform(x_train)

    sv = GridSearchCV(SVR(), param_grid={"kernel": ('rbf', 'sigmoid'), "C": np.linspace(1, 64, 40),
                                         "gamma": np.linspace(0.00001, 1, 40)}, cv=5,
                      scoring={'MAPE': mape, 'R2': 'r2'}, refit='MAPE')  # start,stop,num

    wrapper = MultiOutputRegressor(sv)  # 简单SVR不支持多输出('rbf',)
    wrapper.fit(x_train, y_train)
    print(wrapper.estimators_[0].best_params_)
    print('MAPE:', -wrapper.estimators_[0].best_score_)
    best_index_r2 = np.nonzero(wrapper.estimators_[0].cv_results_['rank_test_R2'] == 1)[0][0]
    best_score_r2 = wrapper.estimators_[0].cv_results_['mean_test_R2'][best_index_r2]
    print('R2:', best_score_r2)
    # joblib.dump(wrapper, 'svr.pkl')

    # MCS抽样#
    Draw.draw(indata[0], outdata[0], wrapper, variable, CV, distr, fig, sensi, xlsname)

# CV = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.01,0.01,0.00033,0.00033]
# distr = ['ND','ND','ND','ND','ND','ND','ND','ND','ND','ND','ND']
# fig = '1111'
# svr('D:/ABAQUStemp/result/oneeight/300dataSet.xls',CV,distr,fig)

