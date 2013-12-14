#~/mypython/bin/python
import os, sys
import matplotlib.pyplot as plt

def plot_together(fileList, savePath):
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    leg=[]
    for index in range(0, len(fileList), 2):
        fp=open(fileList[index])
        x=[]
        y=[]
        total=0
        for line in fp.readlines():
            item=line.strip().split()
            try:
                if len(item)==2 and item[0].isdigit() and item[1].isdigit():
                    x.append(int(item[0]))
                    y.append(int(item[1]))
                    total+=int(item[1])
            except IndexError, e:
                print e
                print line
                print savePath
            except ValueError, e:
                print e
                print line
                print savePath
        fp.close()
        plt.loglog(x, y, '.', color=colorList[index])
        leg.append(fileList[index+1])
    plt.xlabel('File size')
    plt.ylabel('Frequency')
    plt.legend(leg)
    plt.savefig(savePath+'.png', dpi=500)

if __name__=='__main__':
    if len(sys.argv)==2:
        x=[]
        y=[]
        for line in sys.stdin:
            item=line.strip().split()
            x.append(int(item[0]))
            y.append(int(item[1]))
        plt.loglog(x, y, '.')
        plt.xlabel('Token length')
        plt.ylabel('Frequency')
        plt.savefig(sys.argv[1]+'.png', dpi=500)
    else:
        plot_together(sys.argv[1:-1], sys.argv[-1])
