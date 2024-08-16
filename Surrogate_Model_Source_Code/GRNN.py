# -*- coding: utf-8 -*-
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from pyGRNN import GRNN
import data
import Draw
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import make_scorer


def grnn(xlsname, CV, distr, fig, sensi):
    print('GRNN BEGIN')

    def my_loss_func(y_true, y_pred):
        mape = np.mean(np.abs((y_pred - y_true) / y_true))
        return mape
    mape = make_scorer(my_loss_func, greater_is_better=False)

    indata, outdata, ninput, noutput, variable = data.load_data(xlsname)
    X_train = indata
    y_train = outdata
    scaler = preprocessing.MinMaxScaler()
    X_train = scaler.fit_transform(X_train)

    IGRNN = GRNN()
    params = {'kernel': ["RBF"], 'sigma': list(np.arange(0.01, 4, 0.01)), 'calibration': ['None']}
    grid = GridSearchCV(estimator=IGRNN, param_grid=params, scoring={'MAPE': mape, 'R2': 'r2'}, refit='MAPE', cv=5)
    wrapper = MultiOutputRegressor(grid)
    wrapper.fit(X_train, y_train)
    # joblib.dump(wrapper, 'grnn.pkl')
    print(wrapper.estimators_[0].best_params_)
    print('MAPE:', wrapper.estimators_[0].best_score_)
    best_index_r2 = np.nonzero(wrapper.estimators_[0].cv_results_['rank_test_R2'] == 1)[0][0]
    best_score_r2 = wrapper.estimators_[0].cv_results_['mean_test_R2'][best_index_r2]
    print('R2:', best_score_r2)

    Draw.draw(indata[0], outdata[0], wrapper, variable, CV, distr, fig, sensi, xlsname)


