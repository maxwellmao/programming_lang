#!/usr/bin/python
from __future__ import division
import MySQLdb
import os, sys
from msr_db import hist_data
import matplotlib.pyplot as plt
from msr_db import _pdf, _ccdf

db=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
cursor=db.cursor()

def contributor_repos_dist():
    '''
    the distribution of number of repos a contributor watches
    '''
    sql='select distinct committer_id from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    contributor=set()
    for r in results:
        contributor.add(r[0])
    sql='select user_id, count(distinct repo_id) from watchers group by user_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    contributor_repos_num=[]
    for r in results:
        if r[0] in contributor:
            contributor_repos_num.append(r[1])
    hist, bin_edge=hist_data(contributor_repos_num, N=max(contributor_repos_num)-min(contributor_repos_num)+1, type=_ccdf)
    plt.clf()
    plt.loglog(bin_edge[:-1], hist, '.')
    plt.xlabel('Number of repos a contributor watching')
    plt.ylabel('Probability')
    plt.savefig('ContributorReposDist.png', dpi=500)


def watcher_repos_dist():
    '''
    the distribution of number of repos a user watches
    '''
    sql='select count(distinct repo_id) from watchers group by user_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    watcher_repos_num=[]
    for r in results:
        watcher_repos_num.append(r[0])
    hist, bin_edge=hist_data(watcher_repos_num, N=max(watcher_repos_num)-min(watcher_repos_num)+1, type=_ccdf)
    plt.clf()
    plt.loglog(bin_edge[:-1], hist, '.')
    plt.xlabel('Number of repos a user watching')
    plt.ylabel('Probability')
    plt.savefig('WatcherReposDist.png', dpi=500)

def repo_watchers_dist():
    '''
    the distribution of number of users that watch the repo
    '''
    sql='select count(distinct user_id) from watchers group by repo_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    repo_watchers_num=[]
    for r in results:
        repo_watchers_num.append(r[0])
    hist, bin_edge=hist_data(repo_watchers_num, N=max(repo_watchers_num)-min(repo_watchers_num)+1, type=_pdf)
    plt.clf()
    plt.plot(bin_edge[:-1], hist, '.')
    plt.xlabel('Number of wathers in one repo')
    plt.ylabel('Probability')
    plt.savefig('RepoWatchersDist.png', dpi=500)

if __name__=='__main__':
    contributor_repos_dist()
    watcher_repos_dist()
    repo_watchers_dist()
