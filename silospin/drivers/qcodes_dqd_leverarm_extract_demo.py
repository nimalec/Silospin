# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 11:57:24 2023

@author: PC1
"""

# %matplotlib inline
import os, sys
import qcodes
import qtt
import matplotlib.pyplot as plt
import numpy as np

from qcodes.plots.qcmatplotlib import MatPlot
from qcodes.data.data_set import DataSet
from qtt.data import diffDataset
from qtt.algorithms.bias_triangles import perpLineIntersect, lever_arm, E_charging

exampledatadir=os.path.join(qtt.__path__[0],'exampledata')
DataSet.default_io = qcodes.data.io.DiskIO(exampledatadir)
dataset_anticrossing = qcodes.data.data_set.load_data('charge_stability_diagram_double_dot_system_detail')
dataset_la = qcodes.data.data_set.load_data('charge_stability_diagram_double_dot_system_bias_triangle')
dataset_Ec = qcodes.data.data_set.load_data('charge_stability_diagram_double_dot_system')

# plt.figure(1); plt.clf()
# MatPlot([dataset_anticrossing.measured], num = 1)
# _=plt.suptitle('Anti crossing (1,0)--(0,1)')

plt.figure(1); plt.clf()
MatPlot([dataset_la.measured], num = 1)
_=plt.suptitle('Bias triangle')

dot = 'P4'

if dot == 'P4':
    vertical = False
elif dot == 'P5':
    vertical = True
else:
    print("Please choose either dot 4 or dot 5")

# clicked_pts = np.array([[  24.87913077,   38.63388728,   40.44875099],
#        [ 135.28934654,  128.50469446,  111.75508464]])

lev_arm_fit = perpLineIntersect(dataset_la, description = 'lever_arm', vertical = vertical)

bias = dataset_la.snapshot()['allgatevalues']['O5'] # bias voltage extracted from the dataset
print(bias)
lev_arm = lever_arm(bias, lev_arm_fit, fig = True)
print('''The lever arm of gate %s to dot %s is %.2f ueV/mV'''%(dot, dot[1], lev_arm))