#!/usr/bin/python
from __future__ import division
import sys, os
import datetime
import pymongo
from pymongo import Connection
import codecs
import numpy as np
import matplotlib.pyplot as plt


changing_file_ext_dict={}
changing_file_dict={}
file_changes_per_commit=[]
commit_stat_dict={}
(_pdf, _ccdf)=range(2)

def hist_data(data_list, data_range=None, N=1000, type=_pdf):
    if data_range is None:
        data_range=(min(data_list), max(data_list)+1)
    bins=np.arange(data_range[0], data_range[1]+(data_range[1]-data_range[0])/N, (data_range[1]-data_range[0])/N)
    hist=[0 for i in range(len(bins)-1)]
    current_bin=0
    for item in sorted(data_list):
        while(item>bins[current_bin]) and current_bin<len(bins)-1:
            current_bin+=1
        if current_bin==0:
            hist[current_bin]+=1
        else:
            hist[current_bin-1]+=1
    bin_center=[(bins[i+1]+bins[i])/2 for i in range(len(bins)-1)]
    if type==_pdf:
        s=sum(hist)
        return [h/s for h in hist], bins
    else:
        cumulative=0
        ccdf_hist=[]
        for h in hist[::-1]:
            cumulative+=h
            ccdf_hist.append(cumulative)
        ccdf_hist.reverse()
        return [h/cumulative for h in ccdf_hist], bins

def read_project_repo_map():
    fp=open('ForkRepoMap')
    proj_repo_map=dict()
    for line in fp.readlines():
        item=line.strip().split()
        proj_repo_map[item[0]]=item[1]
    fp.close()
    return proj_repo_map

class CommitStats:
    def __init__(self, add_num, del_num):
        self.add_num=add_num
        self.del_num=del_num

    def __str__(self):
        return '%s-%s' % (self.add_num, self.del_num)

    __repr__=__str__

    def __hash__(self):
        return self.__str__().__hash__()

def filter_file_extension(file_name):
    ext=change_file['filename'].split('.')[-1]
    if ext.find('/')>0:
        ext=ext.split('/')[-1]
    ext_set=set(['php', 'rb', 'cpp', 'h', 'scala', 'java', 'py', 'js', 'cs', 'sql', 'c', 'cc', 'hpp', 'css', 'makefile', 'sh', 'r', 'bat', 'tex', 'coffee', 'pl', 'tcl', 'asm', 'm', 'aspx', 'go', 'lua', 'lisp', 'sed', 'awk', 'vb', 'bash', 'el', 'perl', 'asp'])
   

def change_file_stat(sha, sufix=''):
    for result in db.commits.find({'sha':sha}):
#        if len(sufix)==0:
        if result.has_key('files'):
            for change_file in result['files']:
                changing_file_dict[change_file['filename']]=changing_file_dict.get(change_file['filename'], 0)+1
                ext=change_file['filename'].split('.')[-1]
                if ext.find('/')>0:
                    ext=ext.split('/')[-1]
                changing_file_ext_dict[ext]=changing_file_ext_dict.get(ext, 0)+1
            file_changes_per_commit.append(len(result['files']))
            if len(result['files'])==0:
                print sha
        else:
            print 'No files:', result.keys(), sha
#     else:
        if result.has_key('stats'):
            cs=CommitStats(result['stats']['additions'], result['stats']['deletions'])
            commit_stat_dict[str(cs)]=commit_stat_dict.get(str(cs), 0)+1

def query_commits(sha):
    for result in db.commits.find({'sha':sha}):
        for change_file in result['files']:
            print change_file.keys()
            print change_file['filename']
#        print result

def project_level_stat():
    pass

def repo_level_stat():
    pass

def query_commits_of_project(sufix=''):
    '''
    get the information of repos-project-commits
    the format of proj_repo_map is {repo_id:[project_url, sha]}

    the CommitsURL should be as input from standard input
    '''
    proj_repo_map=read_project_repo_map()
    proj_commit_dict={}
    repo_commit_dict={}
    index=0
    for line in sys.stdin:
        item=line.strip().split()
        commit_list=repo_commit_dict.get(proj_repo_map[item[2]], [])
        commit_list.append([item[3], item[4]])
        repo_commit_dict[proj_repo_map[item[2]]]=commit_list
#        query_commits(item[4])
        change_file_stat(item[4], sufix)
        index+=1
        print index
#    print '\n'.join(['%s\t%s' % (k,v) for k,v in ext_dict.items()])
    if len(sufix)==0:
        fp=codecs.open('ChangingFile', 'w', 'utf-8')
        changing_file_list=sorted(changing_file_dict.items(), key=lambda x:x[1], reverse=True)
        fp.write('\n'.join(['%s\t%s' % (item[0], item[1]) for item in changing_file_list]))
        fp.close()
        fp=codecs.open('ChangingFileExt', 'w', 'utf-8')
        changing_file_ext_list=sorted(changing_file_ext_dict.items(), key=lambda x:x[1], reverse=True)
        fp.write('\n'.join(['%s\t%s' % (item[0], item[1]) for item in changing_file_ext_list]))
        fp.close()
    
        changing_num=changing_file_dict.values()
        hist, bin_edges=hist_data(changing_num, N=max(changing_num)-min(changing_num)+1, type=_ccdf)
        plt.loglog(bin_edges[:-1], hist, '.', color='b')
        hist, bin_edges=hist_data(changing_num, N=max(changing_num)-min(changing_num)+1, type=_pdf)
        plt.loglog(bin_edges[:-1], hist, '.', color='r')
        plt.xlabel('Number of times a file changed')
        plt.ylabel('Probability')
        plt.legend(['CCDF', 'PDF'])
        plt.savefig('FileChangingTimeDist.png', dpi=500)
    else:
        fp=open('CommitStats%s' % sufix, 'w')
        fp.write('\n'.join(['%s\t%s' % (str(k), v) for k, v in commit_stat_dict.items()]))
        fp.close()

def parse_pull_request_commits(commit_type=''):
#    commit_type='_NonBugCommit'
    for line in sys.stdin:
        item=line.strip().split()
        change_file_stat(item[-1])
    fp=codecs.open('ChangingFile%s' % commit_type, 'w', 'utf-8')
    changing_file_list=sorted(changing_file_dict.items(), key=lambda x:x[1], reverse=True)
    fp.write('\n'.join(['%s\t%s' % (item[0], item[1]) for item in changing_file_list]))
    fp.close()
    fp=codecs.open('ChangingFileExt%s' % commit_type, 'w', 'utf-8')
    changing_file_ext_list=sorted(changing_file_ext_dict.items(), key=lambda x:x[1], reverse=True)
    fp.write('\n'.join(['%s\t%s' % (item[0], item[1]) for item in changing_file_ext_list]))
    fp.close()
    
    changing_num=changing_file_dict.values()
    hist, bin_edges=hist_data(changing_num, N=max(changing_num)-min(changing_num)+1, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    hist, bin_edges=hist_data(changing_num, N=max(changing_num)-min(changing_num)+1, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    plt.xlabel('Number of times a file changed')
    plt.ylabel('Probability')
    plt.legend(['CCDF', 'PDF'])
    plt.savefig('FileChangingTimeDist%s.png' % commit_type, dpi=500)

    plt.clf()
    hist, bin_edges=hist_data(file_changes_per_commit, N=max(file_changes_per_commit)-min(file_changes_per_commit)+1, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    hist, bin_edges=hist_data(file_changes_per_commit, N=max(file_changes_per_commit)-min(file_changes_per_commit)+1, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    plt.xlabel('Number of changed files per commits')
    plt.ylabel('Probability')
    plt.legend(['CCDF', 'PDF'])
    plt.savefig('FileChangesPerCommitDist%s.png' % commit_type, dpi=500)
    

    fp=open('CommitStats%s' % commit_type, 'w')
    fp.write('\n'.join(['%s\t%s' % (str(k), v) for k, v in commit_stat_dict.items()]))
    fp.close()
    

if __name__=='__main__':
    con=Connection()
    db=con.msr14
    db.authenticate('msr14', 'msr14')
    if len(sys.argv)>1:
        parse_pull_request_commits(sys.argv[1])
    else:
        parse_pull_request_commits()
#    if len(sys.argv)>1:
#        query_commits_of_project(sys.argv[1])
#    else:
#        query_commits_of_project()
#    print db.commits.find({'commit':{'author':{'name':'Matthias Vallentin'}}}).count()
#    result=db.commits.find_one()
#    print type(result), len(result.keys()), len(result.values())
#    print len(result['files'][0])
#    print result['files'][0].keys()
#    print result
