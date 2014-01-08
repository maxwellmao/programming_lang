#!/usr/bin/python
from __future__ import division
import numpy as np
import scipy
import os, sys
import math
import matplotlib.pyplot as plt

def convert_to_signal(read_path, save_path):
    fp=open(read_path)
    log_value=[]
    for line in fp.readlines():
        item=line.strip().split()
        if len(item)==2:
            for i in range(int(item[-1])):
                log_value.append(math.log10(float(item[0])))
    fp.close()
    print 'Mean:%s' % sum(log_value)
    abs_max=max(log_value)
    if (-min(log_value) > max(log_value)):
        abs_max=-min(log_value)
    hist, bins = np.histogram(log_value, range=(-abs_max, abs_max), bins=499)
    hist=hist/sum(hist)
    print len(bins), len(hist)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.savefig(save_path+'.png', dpi=500)
    for index in range(len(bins)-1):
        if bins[index]<=0 and bins[index+1]>0:
            break
    print '%s bins before 0' % index
    return hist, bins[1]-bins[0], bins[0]

def load_filesize(read_path, interval):
    '''
        reading pdf of file size
    '''
    initial_value=[]
    fp=open(read_path)
    for line in fp.readlines():
        items=line.strip().split()
        if len(items)==2:
            for i in range(int(items[1])):
                initial_value.append(math.log10(float(items[0])))
    fp.close()
    print min(initial_value)-interval, max(initial_value)+interval
    hist, bins=np.histogram(initial_value, bins=np.arange(min(initial_value)-interval, max(initial_value)+interval, interval))
    hist=hist/sum(hist)
    return hist, bins


def load_filesize_shift(read_path, interval, first_bin):
    '''
        reading pdf of file size
    '''
    initial_value=[]
    fp=open(read_path)
    for line in fp.readlines():
        items=line.strip().split()
        if len(items)==2:
            for i in range(int(items[1])):
                initial_value.append(math.log10(float(items[0])))
    fp.close()
    print min(initial_value)-interval, max(initial_value)+interval
    hist, bins=np.histogram(initial_value, bins=np.arange(first_bin, max(initial_value)+interval, interval))
    hist=hist/sum(hist)
    return hist, bins

def read_init(read_path):
    pass

def convolution(init_dist, save_path, interval, N=2):
    plt.clf()
    f_n=init_dist
    for i in range(1, N+1):
        f_n=np.convolve(f_n, init_dist)
#        f_n=np.fft.ifft(np.fft.fft(f_n, n=2*len(f_n)-1)*np.fft.fft(init_dist, n=2*len(f_n)-1), axis=0)
#        f_n=f_n[int(math.floor((len(f_n)-1)/2)):int(math.floor((len(f_n)-1)/2))+len(f_n)]
    print len(f_n)
#    print f_n
##    fp=open(save_path, 'w')
##    fp.write('\n'.join([str(i) for i in f_n]))
##    fp.close()
#    print '\n'.join([str(i) for i in f_n])
    plt.plot(np.arange(int((1-len(f_n))/2)*interval, int((len(f_n)-1)/2+1)*interval, interval), f_n)
#    plt.plot(range(int((1-len(f_n))/2), int((len(f_n)-1)/2+1)), f_n)
    plt.savefig(save_path+'.png', dpi=500)
    return f_n

(_ccdf, _cdf)=range(2)

def plot_dist(hist_seq, bins, plot_type=_cdf):
    print plot_type
    hist=[s for s in hist_seq]
    dist=[]
    cumulative=0
    if plot_type==_ccdf:
        hist.reverse()

    for h in hist:
        cumulative+=h
        dist.append(cumulative)
    if plot_type==_ccdf:
        dist.reverse()
    plt.plot(bins, dist)

def usage():
    print 'python multilicative.py Multi_factor_reading_file Multi_factor_plot_file Conv_of_multi_factor_plot_file Initial_file_size_pdf_file latest_file_size'

if __name__=='__main__':
    seq, interval, first_bin=convert_to_signal(sys.argv[1], sys.argv[2])
    conv=convolution(seq, sys.argv[3], interval, 10)
    print 'Sum of mulitiplicative factors after convlution:%s' % sum(conv)
    initial_seq, inital_bins=load_filesize_shift(sys.argv[4], interval, first_bin)
    actual_latest_seq, actual_lastest_bins=load_filesize_shift(sys.argv[5], interval, first_bin)
    latest_seq=np.convolve(initial_seq, conv)
    plt.clf()
    print len(initial_seq), len(np.arange(min(initial_seq)-interval, max(initial_seq)+interval, interval))
    initial_center = (inital_bins[:-1] + inital_bins[1:]) / 2
    actual_lastest_center=(actual_lastest_bins[:-1]+actual_lastest_bins[1:])/2
    plt.plot(initial_center, initial_seq, '.')
    plt.plot(actual_lastest_center, actual_latest_seq, '.')
#+int((len(conv)+1)/2)*interval
    plt.plot(np.arange(int((1-len(latest_seq))/2)*interval, int((len(latest_seq)-1)/2+1)*interval, interval), latest_seq)
    plt.legend(['Inital', 'Latest', 'Convolution'])
    print 'Sum of latest after convlution:%s' % sum(latest_seq)
    plt.savefig(sys.argv[-1]+'.png', dpi=500)

    plt.clf()
    plot_dist(initial_seq, initial_center)
    plot_dist(actual_latest_seq, actual_lastest_center)
    plot_dist(latest_seq, np.arange(int((1-len(latest_seq))/2)*interval, int((len(latest_seq)-1)/2+1)*interval, interval))
    plt.legend(['Inital', 'Latest', 'Convolution'])
    plt.savefig(sys.argv[-1]+'-cdf.png', dpi=500)
    
    plt.clf()
    plot_dist(initial_seq, initial_center, _ccdf)
    plot_dist(actual_latest_seq, actual_lastest_center, _ccdf)
    plot_dist(latest_seq, np.arange(int((1-len(latest_seq))/2)*interval, int((len(latest_seq)-1)/2+1)*interval, interval), _ccdf)
    plt.legend(['Inital', 'Latest', 'Convolution'])
    plt.savefig(sys.argv[-1]+'-ccdf.png', dpi=500)
#    plt.loglog()
