#~/mypython/bin/python
from __future__ import division
import os, sys
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import plot_rank_freq
import math
import numpy as np

def plot_dist(x, save_path):
    hist, bins = np.histogram(x, bins=500)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.savefig(save_path+'.png', dpi=500)
                
def plot_dist_together(x_list, leg, save_path):
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    for x in range(len(x_list)):
#        print x_list[x]
        hist, bins = np.histogram(x_list[x], bins=500)
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
#        plt.bar(center, hist, align='center', width=width)
        plt.plot(center, hist/sum(hist), '.', color=colorList[x])
    plt.legend(leg)
    plt.xlabel('Ratio of program tokens in a file')
    plt.ylabel('Probability')
    plt.savefig(save_path+'.png', dpi=500)

def load_size_files(file_list, save_path):
    x_list=[]
    print len(file_list)
    leg=[]
    for f in range(0, len(file_list), 2):
        fp=open(file_list[f])
        leg.append(file_list[f+1])
        x=[]
        for line in fp.readlines():
            num=line.strip().split()[-1].split(':')
            if len(num)==2:
                if int(num[0])>0:
                    if int(num[1])>int(num[0]):
                        print line.strip()
                    x.append(int(num[1])/int(num[0]))
            else:
                print line.strip()
        fp.close()
        x_list.append(x)
    return x_list, leg
#    plot_dist_together(x_list, leg, save_path)

def sub_plot(x, leg, index):
    plt.subplot(2,2,index+1)
    hist, bins = np.histogram(x, bins=500)
    center = (bins[:-1] + bins[1:]) / 2
    plt.plot(center, hist/sum(hist), '.')
    plt.legend([leg])
    plt.xlabel('Ratio of program tokens in a file')
    plt.ylabel('Probability')
    

if __name__=='__main__':
    if len(sys.argv)>2:
        x_list, leg=load_size_files(sys.argv[1:-1], sys.argv[-1])
        plt.figure(1)
        sub_plot(x_list[0], leg[0], 0)
        sub_plot(x_list[1], leg[1], 1)
        sub_plot(x_list[2], leg[2], 2)
        sub_plot(x_list[3], leg[3], 3)
        plt.savefig(sys.argv[-1]+'.png', dpi=500) 
