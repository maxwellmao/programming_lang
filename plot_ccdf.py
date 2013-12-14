#~/mypython/bin/python
from __future__ import division
import os, sys
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import plot_rank_freq
import math

def plot_together(fileList, savePath, sub=False, lang=''):
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    leg=[]
    fitting=False
    for i in range(0, len(fileList), 2):
        fp=open(fileList[i])
#        leg.append(fileList[i].split('/')[-1])
        x=[]
        y=[]
        while True:
            lines=fp.readlines(100000)
            if not lines:
                break
            for line in lines:
                item=line.strip().split()
                if len(item)==2:
                    x.append(int(item[0]))
                    y.append(int(item[1]))
        ax=np.array(x)
        ay=np.array(y)/max(y)
        #plt.rc('text', usetex=True)
        start=10
        end=int(len(ay)/10)
#        item_type=fileList[i].split('/')[-1].split('-')[-2]
        item_type=fileList[i+1]
#        if item_type.startswith('pygment'):
#            item_type='_'.join(item_type.split('_')[2:])
#        else:
#            item_type='_'.join(item_type.split('_')[:-1])
        print item_type
        if fitting and start<end:
            (k, b, x1, y1, x2, y2)=plot_rank_freq.linear_fitting([math.log10(ax[index]) for index in range(start, end+1)], [math.log10(ay[j_index]) for j_index in range(start-1, end)])
        #    print k
            leg.append('%s a=%.4f' % (item_type, k))
        else:
            leg.append(item_type)

        if int(i/2)>=len(colorList):
            if int(i/2)>=2*len(colorList):
                plt.loglog(ax,ay,'*', color=colorList[int(i/2)-len(colorList)])
            else:
                plt.loglog(ax,ay,'+', color=colorList[int(i/2)-2*len(colorList)])
        else:
            plt.loglog(ax,ay,'.', color=colorList[int(i/2)])
        fp.close()
    #plt.title('Distribution of token\'s appearence')
    plt.xlabel('Sizes of files(# of tokens)'+lang)
    #if savePath.split('/')[-1].find('file')!=-1:
    #    plt.xlabel('Token appearence(# of files)'+lang)
    #else:
    #    plt.xlabel('Token appearence(among corpus)'+lang)
    plt.ylabel('P(X<=x)-CCDF')
    print leg
    lg=plt.legend(leg)
    lg.get_frame().set_alpha(0)
    if not sub:
        plt.savefig(savePath+'.png', dpi=500)

def sub_plot():
    reposDir='repos-final'
    item=['pygment_token_all', 'all', 'pygment_token_comment', 'comment', 'pygment_token_literal', 'literal', 'pygment_token_program', 'program', 'pygment_token_program_operator', 'program_operator', 'token_dict_pygments-2_gram_refine', '2_gram', 'token_dict_pygments-3_gram_refine', '3_gram']

    item=['file_size_all', 'all', 'file_size_program', 'program']

    lang=['pl', 'asm', 'java', 'lisp']
    option='-ccdf'
#    lang=['py', 'fortran', 'erlang', 'matlab']
    plt.figure(1)
    for l in range(len(lang)):
        plt.subplot(2,2,l+1)
        filelist=[]
        for i in range(0, len(item), 2):
            filelist.append(os.path.join('-'.join([reposDir, lang[l]]), item[i]+option))
            filelist.append(item[i+1])
        plot_together(filelist, '', True, lang[l])
    plt.savefig('_'.join(['-'.join(lang), 'file-size-ccdf'])+'.png', dpi=500)

if __name__=='__main__':
    if len(sys.argv)>2:
        fileList=[i for i in sys.argv[1:-1]]
        plot_together(fileList, sys.argv[-1])
    elif len(sys.argv)==1:
        sub_plot()
    elif len(sys.argv)==2:
        x=[]
        y=[]
        for line in sys.stdin:
            item=line.strip().split()
            x.append(int(item[0]))
            y.append(int(item[1]))
        if len(x)==0:
            print 'Empty of ccdf:', sys.argv[1]
            sys.exit(1)
        ax=np.array(x)
        ay=np.array(y)/max(y)
        #plt.rc('text', usetex=True)
        plt.loglog(ax,ay,'.')
        plt.title('Distribution of token\'s appearence')
        plt.xlabel('Token appearence(# of files)')
        plt.ylabel('P(X<=x)-CCDF')
        plt.savefig(sys.argv[1]+'.png', dpi=500)
