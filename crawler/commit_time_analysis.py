#!~/usr/bin/python
from __future__ import division
import os, sys
sys.path.append('..')
import random
from crawling_github import Repository
import logging
import datetime
import matplotlib.pyplot as plt
import numpy as np

class CommitTime:
    def __init__(self):
        self.commit_date_dict=dict()
        self.date_commit_dict=dict()

    def construct_commit_time(self):
        for line in sys.stdin:
            items=line.strip().split()
            commit_sha=items[1]
            commit_date=datetime.datetime.strptime(items[2], '%m/%d/%Y')
            if commit_sha not in self.commit_date_dict.keys():
                self.commit_date_dict[commit_sha]=commit_date
                self.date_commit_dict[commit_date]=self.date_commit_dict.get(commit_date, [])+[commit_date]
    
    def query_commit_date(self, commit_list):
        date_list=[]
        print len(self.commit_date_dict)
        for commit_sha in commit_list:
            date_list.append(self.commit_date_dict[commit_sha])
        return sorted(date_list)

    def plot_commit_date(self, date_list, savePath):
        '''
            date_list is a list of date list
        '''
        base_date=min([d[0] for d in date_list])
        colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
        index=0
        leg=[]
        min_y=99999
        max_y=0
        plt.clf()
        for d_list in date_list:
            d_freq=dict()
            for d in d_list:
                d_freq[(d-base_date).days]=d_freq.get((d-base_date).days, 0)+1
            freq_list=sorted(d_freq.items(), key=lambda x:x[0])
            x_list=[x[0] for x in freq_list]
            y_list=[x[1] for x in freq_list]
            if min_y>min(y_list):
                min_y=min(y_list)

            if max_y<max(y_list):
                max_y=max(y_list)

            if index>=len(colorList):
                plt.plot(x_list, y_list, '+-', color=colorList[index-len(colorList)])
            else:
                plt.plot(x_list, y_list, '.-', color=colorList[index])
            index+=1
            leg.append('file-%s' % index)
        plt.xlabel('Days')
        plt.ylabel('Commit times')
        plt.ylim([min_y-1, max_y+1])
        if index>=len(colorList):
            plt.plot([x[0] for x in freq_list], [x[1] for x in freq_list], color=colorList[index-len(colorList)])
        else:
            plt.plot([x[0] for x in freq_list], [x[1] for x in freq_list], color=colorList[index])
        lg=plt.legend(leg, loc=2)
        lg.get_frame().set_alpha(0)
        plt.savefig(savePath+'.png', dpi=500)

    def plot_commit_date_cdf(self, date_list, savePath):
        '''
            date_list is a list of date list
        '''
        base_date=min([d[0] for d in date_list])
        colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
        index=0
        leg=[]
        plt.clf()
        for d_list in date_list:
            d_freq=dict()
            for d in d_list:
                d_freq[(d-base_date).days]=d_freq.get((d-base_date).days, 0)+1
            freq_list=sorted(d_freq.items(), key=lambda x:x[0])
            x_list=[x[0] for x in freq_list]
            y_list=[x[1] for x in freq_list]
            for i in range(1, len(y_list)):
                y_list[i]+=y_list[i-1]
            if index>=len(colorList):
                plt.plot(x_list, np.array(y_list)/y_list[-1], '+-', color=colorList[index-len(colorList)])
            else:
                plt.plot(x_list, np.array(y_list)/y_list[-1], '.-', color=colorList[index])
            index+=1
            leg.append('file-%s' % index)
        plt.xlabel('Days')
        plt.ylabel('Probability of commit times - CDF')
        lg=plt.legend(leg, loc=4)
        lg.get_frame().set_alpha(0)
        plt.savefig(savePath+'.png', dpi=500)

    def plot_commit_date_interval(self, date_list, savePath):
        '''
            date_list is a list of date list
        '''
        base_date=min([d[0] for d in date_list])
        colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
        index=0
        leg=[]
        plt.clf()
        for d_list in date_list:
            interval_freq=dict()
            d_freq=dict()
            for d in d_list:
                d_freq[(d-base_date).days]=d_freq.get((d-base_date).days, 0)+1
            freq_list=sorted(d_freq.items(), key=lambda x:x[0])
            x_list=[x[0] for x in freq_list]
            y_list=[x[1] for x in freq_list]
            for i in range(1, len(x_list)):
                interval_freq[x_list[i]-x_list[i-1]]=interval_freq.get(x_list[i]-x_list[i-1], 0)+1
            freq_list=sorted(interval_freq.items(), key=lambda x:x[0])
            x_list=[x[0] for x in freq_list]
            y_list=[x[1] for x in freq_list]
            if index>=len(colorList):
                plt.semilogx(x_list, y_list, '+-', color=colorList[index-len(colorList)])
            else:
                plt.semilogx(x_list, y_list, '.-', color=colorList[index])
            index+=1
            leg.append('file-%s' % index)
        plt.xlabel('Days')
        plt.ylabel('Probability of commit times\' interval - PDF')
        lg=plt.legend(leg, loc=4)
        lg.get_frame().set_alpha(0)
        plt.savefig(savePath+'.png', dpi=500)


    def plot_commit_date_interval_cdf(self, date_list, savePath):
        base_date=min([d[0] for d in date_list])
        colorList=['b', 'r', 'g', 'y', 'c', 'k', 'm']
        index=0
        leg=[]
        plt.clf()
        for d_list in date_list:
            interval_freq=dict()
            d_freq=dict()
            for d in d_list:
                d_freq[(d-base_date).days]=d_freq.get((d-base_date).days, 0)+1
            freq_list=sorted(d_freq.items(), key=lambda x:x[0])
            x_list=[x[0] for x in freq_list]
            y_list=[x[1] for x in freq_list]
            for i in range(1, len(x_list)):
                interval_freq[x_list[i]-x_list[i-1]]=interval_freq.get(x_list[i]-x_list[i-1], 0)+1
            freq_list=sorted(interval_freq.items(), key=lambda x:x[0])
            x_list=[x[0] for x in freq_list]
            y_list=[x[1] for x in freq_list]
            for i in range(1, len(y_list)):
                y_list[i]+=y_list[i-1]
            if index>=len(colorList):
                plt.semilogx(x_list, np.array(y_list)/y_list[-1], '+-', color=colorList[index-len(colorList)])
            else:
                plt.semilogx(x_list, np.array(y_list)/y_list[-1], '.-', color=colorList[index])
            index+=1
            leg.append('file-%s' % index)
        plt.xlabel('Days')
        plt.ylabel('Probability of commit times\' interval - CDF')
        lg=plt.legend(leg, loc=4)
        lg.get_frame().set_alpha(0)
        plt.savefig(savePath+'.png', dpi=500)

if __name__=='__main__':
    ct=CommitTime()
    ct.construct_commit_time()
    fp=open(sys.argv[1])#read query files from the file
    date_list=[]
    for file_rec in fp.readlines():
        items=file_rec.strip().split()
        print items[0]
        date_list.append(ct.query_commit_date(items[1:]))
    fp.close()
    if sys.argv[2].endswith('cdf'):
#        ct.plot_commit_date_cdf(date_list, sys.argv[2])
        ct.plot_commit_date_interval_cdf(date_list, sys.argv[2])
    else:
#        ct.plot_commit_date(date_list, sys.argv[2])
#        ct.plot_commit_date_cdf(date_list, '-'.join([sys.argv[2], 'cdf']))
        ct.plot_commit_date_interval(date_list, sys.argv[2])
        ct.plot_commit_date_interval_cdf(date_list, '-'.join([sys.argv[2], 'cdf']))

