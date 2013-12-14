#~/mypython/bin/python
from __future__ import division
import os, sys
import matplotlib.pyplot as plt
import plot_rank_freq
import math

def plot_together(fileList, savefig):
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    leg=[]
    for i in range(len(fileList)):
        fp=open(fileList[i])
        leg.append(fileList[i].split('/')[-2].split('-')[-1])
        x=[]
        y=[]
        while True:
            lines=fp.readlines(100000)
            if not lines:
                break
            for line in lines:
                item=line.strip().split()
                if len(item)==2:
                    x.append(int(item[0])+1)
                    y.append(int(item[1]))
        #plt.rc('text', usetex=True)
        if i>=len(colorList):
            plt.loglog(x,y,'+', color=colorList[len(colorList)-i])
        else:
            plt.loglog(x,y,'.', color=colorList[i])
        fp.close()
    plt.ylabel('Unique occurrence')
    plt.xlabel('Total occurrence')
    plt.legend(leg)
    plt.savefig(savefig+'.png', dpi=500)

if __name__=='__main__':
    if len(sys.argv)>4:
        fileList=[i for i in sys.argv[1:-1]]
        plot_together(fileList, sys.argv[-1])
    else:
        if len(sys.argv)>2:
            for i in range(1, len(sys.argv)-1):
                totalAppear=[]
                uniqAppear=[]
                fp=open(sys.argv[i])
                while True:
                    lines=fp.readlines(100000)
                    if not lines:
                        break
                    for line in lines:
                        item=line.strip().split()
                        if len(item)==2:
                            totalAppear.append(int(item[0])+1)
                            uniqAppear.append(int(item[1]))
                fp.close()
                plt.loglog(totalAppear, uniqAppear, '.')
        else:
            totalAppear=[]
            uniqAppear=[]
            lastLine=''
            for line in sys.stdin:
                try:
                    item=line.strip().split()
                    if len(item)==2 and lastLine!=line:
                        totalAppear.append(int(item[0]))
                        uniqAppear.append(int(item[1]))
                    lastLine=line
                except ValueError,e:
                    print e
            plt.loglog(totalAppear, uniqAppear, '.')
        (k, b, x1, y1, x2, y2)=plot_rank_freq.linear_fitting([math.log10(i) for i in totalAppear], [math.log10(j) for j in uniqAppear])
        plt.legend(['k=%.4f' % k])
        plt.xlabel('Total occurrence')
        plt.ylabel('Unique occurrence')
        plt.savefig(sys.argv[-1]+'.png', dpi=500)
