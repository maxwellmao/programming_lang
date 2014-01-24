#!/usr/bin/python
from __future__ import division
import sys, os
import numpy as np
import matplotlib.pyplot as plt
import math

def linear_fitting(x,y):
#    print x
#    print y
    if len(x)==len(y):
        xy_sum=reduce((lambda t1,t2: t1+t2[0]*t2[1]), zip(x,y), 0)
        x2=reduce((lambda x1, x2: x1+x2*x2), x, 0)
        k=(len(x)*xy_sum-sum(x)*sum(y))/(len(x)*x2-sum(x)*sum(x))
        b=(sum(y)-k*sum(x))/len(x)
        x_min=min(x)
        x_max=max(x)
        y_min=k*x_min+b
        y_max=k*x_max+b
        return (k,b, x_min, y_min, x_max, y_max)
    else:
        print 'The length of x and y must be same'

def histogram_2d(data):
#    total_freq=sum([item[2] for item in data])
#    hist_2d=np.array.zeros((max(x), max(y)))
#    for item in data:
#        hist_2d[]
    x=[item[0] for item in data]
    y=[item[1] for item in data]
    print min(x), max(x)
    print min(y), max(y)
    H, xedges, yedges=np.histogram2d(x, y, bins=[max(x)-min(x), max(y)-min(y)])
    H = np.rot90(H)
    H = np.flipud(H)
    Hmasked = np.ma.masked_where(H==0,H)
    plt.pcolormesh(xedges,yedges,Hmasked)
    plt.xlabel('add')
    plt.ylabel('delete')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Frequency')
    plt.savefig('CommitStats.png', dpi=500)

def plot_two(data):
    x=[item[0] for item in data]
    y=[item[1] for item in data]
#    plt.plot(x, y, '.')
    plt.loglog(x, y, '.')
    plt.xlabel('Add')
    plt.ylabel('Del')
    plt.savefig('CommitStats.png', dpi=500)

def parse_commit_stats():
    data=[]
    for line in sys.stdin:
        item=line.strip().split()
        if len(item)==2:
            data+=[int(item[-1])*[int(i) for i in item[0].split('-')]]
        else:
            print line.strip()
#    histogram_2d(data)
    plot_two(data)

def scatter_two(data, commit_type=''):
    x=[]
    y=[]
    z=[]
    for item in data:
        if item[0]>0 and item[1]>0:
            x.append(math.log10(item[0]))
            y.append(math.log10(item[1]))
            z.append(math.log10(item[2]))
#    x=[math.log(item[0]) for item in data]
#    y=[math.log(item[1]) for item in data]
    k,b, x_min, y_min, x_max, y_max=linear_fitting(x, y)
    print k, b
    print 'Correlation coefficient:'
    print np.corrcoef(x, y)
    total=sum(x)
    plt.scatter(x, y, c=z, s=10, vmin=int(min(z)), vmax=int(max(z)+1), lw = 0)
    plt.colorbar()
#, cmap=plt.cm.coolwarm)
    plt.xlabel('Add')
    plt.ylabel('Del')
    #'PullRequestCommit'
    print 'Saveing: CommitStats%s.png' % commit_type
    plt.savefig('CommitStats%s.png' % commit_type, dpi=500)
    #_pullrequestcommit  _PullRequestCommit

def parse_commit_stats_scatter(commit_type=''):
    data=[]
    for line in sys.stdin:
        item=line.strip().split()
        num=item[0].split('-')
        data.append([int(num[0]), int(num[1]), int(item[-1])])
    scatter_two(sorted(data, key=lambda x:x[2]), commit_type)

if __name__=='__main__':
#    parse_commit_stats()
    if len(sys.argv)>1:
        parse_commit_stats_scatter(sys.argv[1])
    else:
        parse_commit_stats_scatter()
