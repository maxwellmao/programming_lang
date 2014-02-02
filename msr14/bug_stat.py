#!/usr/bin/python
from __future__ import division
import os, sys
import MySQLdb
import numpy as np
import matplotlib.pyplot as plt
from commit_mongo import hist_data
from fork_info import construct_fork_tree
from fork_info import assign_fork_to_repos
import codecs
import re
from pymongo import Connection
from two_d_histogram import scatter_two
from two_d_histogram import _loglog, _normal
from commit_mongo import _pdf, _ccdf

mySqlDB=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
cursor=mySqlDB.cursor()
con=Connection()
db=con.msr14
db.authenticate('msr14', 'msr14')

def issue_commit_repo():
    '''
        measuring the quality of repo based on the issue/commit
    '''
    fork_tree=construct_fork_tree()
    repo_forks_map, fork_repo_map=assign_fork_to_repos(fork_tree)
    fp=codecs.open('results/BugFixingCommits_BugFixingCommitInfo')
    
    for line in fp.readlines():
        for n in re.findall('\#\d+', line):
            pass
    fp.close()

def watcher_bug_stat(user_bug, user_commit_num):
    '''
        find the relationship between number of projects developer watches and the number of bugs he introduces
    '''
    sql='select count(*), user_id from watchers group by user_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    watches_bug={}
    watches_contribute={}
    for r in results:
        if user_commit_num.has_key(r[1]):
            wb_str='%s-%s' % (r[0], len(user_bug.get(r[1], set())))
            watches_bug[wb_str]=watches_bug.get(wb_str, 0)+1
            wc_str='%s-%s' % (r[0], user_commit_num[r[1]])
            watches_contribute[wc_str]=watches_contribute.get(wc_str, 0)+1
    data=[]
    for data_str, freq in watches_bug.items():
        data.append([int(data_str.split('-')[0]), int(data_str.split('-')[1]), freq])
    scatter_two(data, '', xlabel='Number of watches', ylabel='No of bug', save_file='results/WatchesBugNumDist', scale=_normal)

    data=[]
    for data_str, freq in watches_contribute.items():
        data.append([int(data_str.split('-')[0]), int(data_str.split('-')[1]), freq])
    scatter_two(data, '', xlabel='Number of watches', ylabel='No of bug', save_file='results/WatchesContributionsNumDist', scale=_normal)


def bug_per_commit():
    '''
        measuring the effectiveness of a developer by number of introduced bugs per commit
    '''
    sql='select sha, author_id, committer_id from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    commit_user={}
    user_commit_num={}
    user_bug={}
    user_fixing_bug={}
    for r in results:
        commit_user[r[0]]=r[1]
        user_commit_num[r[1]]=user_commit_num.get(r[1], 0)+1
    for line in sys.stdin:
        item=line.strip().split()
        if len(item)>7:
#            print item[7]
            sha=item[7].split(':')[-1]
            if commit_user.has_key(sha):
                bug_sha=user_bug.get(commit_user[sha], set())
                bug_sha.add(sha)
                user_bug[commit_user[sha]]=bug_sha

            sha=item[6].split(':')[-1]
            if commit_user.has_key(sha):
                bug_sha=user_bug.get(commit_user[sha], set())
                bug_sha.add(sha)
                user_fixing_bug[commit_user[sha]]=bug_sha

    commit_bug_num={}
    bug_per_commit_list=[]
    threshold=0.8
    for user in set(user_bug.keys()).union(set(user_commit_num.keys())):
        total_commit=user_commit_num.get(user, 0)
        bug_num=len(user_bug.get(user, set()))
        num_str='%s-%s' % (total_commit, bug_num)
        commit_bug_num[num_str]=commit_bug_num.get(num_str, 0)+1
        bug_per_commit_list.append(bug_num/total_commit)
        if bug_num/total_commit>threshold:
            print user, total_commit
    data=[]
    for data_str, freq in commit_bug_num.items():
        data.append([int(data_str.split('-')[0]), int(data_str.split('-')[1]), freq])
    scatter_two(data, '', xlabel='Total commits', ylabel='Bug commits', save_file='results/CommitBugNumDist', scale=_loglog)
    plt.clf()
    hist, bin_edges=hist_data(bug_per_commit_list, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    hist, bin_edges=hist_data(bug_per_commit_list, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    plt.xlabel('Bug/Commits')
    plt.ylabel('Probability')
    plt.legend(['CCDF', 'PDF'])
    plt.savefig('results/BugPerCommitDist.png', dpi=500)

    plt.clf()
    user_bug_list=[len(bug_list) for bug_list in user_bug.values()]
    hist, bin_edges=hist_data(user_bug_list, N=max(user_bug_list)-min(user_bug_list)+1, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    hist, bin_edges=hist_data(user_bug_list, N=max(user_bug_list)-min(user_bug_list)+1, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    plt.xlabel('Number of bug a developer introduces')
    plt.ylabel('Probability')
    plt.legend(['CCDF', 'PDF'])
    plt.savefig('results/UserBugIntroducingDist.png', dpi=500)

    plt.clf()
    user_fixing_list=[len(bug_list) for bug_list in user_fixing_bug.values()]
    hist, bin_edges=hist_data(user_fixing_list, N=max(user_fixing_list)-min(user_fixing_list)+1, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    hist, bin_edges=hist_data(user_fixing_list, N=max(user_fixing_list)-min(user_fixing_list)+1, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    plt.xlabel('Number of bug a developer fixes')
    plt.ylabel('Probability')
    plt.legend(['CCDF', 'PDF'])
    plt.savefig('results/UserBugFixingDist.png', dpi=500)

    watcher_bug_stat(user_bug, user_commit_num)

if __name__=='__main__':
    bug_per_commit()
    cursor.close()
    mySqlDB.close()
    con.close()
