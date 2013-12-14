#!/usr/bin/python
from __future__ import division
from scipy.special import gamma as Gamma
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import math
import plot_rank_freq

def gamma(x,alpha=1):
#    return math.gamma(x-alpha+1)/math.gamma(x+1)
    return Gamma(x-alpha+1)/Gamma(x+1)

x=np.linspace(1, 100, 100)
colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
leg=[]
index=0
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
for a in np.arange(0.6, 1.6, 0.1):
    print a
    y=[gamma(i, a) for i in x]
    i=0
    j=0
    try:
        (k, b, x1, y1, x2, y2)=plot_rank_freq.linear_fitting([math.log10(x[i]) for i in range(len(x))], [math.log10(y[j]) for j in range(len(x))])
    except ValueError, e:
        print e
        print x
        print y
    if index>=len(colorList):
        plt.loglog(x, y, '+', color=colorList[index-len(colorList)])
    else:
        plt.loglog(x, y, '.', color=colorList[index])
    index+=1
    leg.append('a=%s, e=%.4f' % (a , k))
plt.legend(leg)
plt.xlabel('n')
plt.ylabel(r'${\Gamma(n-a+1)}/{\Gamma(n+1)}$')
plt.savefig('gamma.eps', dpi=500)
