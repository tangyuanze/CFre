# -*- coding: UTF-8 -*-
import ELM
import SVR
import ANN
import GRNN
import sys

model = sys.argv[1]
path = sys.argv[2]
sample = int(sys.argv[3])

cv = sys.argv[4]
cvs = cv.split(',')
CV = []
for i in range(len(cvs)):
    CV.append(float(cvs[i]))
distribution = sys.argv[5]
distr = distribution.split(',')

fig = sys.argv[6]
sensi = float(sys.argv[7])

if model == 'ANN':
    ANN.ann(path, sample, CV, distr, fig, sensi)
elif model == 'ELM':
    ELM.elm(path, sample, CV, distr, fig, sensi)
elif model == 'GRNN':
    GRNN.grnn(path, CV, distr, fig, sensi)
elif model == 'SVR':
    SVR.svr(path, CV, distr, fig, sensi)


