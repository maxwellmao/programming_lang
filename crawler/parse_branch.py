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

    def add_commit(self, last_commit_sha, new_commit_sha, branch_name, new_commit_date):
        # construct the commit, the direction in the tree will be the parent-child relationship
        # last_commit_sha is the parent commit, new_commit_sha is the child commit
        new_commit=Commit(os.path.join(self.repository.href, 'commit', new_commit_sha), datetime.datetime.strptime(new_commit_date, '%m/%d/%Y'))
        new_id=self.commit_id_map.get(new_commit_sha, len(self.commit_id_map))
        if new_id==len(self.commit_id_map):
            self.commit_id_map[new_commit_sha]=new_id
            self.id_commit_map[new_id]=new_commit
        branch_set=self.commit_branch_map.get(new_commit_sha, set())
        branch_set.update([branch_name])
        self.commit_branch_map[new_commit_sha]=branch_set
        self.commit_tree.add_node(new_id)
        if len(last_commit_sha)!=0:
            last_id=self.commit_id_map.get(last_commit_sha, len(self.commit_id_map))
            if last_id==len(self.commit_id_map):
                self.commit_id_map[last_commit_sha]=last_id
                last_commit=Commit(os.path.join(self.repository.href, 'commit', last_commit_sha), datetime.datetime.strptime(new_commit_date, '%m/%d/%Y'))
                self.id_commit_map[last_id]=last_commit
            self.commit_tree.add_edge(last_id, new_id)

#            last_id=self.commit_id_map.get(last_commit_sha, -1)
#            if last_id==-1:
#                print 'Error! Last commit does not exsit!'
#                return           
#            else:
#                self.commit_tree.add_edge(last_id, new_id)

    def expand_dfs(self, node, all_corpus, program_corpus):
        for child in self.commit_tree[node]:
#            commit=Commit(os.path.join(self.repository.href, 'commit', self.id_commit_map[child]))
            proj_stat=ProjectStat(os.path.join(self.saveDir,self.repository.repos_name), 'java', 'java')
            proj_stat.all_corpus=dict(all_corpus)
            proj_stat.program_corpus=dict(program_corpus)
            commit=self.id_commit_map[child]
            commit_stat=proj_stat.incremental_parse(self.id_commit_map[node], commit)
            print commit_stat
            self.expand_dfs(child, proj_stat.all_corpus, proj_stat.program_corpus)


# use loop to dfs instead of recursion, since Python has contraints on # the maximun of recursions
    def expand_dfs_loop(self, node, all_corpus, program_corpus):
        root_proj_stat=ProjectStat(os.path.join(self.saveDir, self.repository.repos_name), 'java', 'java')
        null_commit=Commit()
        # the element of expand_stack is tuple
        # which in format of [ProjectStat, node id, last commit]
        expand_stack=[[root_proj_stat, node, null_commit]]
        while len(expand_stack)>0:
            item=expand_stack.pop()
            commit_stat=item[0].incremental_parse(item[-1], self.id_commit_map[item[1]])
            print commit_stat
            for child in self.commit_tree[item[1]]:
                proj_stat=ProjectStat(os.path.join(self.saveDir, self.repository.repos_name), 'java', 'java')
                proj_stat.all_corpus=dict(item[0].all_corpus)
                proj_stat.program_corpus=dict(item[0].program_corpus)
                expand_stack.append([proj_stat, child, self.id_commit_map[item[1]]])
        

    def expand_tree(self):
        root=filter(lambda x:self.commit_tree.in_degree(x)==0, self.commit_tree.nodes())
        for r in root:
            commit=self.id_commit_map[r]
            null_commit=Commit()
            proj_stat=ProjectStat(os.path.join(self.saveDir, self.repository.repos_name), 'java', 'java')
            self.expand_dfs_loop(r, proj_stat.all_corpus, proj_stat.program_corpus)
        
    def save_tree(self, saveDir):
        
        nx.write_edgelist(self.commit_tree, os.path.join(saveDir, 'EdgeList.nx'))
        fp=open(os.path.join(saveDir, 'NodeID'), 'w')
        fp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in self.commit_id_map.items()]))
        fp.close()
        
        fp=open(os.path.join(saveDir, 'CommitBranch'), 'w')
        fp.write('\n'.join(['\t'.join([str(k), '\t'.join(v)]) for k, v in self.commit_branch_map.items()]))
        fp.close()

    def load_tree(self, loadDir):
        self.commit_tree=nx.read_edgelist(os.path.join(loadDir, 'EdgeList.nx'))
        fp=open(os.path.join(loadDir, 'NodeID'))
        self.commit_id_map=dict()
        for line in fp.readlines():
            item=line.strip().split()
            self.commit_id_map[item[0]]=int(item[1])
        fp.close()
        self.commit_branch_map=dict()
        fp=open(os.path.join(loadDir, 'CommitBranch'))
        for line in fp.readlines():
            item=line.strip().split()
            self.commit_branch_map[item[0]]=set(item[1:])
        fp.close()

    def find_branch_latest_commit(self, branch):
        pass

    def find_leaves_in_repository(self):
        leaves=filter(lambda x:self.commit_tree.out_degree(x)==0, self.commit_tree.nodes())
        for leaf in leaves:
            print self.id_commit_map[leaf].commit_sha, self.commit_branch_map[self.id_commit_map[leaf].commit_sha]
        return leaves
        pass

class BranchParser:
    def __init__(self, repos, saveDir):
        self.repository=repos
        self.saveDir=saveDir
        self.commit_tree=CommitTree(self.repository, self.saveDir)
    
    def parsing_log(self):
        log_path=os.path.join(self.saveDir, self.repository.repos_name, 'branch_commit.info')
        last_branch=''
        last_sha=''
        last_date=datetime.datetime.now()
        fp=open(log_path)
        for line in fp.readlines():
            items=line.strip().split()
            if len(items)==4:
                self.commit_tree.add_commit(items[-1], items[1], items[0])
            else:
                self.commit_tree.add_commit('', items[1], items[0])
        fp.close()
        print 'Commit Tree construction completed!'
        print 'Number of nodes is %s' % len(self.commit_tree.commit_tree.nodes())
        print 'Number of edges is %s' % len(self.commit_tree.commit_tree.edges())

    def parsing_log_from_stdin(self):
        for line in sys.stdin:
            items=line.strip().split()
            if len(items)==4:
                self.commit_tree.add_commit(items[-1], items[1], items[0], items[2])
            else:
                self.commit_tree.add_commit('', items[1], items[0], items[2])
        print 'Commit Tree construction completed'
        print 'Number of nodes if %s' % len(self.commit_tree.commit_tree.nodes())
        print 'Number of edges is %s' % len(self.commit_tree.commit_tree.edges())

    def show_heaps_law(self, result_path, save_path):
        fp=open(result_path)
        x_all=[]
        y_all=[]
        x_program=[]
        y_program=[]
        for line in fp.readlines():
            items=line.strip().split()
            if len(items)==4 and items[0].isdigit():
                x_all.append(int(items[0]))
                y_all.append(int(items[1]))
                x_program.append(int(items[2]))
                y_program.append(int(items[3]))
        fp.close()
        plt.clf()
        plt.loglog(x_all, y_all, '.', color='b')
        plt.loglog(x_program, y_program, '.', color='r')
        plt.xlabel('Number of unique tokens')
        plt.ylabel('Number of appearing tokens')
        plt.legend(['All',  'Program'])
        plt.savefig(save_path+'.png', dpi=500)

if __name__=='__main__':
    repos=Repository('/voldemort/voldemort')
    repos_save_dir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'
    branchParser=BranchParser(repos, repos_save_dir)
#    branchParser.parsing_log()
    branchParser.parsing_log_from_stdin()
#    branchParser.commit_tree.save_tree('./')
#    branchParser.commit_tree.load_tree('./')
    print len(branchParser.commit_tree.find_leaves_in_repository())
#    branchParser.commit_tree.expand_tree()
#    branchParser.show_heaps_law('result', 'heap_law')
