#!~/usr/bin/python
import os, sys
sys.path.append('..')
import random
from crawling_github import Repository
import logging
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from stat_repository import ProjectStat
from deep_crawling import Commit

class CommitTree:
    def __init__(self, repos, saveDir):
        self.commit_tree=nx.DiGraph()
        # recording the map between the commit_sha and the id of it in the ree
        self.commit_id_map=dict()
        # recording the map between the commit_sha and the set of branches it belongs to
        self.id_commit_map=dict()
        self.commit_branch_map=dict()
        self.repository=repos
        self.saveDir=saveDir
        self.proj_stat=ProjectStat(self.saveDir, 'java', 'java')

    def add_commit(self, last_commit_sha, new_commit_sha, branch_name):
        new_id=self.commit_id_map.get(new_commit_sha, len(self.commit_id_map))
        if new_id==len(self.commit_id_map):
            self.commit_id_map[new_commit_sha]=new_id
            self.id_commit_map[new_id]=new_commit_sha
        branch_set=self.commit_branch_map.get(new_commit_sha, set())
        branch_set.update(branch_name)
        self.commit_branch_map[new_commit_sha]=branch_set
        self.commit_tree.add_node(new_id)
        if len(last_commit_sha)!=0:
            last_id=self.commit_id_map.get(last_commit_sha, len(self.commit_id_map))
            if last_id==len(self.commit_id_map):
                self.commit_id_map[new_commit_sha]=new_id
                self.id_commit_map[last_id]=last_commit_sha
            self.commit_tree.add_edge(last_id, new_id)

#            last_id=self.commit_id_map.get(last_commit_sha, -1)
#            if last_id==-1:
#                print 'Error! Last commit does not exsit!'
#                return           
#            else:
#                self.commit_tree.add_edge(last_id, new_id)

    def expand_dfs(self, node):
        for child in self.commit_tree[node]:
            commit=Commit(os.path.join(self.repository.href, 'commit', self.id_commit_map[child]))
            commit_stat=self.proj_stat.incremental_parse(self.id_commit_map[node], commit)
            print commit_stat
            self.expand_dfs(child)


    def expand_tree(self):
        root=filter(lambda x:self.commit_tree.in_degree(x)==0, self.commit_tree.nodes())
        print '\n'.join([self.id_commit_map[id] for id in root])
#        print 'In degree of inital import is', self.commit_tree.in_degree(self.commit_id_map['fbd0f95d62ac2c5e97e5a4df5a732e9342d60da1'])
        if len(root)!=1:
            print 'Error! Should be only one root!'
            return
        root=root[0]
        print self.id_commit_map[root]
#        root_commit=Commit(os.path.join(self.repository.href, 'commit', self.id_commit_map[root]), '')
#        commit_stat=self.proj_stat.incremental_parse('', root_commit)
#        print commit_stat
#        self.expand_dfs(root)
        
        
    def save_tree(self, saveDir):
        nx.write_edgelist(self.commit_tree, os.path.join(saveDir, 'EdgeList.nx'))
        fp=open(os.path.join(saveDir, 'NodeID'), 'w')
        fp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in self.commit_id_map.items()]))
        fp.close()
        
        fp=open(os.path.join(saveDir, 'CommitBranch'), 'w')
        fp.write('\n'.join(['\t'.join([str(k), '\t'.join(v)]) for k, v in self.commit_branch_map.items()]))
        fp.close()

    def load_tree(self, loadDir):
        self.commit_tree=nx.read_edgelist(os.path.join(saveDir, 'EdgeList.nx'))
        fp=open(os.path.join(saveDir, 'NodeID'))
        self.commit_id_map=dict()
        for line in fp.readlines():
            item=line.strip().split()
            self.commit_id_map[item[0]]=int(item[1])
        fp.close()
        self.commit_branch_map=dict()
        fp=open(os.path.join(saveDir, 'CommitBranch'))
        for line in fp.readlines():
            item=line.strip().split()
            self.commit_branch_map[item[0]]=set(item[1:])
        fp.close()

class BranchParser:
    def __init__(self, repos, saveDir):
        self.repository=repos
        self.saveDir=saveDir
        self.commit_tree=CommitTree(self.repository, self.saveDir)
    
    def parsing_log(self):
        log_path=os.path.join(self.saveDir, repos.repos_name, 'branch_commit.info')
        last_branch=''
        last_sha=''
        last_date=datetime.datetime.now()
        fp=open(log_path)
        for line in fp.readlines():
            items=line.strip().split()
#            current_date=datetime.datetime.strptime(items[2], '%m/%d/%Y')
            if len(items)==4:
                self.commit_tree.add_commit(items[-1], items[1], items[0])
            else:
                self.commit_tree.add_commit('', items[1], items[0])

#            if last_branch!=items[0]:
#                last_sha=''
#            current_date=datetime.datetime.strptime(items[-1], '%m/%d/%Y')
#            if len(last_sha)==0:
#                self.commit_tree.add_commit(last_sha, items[1], items[0])
#            else:
#                if current_date < last_date:
##                    print items[1], last_sha
#                    self.commit_tree.add_commit(items[1], last_sha, items[0])
#                else:
#                    self.commit_tree.add_commit(last_sha, items[1], items[0])
#                    
##            print 'Adding %s -> %s' % (last_sha, items[1])
#            last_branch=items[0]
#            last_sha=items[1]
#            last_date=current_date
        fp.close()
        print 'Commit Tree construction completed!'
        print 'Number of nodes is %s' % len(self.commit_tree.commit_tree.nodes())
        print 'Number of edges is %s' % len(self.commit_tree.commit_tree.edges())
        self.commit_tree.expand_tree()

if __name__=='__main__':
    repos=Repository('/voldemort/voldemort')
    repos_save_dir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'
    branchParser=BranchParser(repos, repos_save_dir)
    branchParser.parsing_log()
