# -*- coding: UTF-8 -*-
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import os
import data
import Draw
from sklearn import preprocessing

def create_model(ninput, noutput):
    model = Sequential()
    model.add(Dense(ninput, activation='relu', input_shape=(ninput,), name='Dense1'))
    model.add(Dense(64, activation='relu', name='Dense2'))
    model.add(Dense(128, activation='relu', name='Dense3'))
    model.add(Dropout(0.02, name='Dropout1'))
    model.add(Dense(64, activation='relu', name='Dense4'))
    model.add(Dense(noutput, name='Output'))
    return model

batch_size = 32
epoch = 800
def ann(xlsname, num, CV, distr, fig, sensi):
    if num == 0:
        indata, outdata, ninput, noutput, variable = data.load_data(xlsname)
    else:
        indata, outdata, ninput, noutput, variable = data.sample_expansion(xlsname, num, CV, distr)
    scaler = preprocessing.MinMaxScaler()
    X_data = scaler.fit_transform(indata)

    # 训练ANN模型#
    print('ANN BEGIN')
    kfold = KFold(n_splits=10, random_state=11, shuffle=True)  # KFold回归，StratifiedKFold分类
    MAPEmin = 1
    callback_list = [EarlyStopping(monitor='mean_absolute_error', patience=40, verbose=0, mode='min'),
                     ModelCheckpoint(os.path.join(os.path.dirname(xlsname), 'ANNmodel.hdf5'),
                                     monitor='mean_absolute_error', verbose=0, save_best_only=True, mode='min'),
                     ReduceLROnPlateau(monitor='mean_absolute_error', factor=0.5, patience=5, min_lr=0.00001)]
    for train, test in kfold.split(X_data, outdata):
        model = create_model(ninput, noutput)
        model.compile(loss='mae', optimizer='Adam', metrics=['mean_absolute_error'])
        model.fit(X_data[train], outdata[train], batch_size=batch_size, epochs=epoch, verbose=0, callbacks=callback_list)
        Y_pred = model.predict(X_data[test])
        ANNMAPE = np.mean(np.abs((Y_pred - outdata[test]) / outdata[test]))
        if ANNMAPE < MAPEmin:
            MAPEmin = ANNMAPE
            id_tr = train
            id_te = test

    model.fit(X_data[id_tr], outdata[id_tr], batch_size=batch_size, epochs=epoch, verbose=0, callbacks=callback_list)

    Y_pred = model.predict(X_data[id_te])
    ANNMAPE = np.mean(np.abs((Y_pred - outdata[id_te]) / outdata[id_te]))
    ANNR2 = r2_score(outdata[id_te], Y_pred)
    n = len(outdata)
    p = noutput
    ANNAdjust_R2 = 1 - (1 - ANNR2) * (n - 1) / (n - p - 1)
    print(" ANN-Adjust_R2: ", ANNAdjust_R2)
    print(" ANN-MAPE: ", ANNMAPE)
    Draw.draw(indata[0], outdata[0], model, variable, CV, distr, fig, sensi, xlsname)

