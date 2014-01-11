#!/usr/bin/python
from __future__ import division
import os, sys
import math
import numpy as np
import scipy
import scipy.stats
import matplotlib.pyplot as plt

class FileSizeChange:
    def __init__(self, factor, delta):
        self.multiplicative_factor=factor
        self.sum_delta=delta

    def __str__(self):
        return '%s:%s' % (self.multiplicative_factor, self.sum_delta)

    __repr__=__str__


def plot_size_change(file_change_list, save_path):
    plt.clf()
    colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
    leg=[]
    for index in range(len(file_change_list)):
        mean=np.mean(file_change_list[index])
        std=np.std(file_change_list[index])
#        mean=np.mean([math.pow(10, v) for v in file_change_list[index]])
#        std=np.std([math.pow(10, v) for v in file_change_list[index]])
        if index<len(colorList):
            plt.plot(range(1, len(file_change_list[index])+1), file_change_list[index], '.', color=colorList[index])
        elif index<len(colorList)*2:
            plt.plot(range(1, len(file_change_list[index])+1), file_change_list[index], '*', color=colorList[len(colorList)-index])
        elif index<len(colorList)*3:
            plt.plot(range(1, len(file_change_list[index])+1), file_change_list[index], '*', color=colorList[len(colorList)*2-index])
        leg.append('File:%s mean:%.6f std:%.6f' % (index+1, mean, std))
    plt.xlabel('The modified times for single file')
    plt.ylabel('Change')
    plt.legend(leg)
    plt.savefig(save_path+'.png', dpi=500)

def factor_dependence_test(file_change_list, N=10):
    '''
        the format of file_change_list is [file_name, [FileSizeChange, FileSizeChange, ...]]
    '''
    n_factor=[]
    n_delta=[]
    for file_record in file_change_list:
        for index in range(len(file_record[1])):
            if index<len(n_factor):
                n_factor[index].append(file_record[1][index].multiplicative_factor)
                n_delta[index].append(file_record[1][index].sum_delta)
            else:
                n_factor.append([file_record[1][index].multiplicative_factor])
                n_delta.append([file_record[1][index].sum_delta])


    print 'Testing on multiplicative factor'
    test_on_histogram_2d(n_factor, N)
    print 'Testing on delta'
    test_on_histogram_2d(n_delta, N)


def test_on_histogram_2d(factor_mat, N):
    max_factor=max([max(row) for row in factor_mat])
    min_factor=min([min(row) for row in factor_mat])
    hist_2d=[]
    column_sum=[]
    row_sum=[]
    for index in range(len(factor_mat)):
        hist, bins=np.histogram(factor_mat[index], range=(min_factor, max_factor+(max_factor-min_factor)/N), bins=N)
        row_sum.append(sum(hist))
        if len(column_sum)==0:
            column_sum=[c for c in hist]
        else:
            for col_index in range(len(hist)):
                column_sum[col_index]+=hist[col_index]

        hist_2d.append(hist)

    print 'Row sum:%s, Col sum:%s' % (sum(row_sum), sum(column_sum))
    total=sum(column_sum)
    
    observation=[]
    expected=[]
    print 'Total:%s' % total
    for r_index in range(len(hist_2d)):
        for c_index in range(len(hist_2d[r_index])):
            if row_sum[r_index]!=0 and column_sum[c_index]!=0:
#                print hist_2d[r_index][c_index], row_sum[r_index]*column_sum[c_index]/total
                observation.append(hist_2d[r_index][c_index])
                expected.append(row_sum[r_index]*column_sum[c_index]/total)
    print 'Degree of freedom:%s' % len(observation)
#    print sum([(expected[index]-observation[index])**2/expected[index] for index in range(len(observation))])
#    chisq, p=scipy.stats.chisquare(f_obs=observation, f_exp=expected, ddof=len(observation)-1)
    r=len(filter(lambda x:x>0, row_sum))
    c=len(filter(lambda x:x>0, column_sum))
    print 'Non-zero row:%s, Non-zero column:%s' % (r, c)
    chisq, p=scipy.stats.chisquare(f_obs=observation, f_exp=expected, ddof=r+c-1)
    print '%s with P-value:%s' % (chisq, p)

def read_file_size_log(read_path):
    fp=open(read_path)
    file_change_dict=dict()
    for line in fp.readlines():
        items=line.strip().split()
        if len(items)==4 and items[2].isdigit() and  items[3].isdigit():
            if float(items[1])>0:
                change=FileSizeChange(float(items[1]), int(items[3])-int(items[2]))
                file_change_dict[items[0]]=file_change_dict.get(items[0], [])+[change]
    fp.close()
    file_change_list=sorted(file_change_dict.items(), key=lambda x:len(x[1]), reverse=True)
    return file_change_list

if __name__=='__main__':
    file_list=read_file_size_log(sys.argv[1])
#    plot_list=[[math.log10(change.multiplicative_factor) for change in f[1]] for f in file_list[:10]]

    plot_list=[[math.log10(change.multiplicative_factor) for change in f[1]] for f in file_list]
    plot_size_change(plot_list, sys.argv[2])

    factor_dependence_test(file_list[:10], 30)

    file_factor=[[change.multiplicative_factor for change in file[1]] for file in file_list]
    file_delta=[[change.sum_delta for change in file[1]] for file in file_list[:10]]
    test_on_histogram_2d(file_factor, 30)
    test_on_histogram_2d(file_delta, 30)
