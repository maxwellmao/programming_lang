#~/mypython/bin/python
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import math
import powerlaw

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

def plot_together_ccdf(fileList, savePath, useTool=False):
    plt.clf()
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    leg=[]
    for i in range(len(fileList)):
        fp=open(fileList[i])
        leg.append(fileList[i].split('/')[-2].split('-')[-1])
        ccdf=[]
        cumulative=0
        while True:
            lines=fp.readlines(100000)
            if not lines:
                break
            for line in lines:
                cumulative+=int(line.split()[-1])
                ccdf.append(cumulative)
            
        if int(i/2)>=len(colorList):
            plt.loglog(range(len(ccdf), 0, -1), np.array(ccdf)/cumulative, '+', color=colorList[int(i/2)-len(colorList)])
        else:
            plt.loglog(range(len(ccdf), 0, -1), np.array(ccdf)/cumulative, '.', color=colorList[int(i/2)])
        fp.close()
        print fileList[i]
    plt.title('The distribution of token wrt rank in whole corpus(CCDF)')
    plt.xlabel('Rank of token')
    plt.ylabel('Frequence of token(P(X>=x))')
    lg=plt.legend(leg, loc=3)
    lg.get_frame().set_alpha(0)
    plt.savefig(savePath+'.png', dpi=500)

def generate_data(freq):
    data=[]
    for i in range(1, len(freq)):
        data+=freq[len(freq)-i]*[i]
    return data

def plot_together_pdf(fileList, savePath, useTool=False, lang='', sub=False):
    if not sub:
        plt.clf()
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    leg=[]
    fitting=True
    k_list=[]
    for i in range(0, len(fileList), 2):
        fp=open(fileList[i])
#        leg.append(fileList[i].split('/')[-1].split('-')[-1])
#        lang=fileList[i].split('/')[-1].split('-')[-2]
#        lang=fileList[i].split('/')[-1].split('-')[-2]
#        leg.append(fileList[i].split('/')[-1])
        freq=[]
#        ccdf=[]
        cumulative=0
        while True:
            lines=fp.readlines(100000)
            if not lines:
                break
            for line in lines:
                freq.append(int(line.strip().split()[-1]))
#                print line.strip().split()[-1]
                cumulative+=int(line.strip().split()[-1])
                #ccdf.append(cumulative)
        fp.close()
#        print fileList[i]
#        if useTool:
#            fit=powerlaw.Fit(np.array(generate_data(freq)))
#            print fileList[i], 'xmin:', fit.xmin
#            print fileList[i], 'alpha:', fit.power_law.alpha
#            print fileList[i], 'D:', fit.power_law.D
#        else:
        start=10
        freq.reverse()
#        end=int(len(freq)/100)
        end=int(len(freq)/10)
        print end
        item_type=fileList[i+1]
#        item_type=fileList[i].split('/')[-1].split('-')[-2]
#        if item_type.startswith('pygment'):
#            item_type='_'.join(item_type.split('_')[2:])
#        else:
#            item_type='_'.join(item_type.split('_')[:-1])
        print item_type
        if fitting and start<end:
#            print range(start, end+1)
#            print freq[start-1:end]
            (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(index) for index in range(start, end+1)], [math.log10(freq[j_index]) for j_index in range(start-1, end)])
# (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(index) for index in range(start, end+1)], [math.log10(j/cumulative) for j in freq[start-1:end]])
#            print k
            k_list.append(k)
        #leg.append('%s a=%.4f' % (fileList[i].split('/')[-1].split('-')[-1], k))
            leg.append('%s a=%.4f' % (item_type, k))
        else:
            leg.append('%s' % item_type)
        if int(i/2)>=2*len(colorList):
            plt.loglog(range(len(freq)), np.array(freq)/cumulative, '*', color=colorList[int(i/2)-2*len(colorList)])
        elif int(i/2)>=len(colorList):
            plt.loglog(range(len(freq)), np.array(freq)/cumulative, '+', color=colorList[int(i/2)-len(colorList)])
        else:
            plt.loglog(range(len(freq)), np.array(freq)/cumulative, '.', color=colorList[int(i/2)])
    if not useTool:
        if len(lang)>0:
            plt.xlabel('-'.join(['Rank of token', lang]))
        else:
            plt.xlabel('Rank of token')
        plt.ylabel('Frequence of token')
        if not sub:
            print savePath
            print leg
            lg=plt.legend(leg)
            lg.get_frame().set_alpha(0)
            plt.title('Rank v.s. frequence of token in whole corpus')
            plt.savefig(savePath+'.png', dpi=500)
        print ' &'.join(['%.4f' % k for k in k_list])

def sub_plot():
    reposDir='repos-final'
    item=['pygment_token_all', 'all', 'pygment_token_comment', 'comment', 'pygment_token_literal', 'literal', 'pygment_token_program', 'program', 'pygment_token_program_operator', 'program_operator', 'token_dict_pygments-2_gram_refine', '2_gram', 'token_dict_pygments-3_gram_refine', '3_gram']
    lang=['pl', 'asm', 'lisp', 'java']
    lang=['rb',  'erlang', 'fortran','matlab']
    plt.figure(1)
    option='-sort'
    for l in range(len(lang)):
        print lang[l]
        plt.subplot(2,2,l+1)
        filelist=[]
        for i in range(0, len(item), 2):
            filelist.append(os.path.join('-'.join([reposDir, lang[l]]), item[i]+option))
            filelist.append(item[i+1])
        plot_together_pdf(filelist, '', False, lang[l], True)
    plt.savefig('_'.join(['-'.join(lang), 'zipf-law'])+'.png', dpi=500)

if __name__=='__main__':
    if len(sys.argv)>3:
        fileList=[i for i in sys.argv[1:-1]]
        plot_together_pdf(fileList, sys.argv[-1], False)
        #print fileList
#        plot_together_ccdf(fileList, sys.argv[-1]+'_ccdf', True)
    elif len(sys.argv)==1:
        sub_plot()
    elif len(sys.argv)==2:
        freq=[]
        ccdf=[]
        cumulative=0
        for line in sys.stdin:
            #print line.strip()
            freq.append(int(line.split()[-1]))
            cumulative+=int(line.split()[-1])
            ccdf.append(cumulative)
        if len(freq)==0:
            print sys.argv[1]
            sys.exit(1)
        plt.loglog(range(len(freq), 0, -1), np.array(freq)/cumulative, '.')
        freq.reverse()
        start=100
        end=int(len(freq)/10)
        if start<end:
            (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(index) for index in range(start, end+1)], [math.log10(j/cumulative) for j in freq[start-1:end]])
            plt.loglog([math.pow(10, x1), math.pow(10, x2)], [math.pow(10, y1),math.pow(10, y2)], 'k-', linewidth=3)
            plt.annotate(('K=%.4f' % k), xy=(math.exp(x1), math.exp(y1)), xytext=(math.exp(x1), math.exp(y2)))
        #if len(freq)>=100000:
        #    print 'X1=%f, Y1=%f' % (math.log10(100), math.log10(freq[99]))
        #    print 'X2=%f, Y2=%f' % (math.log10(100000), math.log10(freq[99999]))
        #    (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(i) for i in range(100, 100001)], [math.log10(j/cumulative) for j in freq[99:100000]])
        #    print k,b,x1,y1,x2,y2
        #    plt.loglog([math.pow(10, x1), math.pow(10, x2)], [math.pow(10, y1),math.pow(10, y2)], 'k-', linewidth=3)
        #    plt.annotate(('K=%.4f'% k), xy=(math.exp(1), math.exp(y1)), xytext=(math.exp(x1), math.exp(y2)))
        #else:
        #    print 'X1=%f, Y1=%f' % (math.log10(10), math.log10(freq[9]))
        #    print 'X2=%f, Y2=%f' % (math.log10(1000), math.log10(freq[999]))
        #    (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(index) for index in range(10, 10001)], [math.log10(j/cumulative) for j in freq[9:10000]])
 #      #     (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(i) for i in range(10, 1001)], [math.log10(j/cumulative) for j in freq[9:1000]])
        #    print k,b,x1,y1,x2,y2
        #    plt.loglog([math.pow(10, x1), math.pow(10, x2)], [math.pow(10, y1),math.pow(10, y2)], 'k-', linewidth=3)
        #    plt.annotate(('K=%.4f'% k), xy=(math.exp(1), math.exp(y1)), xytext=(math.exp(x1), math.exp(y2)))
        #    print k

        #plt.title('Rank v.s. frequence of token in whole corpus('+sys.argv[1]+')')
        plt.xlabel('Rank of token')
        plt.ylabel('Frequence of token')
        plt.savefig(sys.argv[1]+'.png', dpi=500)
        #plt.clf()
        #
        #plt.loglog(range(len(freq), 0, -1), np.array(ccdf)/cumulative, '.')
        #ccdf.reverse()
        #if len(freq)>=100000:
        #    print 'X1=%f, Y1=%f' % (math.log10(100), math.log10(ccdf[99]/cumulative))
        #    print 'X2=%f, Y2=%f' % (math.log10(100000), math.log10(ccdf[99999]/cumulative))
        #    (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(i) for i in range(100, 100001)], [math.log10(j/cumulative) for j in ccdf[99:100000]])
#       #     (k, b, x1, y1, x2, y2)=linear_fitting(range(100, 100001), cumulative[100:100001])
        #    print k,b,x1,y1,x2,y2
        #    plt.loglog([math.pow(10, x1), math.pow(10, x2)], [math.pow(10, y1),math.pow(10, y2)], 'k-', linewidth=3)
        #    plt.annotate(('K=%.4f' % k), xy=(math.exp(x1), math.exp(y1)), xytext=(math.exp(x1), math.exp(y2)))
        #else:
        #    print 'X1=%f, Y1=%f' % (math.log10(10), math.log10(ccdf[9]/cumulative))
        #    print 'X2=%f, Y2=%f' % (math.log10(1000), math.log10(ccdf[999]/cumulative))
        #    (k, b, x1, y1, x2, y2)=linear_fitting([math.log10(i) for i in range(10, 1001)], [math.log10(j/cumulative) for j in ccdf[9:1000]])
#       #     (k, b, x1, y1, x2, y2)=linear_fitting(range(100, 100001), cumulative[100:100001])
        #    print k,b,x1,y1,x2,y2
        #    plt.loglog([math.pow(10, x1), math.pow(10, x2)], [math.pow(10, y1),math.pow(10, y2)], 'k-', linewidth=3)
        #    plt.annotate(('K=%.4f' % k), xy=(math.exp(x1), math.exp(y1)), xytext=(math.exp(x1), math.exp(y2)))
        #    print k
        #plt.title('Rank v.s. frequence (CCDF) of token in whole corpus('+sys.argv[1]+')')
        #plt.xlabel('Rank of token')
#        plt.ylabel('Frequence of token (CCDF)')
#        plt.savefig(sys.argv[2]+'-ccdf.png', dpi=500)
        #plt.clf()
