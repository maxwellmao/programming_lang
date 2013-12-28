#!/usr/bin/python
from __future__ import division
import powerlaw
import os, sys
import numpy as np
import math
import matplotlib.pyplot as plt

def read_data(file_path):
    fp=open(file_path)
    d=[]
    for line in fp.readlines():
        d.append(int(line.strip()))
    fp.close()
    data=np.array(d)
    print data
    fit=powerlaw.Fit(data, sigma_threshold=0.001)
    r,p = fit.distribution_compare('power_law', 'lognormal')

if __name__=='__main__':
    read_data(sys.argv[1])
