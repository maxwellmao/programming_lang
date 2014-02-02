#!/usr/bin/python
from __future__ import division
import os, sys
import MySQLdb
from pymongo import Connection
import datetime
import networkx as nx
import Queue
'''
    construct the sequence of files users touches in every commit
'''


mySQLdb=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
cursor=mySQLdb.cursor()

con=Connection()
db=con.msr14
db.authenticate('msr14', 'msr14')

def constructing_whole_commits_tree(id_sha_map):
    commit_tree=nx.DiGraph()
    sql='select commit_id, parent_id from commit_parents'
    cursor.execute(sql)
    results=cursor.fetchall()
#    for r in results:
#        '''
#            edges are from child-commit to parent-commit
#        '''
#        commit_tree.add_edge(id_sha_map[r[0]], id_sha_map[r[1]])
    for commit in db.commits.find():
        for par in commit['parents']:
            if par is not None:
                commit_tree.add_edge(commit['sha'], par['sha'])
    print 'Number of commits: %s' % len(commit_tree)
    return commit_tree

def constructing_commit_tree_of_repo(repo_id, whole_commit_tree, sha_time_map):
    sql='select id, url, owner_id, name from projects where id=%s' % repo_id
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        repo_name=r[1].replace('https://api.github.com/repos/', '').replace('/', '_')
    print 'Repo name: %s' % repo_name
    commit_tree=nx.DiGraph()
    sql='select * from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    commit_sha_set=set()
    visited_sha_set=set()
    explore_sha_queue=Queue.Queue()
    for r in results:
        if r[4]==repo_id:
            commit_sha_set.add(r[1])
            commit_tree.add_node(r[1])
            explore_sha_queue.put(r[1])
    print 'Directly related commits: %s' % len(commit_sha_set)
    while not explore_sha_queue.empty():
        sha=explore_sha_queue.get()
        for parent in whole_commit_tree[sha]:
#            if sha_time_map.get(sha, datetime.datetime(1999,1,1))<sha_time_map.get(parent, datetime.datetime(1998,1,1)):
#                print 'Time error:', sha, sha_time_map[sha], parent, sha_time_map[parent]
            commit_tree.add_edge(parent, sha)
            if parent not in visited_sha_set:
                visited_sha_set.add(parent)
                explore_sha_queue.put(parent)
    print 'Total commits: %s' % len(commit_tree)
    fp=open('results/commit_tree/all-sha_%s' % repo_name, 'w')
#    for node in commit_tree:
#        if sha_time_map.has_key(node):
#            fp.write('\n'.join(['%s %s' % (str(node), sha_time_map[node].strftime('%Y-%m-%d')) for node in commit_tree]))#_%H:%M:%S
#        else:
#            print 'No time for %s' % node
    for edge in commit_tree.edges():
        fp.write('%s %s\n' % (edge[0], edge[1]))
    fp.close()

def construct_commit_tree_for_every_repo():
    sql='select id, sha, created_at from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    id_sha_map={}
    sha_time_map={}
    for r in results:
        id_sha_map[r[0]]=r[1]
        sha_time_map[r[1]]=r[2].date()
    whole_commit_tree=constructing_whole_commits_tree(id_sha_map)
    sql='select distinct repo_id from project_members'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        constructing_commit_tree_of_repo(r[0], whole_commit_tree, sha_time_map)

def user_file_network(info_file):
    id_author={}
    sql='select id, login from users'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        id_author[r[0]]=r[1]
    commit_author={}
    sql='select author_id, committer_id, sha from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        commit_author[r[2]]=r[0]
    
    print info_file
    fp=open(info_file)
    commit_sha={}
    for line in fp.readlines():
        item=line.strip().split()
        commit_sha[item[0]]=datetime.datetime.strptime(item[1], '%Y-%m-%d_%H:%M:%S')
    fp.close()
    fp=open(info_file+'-user_file-net', 'w')
    for item in sorted(commit_sha.items(), key=lambda x:x[1]):
        for result in db.commits.find({'sha':item[0]}):
            if commit_author.has_key(item[0]) and result.has_key('files'):
#                user=result['committer']['login']
                user=id_author[commit_author[item[0]]]
                for change_file in result['files']:
                    try:
                        fp.write('%s %s %s %s\n' % (item[0], user, change_file['filename'], item[1].strftime('%Y-%m-%d_%H:%M:%S')))
                    except:
                        print sys.exc_info()[0]
            else:
                print item[0], 'is None'
    fp.close()
    print 'Finish', info_file+'-user_file-net'

def parsing_repo_commits_info():
    dir='results/commit_tree'
    for file in os.listdir(dir):
        if not file.endswith('-user_file-net'):
            user_file_network(os.path.join(dir, file))

if __name__=='__main__':
    construct_commit_tree_for_every_repo()
#    parsing_repo_commits_info()
    cursor.close()
    mySQLdb.close()
