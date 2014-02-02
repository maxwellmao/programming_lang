#/usr/bin/python
import networkx as nx
import MySQLdb
import sys, os
import matplotlib.pyplot as plt
from textblob import TextBlob
from fork_info import construct_fork_tree
from fork_info import assign_fork_to_repos
from msr_db import hist_data
from msr_db import _pdf, _ccdf

class Commit:
    def __init__(self, result):
        self.id=result[0]
        self.sha=result[1]
        self.author_id=result[2]
        self.committer_id=result[3]
        self.project_id=result[4]
        self.create_time=result[5]

    def __str__(self):
        return 'ID:%s SHA:%s Author:%s Committer:%s Project:%s Create:%s' % (self.id, self.sha, self.author_id, self.committer_id, self.project_id, self.create_time.strftime('%Y-%m-%d_%H:%M:%S'))

    __repr__=__str__

def construct_commit_tree():
    commit_info=dict()
    commit_tree=nx.Graph()
    db=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor=db.cursor()
    sql='select * from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        commit_info[r[0]]=Commit(r)

    sql='select commit_id, parent_id from commit_parents'
    cursor=db.cursor()
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        commit_tree.add_edge(r[0], r[1])
    cursor.close()
    db.close()
    print 'Number of commits: %s' % len(commit_tree)
    return commit_info, commit_tree

def save_commit_tree(commit_info, commit_tree):
    fp=open('CommitInfo', 'w')
    for e in commit_tree.edges():
        fp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in commit_info.items()]))
    fp.close()
    fp=open('CommitTree', 'w')
    for e in commit_tree.edges():
        fp.write('%s\t%s\n' % (e[0], e[1]))
    fp.close()

def sentiment_analysis(comment):
    blob = TextBlob(comment)
    polarity=[]
    for sentence in blob.sentences:
        p=sentence.sentiment.polarity
        polarity.append(p)
        if p<0:
            print sentence
    print polarity

def extract_commit_comments():
    db=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor=db.cursor()
    sql='select * from pull_request_comments'
    cursor.execute(sql)
    results=cursor.fetchall()
    commit_comment_dict=dict()
    line=0
    for r in results:
        comment=commit_comment_dict.get(int(r[5]), [])
        comment.append(r[4])
        line+=1
        commit_comment_dict[int(r[5])]=comment
        sentiment_analysis(r[4])
    sql='select * from commit_comments'
    cursor.execute(sql)
    results=cursor.fetchall()
    sys.stderr.write('%s\n' % line)
    line=0
    for r in results:
        line+=1
        comment=commit_comment_dict.get(int(r[1]), [])
        comment.append(r[3])
        commit_comment_dict[int(r[1])]=comment
        sentiment_analysis(r[3])
    sys.stderr.write('%s\n' % line)
    cursor.close()
    db.close()
#    print '\n'.join(['\n'.join(['Commit:%s\t%s' % (k,c) for c in v]) for k,v in commit_comment_dict.items()])
    sys.stderr.write('%s\n' % len(commit_comment_dict))

def project_commits():
    '''
    identifying the commits associated with more than one project
    '''
    db=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor=db.cursor()
    sql='select * from project_commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    commit_projs=dict()
    for r in results:
        commit_list=commit_projs.get(r[1], [])
        commit_list.append(r[0])
        commit_projs[r[1]]=commit_list
    for commit, projs in commit_projs.items():
        if len(projs)>1:
            print commit, projs
    cursor.close()
    db.close()

def get_all_commits():
    db=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor=db.cursor()
    sql='select id, url from projects'
    cursor.execute(sql)
    results=cursor.fetchall()
    proj_url=dict()
    for r in results:
        proj_url[r[0]]=r[1]
    sql='select * from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        if proj_url.has_key(r[4]):
#            print proj_url[r[0]], r[1]
            pass
        else:
            print 'No project matches'
    cursor.close()
    db.close()

def commit_arrival_time():
    fork_tree=construct_fork_tree()
    repo_forks_map, fork_repo_map=assign_fork_to_repos(fork_tree)
    db=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor=db.cursor()
    sql='select project_id, created_at from commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    repo_commit={}
    for r in results:
        commit_list=repo_commit.get(fork_repo_map[r[0]], [])
        commit_list.append(r[1])
        repo_commit[fork_repo_map[r[0]]]=commit_list
    if not os.path.isdir('commit_arrivals'):
        os.mkdir('commit_arrivals')
    for repo, commit_list in repo_commit.items():
        sorted_commit=sorted(commit_list)
        delta_time=[]
        for i in range(len(sorted_commit)-1):
            d_time=sorted_commit[i+1]-sorted_commit[i]
            delta_time.append(int(d_time.days*24+d_time.seconds/3600))
        plt.clf()
        hist, bin_edge=hist_data(delta_time, N=max(delta_time)-min(delta_time)+1, type=_ccdf)
        plt.loglog(bin_edge[:-1], hist, '.', color='b')
        hist, bin_edge=hist_data(delta_time, N=max(delta_time)-min(delta_time)+1, type=_pdf)
        plt.loglog(bin_edge[:-1], hist, '.', color='r')
        plt.xlabel('Interval between two arrivals')
        plt.ylabel('Probability')
        plt.savefig('commit_arrivals/%s_DeltaTimeDist.png' % repo, dpi=500)

if __name__=='__main__':
#    extract_commit_comments()
#    get_all_commits()
#    project_commits()
    commit_arrival_time()
