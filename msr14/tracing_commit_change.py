#!/usr/bin/python
import sys, os
sys.path.append('../crawler')
from deep_crawling import Commit
import datetime
from multiprocessing import Pool as ProcessPool
import logging

poolsize=40

def finding_change_file_with_list(proj_list, logger):
    for proj_info in proj_list:
        sha=proj_info[1]
        commit=Commit(proj_info[0].replace('https://github.com', '')+'/commit/'+sha)
        change, from_hide=commit.find_change_files_from_two('')
        if len(change)==0:
            logger.info('Proj:%s Commit:%s File:NotFound Hide:%s' % (proj_info[0].replace('https://github.com', ''), sha, from_hide))
        for file in change:
            if logger is not None:
                logger.info('Proj:%s Commit:%s File:%s Hide:%s' % (proj_info[0].replace('https://github.com', ''), sha, file, from_hide))
            else:
                print 'Commit:%s File:%s' % (sha, file)

def finding_change_file(proj_url, sha_list, logger):
    for sha in sha_list:
        commit=Commit(proj_url.replace('https://github.com', '')+'/commit/'+sha)
        change, from_hide=commit.find_change_files_from_two('')
        if len(change)==0:
            logger.info('Commit:%s File:NotFound' % sha)
        for file in change:
            if logger is not None:
                logger.info('Commit:%s File:%s' % (sha, file))
            else:
                print 'Commit:%s File:%s' % (sha, file)

def crawling_according_project(proj_commit_dict):
    pool=ProcessPool(poolsize)
    for repo, commits in proj_commit_dict.items():
#        print repo, commits
#        logger=logging.getLogger(proj.replace('https://github.com', ''))
        logger=logging.getLogger(repo)
        pool.apply_async(finding_change_file_with_list(commits, logger, ))
    pool.close()
    pool.join()

def read_project_repo_map():
    fp=open('ForkRepoMap')
    proj_repo_map=dict()
    for line in fp.readlines():
        item=line.strip().split()
        proj_repo_map[item[0]]=item[1]
    fp.close()
    return proj_repo_map

def crawling_commits(log_path=''):
    proj_repo_map=read_project_repo_map()
    proj_commit_dict=dict()
    repo_commit_dict=dict()
    if len(log_path)>0:
        fp=open(log_path)
#    for line in fp.readlines():
    for line in sys.stdin:
        item=line.strip().split()
#        commit_list=proj_commit_dict.get(item[2], [])
        commit_list=repo_commit_dict.get(proj_repo_map[item[2]], [])
        commit_list.append([item[3], item[4]])
#        proj_commit_dict[item[2]]=commit_list
        repo_commit_dict[proj_repo_map[item[2]]]=commit_list
    if len(log_path)>0:
        fp.close()
    crawling_according_project(repo_commit_dict)

if __name__=='__main__':
    saveDir='./'
    logging.basicConfig(filename=os.path.join(saveDir, 'crawling-msr_commit.log'), level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    crawling_commits()
#    create_time=datetime.datetime.strptime('2012-04-07_20:29:18', '%Y-%m-%d_%H:%M:%S')
#    finding_change_file('https://github.com/TTimo/doom3.gpl', 'fb1609f5540e3578b579c5e3476de5613c5d3a6', create_time)
#    finding_change_file('https://github.com/TTimo/doom3.gpl',['d5f751654da8729ca0f30287fad102a597858d77'], None)
