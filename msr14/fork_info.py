#!/usr/bin/python
from __future__ import division
import matplotlib.pyplot as plt
import networkx as nx
import MySQLdb
import sys, os
from label_analysis import project_member
from msr_db import hist_data
import Queue
from msr_db import _pdf, _ccdf

def assign_fork_to_repos(fork_tree):
    root_fork=filter(lambda x:fork_tree.in_degree(x)==0, fork_tree.nodes())
    repo_forks_map=dict()
    fork_repo_map=dict()
#    print 'Forks: %s' % len(fork_tree.nodes())
    for repo in root_fork:
        repo_forks_map[repo]=set()
        explore_Q=Queue.Queue()
        explore_Q.put([repo, 0])
        while not explore_Q.empty():
            item=explore_Q.get()
            node=item[0]
            fork_repo_map[node]=repo
            repo_forks_map[repo].add(node)
            for neighbor in fork_tree[node].keys():
                explore_Q.put([neighbor, item[1]+1])
#        print repo, item[1]
    print '\n'.join(['%s\t%s' % (k, v) for k, v in fork_repo_map.items()])
    return repo_forks_map, fork_repo_map

def construct_fork_tree():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM projects'
    cursor.execute(sql)
    results=cursor.fetchall()
    fork_tree=nx.DiGraph()
    proj_url_dict={}
    for r in results:
        proj_url_dict[r[0]]=r[1].replace('api.', '', 1).replace('repos/', '', 1)
        if r[8] is not None:
            fork_tree.add_edge(r[8], r[0])
        else:
            fork_tree.add_node(r[0])
    cursor.close()
    db.close()
    root_fork=filter(lambda x:fork_tree.in_degree(x)==0, fork_tree.nodes())
    print len(root_fork)
    fp=open('RepoURL', 'w')
    for repo in root_fork:
        fp.write('%s\n' % proj_url_dict[repo])
    fp.close()
#    print 'No. of root forks:%s' % len(root_fork)
    return fork_tree

def commits_distribution(fork_repo_map):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT author_id, committer_id, project_id, created_at FROM commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    repo_fork_commits=dict()
    for r in results:
        if fork_repo_map.has_key(r[2]):
            if repo_fork_commits.has_key(fork_repo_map[r[2]]):
                fork_commits=repo_fork_commits[fork_repo_map[r[2]]].get(r[2], [])
                fork_commits.append(r[3])
                repo_fork_commits[fork_repo_map[r[2]]][r[2]]=fork_commits
            else:
                repo_fork_commits[fork_repo_map[r[2]]]={r[2]:[r[3]]}
    cursor.close()
    db.close()
    fork_commit_num=[]
    repo_time_diff=dict()
    for repo, fork in repo_fork_commits.items():
        print repo, sum([len(c) for c in fork.values()])
        repo_time=[]
        for f, c in fork.items():
            repo_time+=c
            fork_commit_num.append(len(c))
        sorted_time=sorted(repo_time)
        time_diff=[]
        for index in range(len(sorted_time)-1):
            time_delta=sorted_time[index+1]-sorted_time[index]
            time_diff.append(time_delta.days*24*60+time_delta.seconds/60)
        repo_time_diff[repo]=time_diff
    hist, bin_center=hist_data(fork_commit_num, type=_pdf)
    plt.clf()
    plt.loglog(bin_center, hist)
    plt.xlabel('Commit number')
    plt.ylabel('Frequency')
    plt.savefig('ForkCommitNum.png', dpi=500)

    for repo, time in repo_time_diff.items():
        hist, bin_center=hist_data(time, type=_ccdf)
        plt.clf()
        plt.loglog(bin_center, hist)
        plt.xlabel('Time diff')
        plt.ylabel('Frequency')
        plt.savefig('repo_time/%s_time_diff.png' % repo, dpi=500)

def description(fork_repo_map):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM projects'
    cursor.execute(sql)
    results=cursor.fetchall()
    des=set()
    for r in results:
        if r[8] is not None:
            if r[4].strip().lower() not in des:
                print r[0], fork_repo_map[r[8]], r[1], r[4]
                des.add(r[4].strip().lower())
        else:
            print r[0], r[8], r[1], r[4]
            des.add(r[4].strip().lower())
    cursor.close()
    db.close()

#    fp=open('repo_time_diff', 'w')
#    fp.write('\n'.join([' '.join([str(t) for t in time]) for time in repo_time_diff.values()]))
#    fp.close()

def check_root_fork():
    proj_info, developer=project_member()
    fork_tree=construct_fork_tree()
    repo_forks_map, fork_repo_map=assign_fork_to_repos(fork_tree)
    fp=open('ForkRepoMap', 'w')
    fp.write('\n'.join(['%s\t%s' % (k,v) for k, v in fork_repo_map.items()]))
    fp.close()
#    description(fork_repo_map)
#    commits_distribution(fork_repo_map)
#    index=0
#    for root in root_fork:
#        if proj_info.has_key(root):
#            index+=1
#    print index

if __name__=='__main__':
#    construct_fork_tree()
    check_root_fork()
