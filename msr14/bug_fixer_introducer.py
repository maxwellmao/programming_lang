#!/usr/bin/python
import os, sys
import MySQLdb
import matplotlib.pyplot as plt
from commit_mongo import hist_data
from commit_mongo import _pdf, _ccdf
from two_d_histogram import scatter_two
from two_d_histogram import _loglog, _normal
import codecs

def bug_introducer_dist():
    fp=open('results/BugIntroducerFixerFromFile.log')
    bug_introducing={}
    bug_solving_by_others={}
    bug_file=codecs.open('results/BugIntroducerCommit', 'w', 'utf-8')
    for line in fp.readlines():
        item=line.strip().split(' ', 10)
        if len(item)<10:
            print line.strip()
            continue
#            introducer=item[10].split(':')[1]
#            fixer=item[11].split(':')[1]
        if item[7].find(':')>-1:
            sha=item[7].split(':')[1]
        else:
            print sha
        introducer=item[10][:item[10].find('Fixer:')].strip().split(':')[1]
        fixer=item[10][item[10].find('Fixer:'):].strip().split(':')[1]
        bug_sha_set=bug_introducing.get(introducer, set())
        bug_sha_set.add(sha)
        bug_introducing[introducer]=bug_sha_set
        if introducer!=fixer:
            bug_sha_set=bug_solving_by_others.get(introducer, set())
            bug_sha_set.add(sha)
            bug_solving_by_others[introducer]=bug_sha_set
        try:
            bug_file.write('%s %s\n' % (introducer, sha))
        except Exception as e:
#            print e
            pass
#        else:
#            print line.strip()
    fp.close()
    plt.clf()
    bug_commit_num=[len(v) for v in bug_solving_by_others.values()]
    hist, bin_edges=hist_data(bug_commit_num, N=max(bug_commit_num)-min(bug_commit_num)+1, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    hist, bin_edges=hist_data(bug_commit_num, N=max(bug_commit_num)-min(bug_commit_num)+1, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    plt.xlabel('Number of bug introducing commits')
    plt.ylabel('Probability')
    plt.legend(['PDF', 'CCDF'])
    plt.savefig('results/BugSolvingByOther.png', dpi=500)
    plt.clf()
    data_dict={}
    for user_id in set(bug_introducing.keys()).union(set(bug_solving_by_others.keys())):
        total_commit=bug_introducing.get(user_id, set())
        other_commit=bug_solving_by_others.get(user_id, set())
        data_str='%s-%s' % (len(total_commit), len(other_commit))
        data_dict[data_str]=data_dict.get(data_str, 0)+1
    data=[]
    for data_str, freq in data_dict.items():
        data.append([int(data_str.split('-')[0]), int(data_str.split('-')[1]), freq])
    scatter_two(data, '', xlabel='Total bug-introducing commits', ylabel='Others bug-fixing commits', save_file='results/BugIntroducingFixing', scale=_loglog)
    bug_file.close()


if __name__=='__main__':
    bug_introducer_dist()
