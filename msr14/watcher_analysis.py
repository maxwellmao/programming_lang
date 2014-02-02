#!/usr/bin/python
from __future__ import division
import MySQLdb
import os, sys
from msr_db import hist_data
import matplotlib.pyplot as plt
from msr_db import _pdf, _ccdf
from fork_info import construct_fork_tree
from fork_info import assign_fork_to_repos
from two_d_histogram import scatter_two
from two_d_histogram import _loglog, _normal
from user_info import get_user_id_info

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

(_ByRepo, _ByProj, _ByNum)=range(3)

def unique_project(id_list, fork_repo_map, unique_type=_ByRepo):
    if unique_type==_ByProj:
        return set(id_list)
    elif unique_type==_ByRepo:
        repo_set=set()
        for id in id_list:
            repo_set.add(fork_repo_map[id])
        return repo_set
    elif unique_type==_ByNum:
        return id_list

def contribution_watch_dist():
    '''
        find the correlation between number of contributions and watches for developers
    '''
    user_id_info=get_user_id_info()
    fork_tree=construct_fork_tree()
    repo_forks_map, fork_repo_map=assign_fork_to_repos(fork_tree)
    developer_contribution={}
    developer_watch={}
    developer_watch_but_not_contribute={}
    sql='select committer_id, project_id from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        proj_id=developer_contribution.get(r[0], [])
        proj_id.append(r[1])
        developer_contribution[r[0]]=proj_id
    sql='select user_id, repo_id from watchers'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        proj_id=developer_watch.get(r[0], [])
        proj_id.append(r[1])
        developer_watch[r[0]]=proj_id
    uniq_type=_ByNum
    data_dict={}
    for user_id in set(developer_contribution.keys()).intersection(set(developer_watch.keys())):
        contribution_set=unique_project(developer_contribution[user_id], fork_repo_map, uniq_type)
        watch_set=unique_project(developer_watch[user_id], fork_repo_map, uniq_type)
        data_str='%s-%s' % (len(contribution_set), len(watch_set))
        data_dict[data_str]=data_dict.get(data_str, 0)+1
        developer_watch_but_not_contribute[user_id]=len(set(watch_set)-set(contribution_set))
        if developer_watch_but_not_contribute[user_id]>10:
            print user_id_info[user_id]
    data=[]
#    print '\n'.join(['%s %s' % (item[0], item[1]) for item in sorted(data_dict.items(), key=lambda x:x[1])])
    for data_str, freq in data_dict.items():
        data.append([int(data_str.split('-')[0]), int(data_str.split('-')[1]), freq])
    scatter_two(data, '', xlabel='Contribution', ylabel='watches', save_file='results/ContributionByCommitWatcher', scale=_loglog)
    watch_not_contribute=developer_watch_but_not_contribute.values()
    hist, bin_edge=hist_data(watch_not_contribute, N=max(watch_not_contribute)-min(watch_not_contribute)+1, type=_pdf)
    plt.clf()
    plt.plot(bin_edge[:-1], hist, '.')
    plt.xlabel('Watching but not contributing')
    plt.ylabel('Probability')
    plt.savefig('results/WatchingNotContributing.png', dpi=500)


if __name__=='__main__':
#    contributor_repos_dist()
#    watcher_repos_dist()
#    repo_watchers_dist()
    contribution_watch_dist()
    cursor.close()
    db.close()
