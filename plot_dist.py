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

def load_x(file_list):
    x_list=[]
    print len(file_list)
    leg=[]
    for f in range(0, len(file_list), 2):
        fp=open(file_list[f])
        leg.append(file_list[f+1])
        x=dict()
        for line in fp.readlines():
            if len(line.strip().split())==1:
                x[float(line.strip())]=x.get(float(line.strip()), 0)+1
            else:
                items=line.strip().split()
                x[float(items[0])]=x.get(float(items[0]), 0)+int(items[1])
        fp.close()
        x_list.append(x)
    return x_list, leg

def plot_xlist_to_pdf(x_list, leg_list):
    color_list=['b', 'r', 'g', 'k', 'c', 'm']
    for index in range(len(x_list)):
        cum=0
        pdf=[]
        for item in sorted(x_list[index].items(), key=lambda x:x[0], reverse=True):
            cum+=item[1]
            pdf.append([item[0], item[1]])
#        print ccdf
        plt.plot([item[0] for item in pdf], [item[1]/cum for item in pdf], '.', color=color_list[index])
#        plt.semilogx([item[0] for item in ccdf], [item[1]/cum for item in ccdf], '.', color=color_list[index])
    lg=plt.legend(leg_list, loc=3)
    lg.get_frame().set_alpha(0)
#    plt.xlabel('Multiplicative factors')
    plt.xlabel('File Size')
    plt.ylabel('PDF')

def plot_xlist_to_ccdf(x_list, leg_list):
    color_list=['b', 'r', 'g', 'k', 'c', 'm']
    for index in range(len(x_list)):
        cum=0
        ccdf=[]
        mean=0.0
        mean_2=0.0
        for item in sorted(x_list[index].items(), key=lambda x:x[0], reverse=True):
            if item[0]==1.0:
                print item
            mean+=item[0]*item[1]
            mean_2+=item[0]*item[0]*item[1]
            cum+=item[1]
            ccdf.append([item[0], cum])
#        print ccdf
        plt.plot([item[0] for item in ccdf], [item[1]/cum for item in ccdf], '.', color=color_list[index])
        leg_list[index]+=('-mean:%.4f var:%.4f' % (mean/cum, mean_2/cum-mean*mean/(cum*cum)))
        print 'CCDF: The mean of %s is %s, variance is %s in total %s' % (leg_list[index], mean/cum, mean_2/cum-mean*mean/(cum*cum), cum)
    lg=plt.legend(leg_list, loc=3)
    lg.get_frame().set_alpha(0)
    plt.xlabel('Multiplicative factors')
    plt.ylabel('CCDF')
        


def sub_plot(x, leg, index):
    plt.subplot(2,2,index+1)
    hist, bins = np.histogram(x, bins=500)
    center = (bins[:-1] + bins[1:]) / 2
    plt.plot(center, hist/sum(hist), '.')
    lg=plt.legend([leg])
    lg.get_frame().set_alpha(0)
    plt.xlabel('Ratio of program tokens in a file')
    plt.ylabel('Probability')
    

if __name__=='__main__':
    if len(sys.argv)>2:
        x_list, leg=load_x(sys.argv[1:-1])
        if sys.argv[-1].endswith('ccdf'):
            plot_xlist_to_ccdf(x_list, leg)
        elif sys.argv[-1].endswith('pdf'):
            plot_xlist_to_pdf(x_list, leg)
#        plt.figure(1)
#        sub_plot(x_list[0], leg[0], 0)
#        sub_plot(x_list[1], leg[1], 1)
#        sub_plot(x_list[2], leg[2], 2)
#        sub_plot(x_list[3], leg[3], 3)
        plt.savefig(sys.argv[-1]+'.png', dpi=500)
