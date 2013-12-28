#!~/usr/bin/python
import urllib2
import os, sys
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
import json
import Queue
import random
from crawling_github import Repository
import logging
import datetime
import threadpool
import multiprocessing
from multiprocessing import Pool as ProcessPool

# crawling all commits of a repository

poolsize=40

(_multi_thread, _multi_process)=range(2)



# whether it return 404 or not
def page_has_response(url):
    try:
        req=urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        return False
    return True

# find the last page of prefix_url?page=N
# return N
def test_last_page(prefix_url):
    start=1
    end=150
    mid=(start+end)/2
    while(mid!=start and mid!=end):
        if page_has_response(prefix_url+'?page='+str(mid)):
            start=mid
        else:
            end=mid
        mid=(start+end)/2
    return mid

class Branch:
    def __init__(self, href):
        self.href=href
        self.branch_name=self.href.split('/')[-1]
        self.repos=Repository('/'.join(self.href.split('/')[:3]))
        self.commit_url='/'.join([self.repos.href, 'commits', self.branch_name])
    def __hash__(self):
        return self.branch_name.__hash__()

    def __cmp__(self, obj):
        return cmp(self.branch_name, obj.branch_name)

    def __str__(self):
        return str(self.href)

    __repr__=__str__

class Commit:
    def __init__(self, href='', date=datetime.datetime(2001, 1, 1)):
        self.href=href
        if len(href)>0:
            self.commit_sha=self.href.split('/')[-1]
            self.repos=Repository('/'.join(self.href.split('/')[:3]))
        else:
            self.commit_sha=''
        self.commit_date=date
        self.baseURL='https://github.com'
        self.parent_sha=''
        self.parent_sha_list=[]

    def __hash__(self):
        return self.commit_sha.__hash__()

    def __cmp__(self, obj):
        return cmp(self.commit_sha, obj.commit_sha)

    def __str__(self):
        return str(self.href)

    __repr__=__str__

    def find_change_files(self, ext):
        # finding the changing files (delete, adding) of current commit
        req=urllib2.urlopen(self.baseURL+self.href)
#       print self.baseURL+self.href
        result=req.read()
        soup=BeautifulSoup(result)
        file_list=[]
#        for d in soup.div():
#            print d.attrs().keys()
#            if d.has_attr('class') and d.has_attr('data-path') and d['class']=='meta':
        for d in soup.findAll('div', attrs={'class':'meta'}):
                if d.has_attr('data-path'):
                   if d['data-path'].endswith(ext):
                       file_list.append(d['data-path'])
        return file_list

    def parse_parent_info(self):
        # crawling the parent commit of current commit
        req=urllib2.urlopen(self.baseURL+self.href)
        result=req.read()
        soup=BeautifulSoup(result)
        for d in soup.div():
            if d.has_attr('class') and 'commit-meta' in d['class'] and 'clearfix' in d['class']:
                for s in d.findAll('span'):
                    for a in s.findAll('a'):
                        if a.has_attr('data-hotkey'):
                            self.parent_sha_list.append(a['href'].strip().split('/')[-1])
#                            self.parent_sha=a['href'].strip().split('/')[-1]
                
                

class DeepCrawler:
    #crawling all commits of a specified repository
    def __init__(self, repos, saveDir, log_name=''):
        self.target_repos=repos
        self.saveDir=saveDir
        self.baseURL='https://github.com'
        self.visited_commit=set()
        if not os.path.isdir(saveDir):
            os.mkdir(saveDir)

        if not os.path.isdir(os.path.join(saveDir, self.target_repos.repos_name)):
            os.mkdir(os.path.join(saveDir, self.target_repos.repos_name))


        if not os.path.isdir(os.path.join(saveDir, self.target_repos.repos_name, 'previous_commits')):
            os.mkdir(os.path.join(saveDir, self.target_repos.repos_name, 'previous_commits'))
        
        if not os.path.isdir(os.path.join(saveDir, self.target_repos.repos_name, 'logs')):
            os.mkdir(os.path.join(saveDir, self.target_repos.repos_name, 'logs'))
        
        if not os.path.isdir(os.path.join(saveDir, self.target_repos.repos_name, 'branches')):
            os.mkdir(os.path.join(saveDir, self.target_repos.repos_name, 'branches'))
        
        if os.path.isdir(os.path.join(self.saveDir, self.target_repos.repos_name, 'latest')):
            print 'Delete'
            os.system(' '.join(['rm', '-rf', os.path.join(self.saveDir, self.target_repos.repos_name, 'latest')]))
        
        os.mkdir(os.path.join(saveDir, self.target_repos.repos_name, 'latest'))

        os.system(' '.join(['git', 'clone', self.baseURL+self.target_repos.href, os.path.join(self.saveDir, self.target_repos.repos_name, 'latest')]))
        if len(log_name)>0:
            logging.basicConfig(filename=os.path.join(saveDir, self.target_repos.repos_name, log_name), level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
            self.logger=logging.getLogger('Crawler_'+self.target_repos.repos_name)
            self.logger.info('Cloning %s' % self.target_repos.repos_name)

    def start_crawling(self, multi_way=_multi_process):
#        self.branch_commit_fp=open(os.path.join(self.saveDir, self.target_repos.repos_name, 'branch_commit.info'), 'w')
        self.parse_branch_name()
        print 'Number of branches:%s' % len(self.branches)


        ######################################################################################
        ##########
        ##########      implementing crawler with the third part package 'threadpool', which is not truly multi-thread
        ##########
        if multi_way==_multi_thread:
            para=[((b, self.baseURL, os.path.join(self.saveDir, self.target_repos.repos_name),), {}) for b in self.branches[:poolsize]]
            pool=threadpool.ThreadPool(poolsize)
            requests=threadpool.makeRequests(crawling_branch, para)

            for req in requests:
                pool.putRequest(req)
            pool.wait()
        #######################################################################################

        #######################################################################################
        ##########
        ##########      truly multi-process implementation
        else:
            pool=ProcessPool(poolsize)
#            para=[(b, self.baseURL, os.path.join(self.saveDir, self.target_repos.repos_name),) for b in self.branches[:poolsize]]
            for b in self.branches:
                sys.stderr.write('Branch %s\n' % b.branch_name)
                pool.apply_async(crawling_branch, (b, self.baseURL, os.path.join(self.saveDir, self.target_repos.repos_name),))
            pool.close()
            pool.join()
            sys.stderr.write('All processes has been terminated\n')
        ##########
        ##########
        #######################################################################################

#        for branch in self.branches:
#            self.parse_commit(branch)

#        self.branch_commit_fp.close()

    def parse_branch_name(self):
        self.branches=[]
        try:
#            print self.baseURL+self.target_repos.href
            req=urllib2.urlopen(self.baseURL+self.target_repos.href)
            result=req.read()
            soup=BeautifulSoup(result)
            for d in soup.div():
                if d.has_attr('class') and 'select-menu-list' in d.attrs['class'] and d.has_attr('data-tab-filter') and d['data-tab-filter']=='branches':
                    for item in d.div():
                        if item.has_attr('class') and 'select-menu-item' in item.attrs['class']:
                            branch=Branch(item.a['href'])
                            self.branches.append(branch)
                            self.logger.info('Branch %s' % branch.branch_name)
        except urllib2.HTTPError, e:
            print e

    def parse_specified_commits_parent(self, commits_list):
        pool=ProcessPool(poolsize)
        for commit_sha in commits_list:
            commit=Commit(os.path.join(self.target_repos.href, 'commit', commit_sha))
            pool.apply_async(parsing_parent_info, (commit,))
        pool.close()
        pool.join()
        sys.stderr.write('All processes has been terminated\n')

    def parse_commit(self, branch):
        N=test_last_page(self.baseURL+branch.commit_url)
        print 'Branch: %s' % branch.branch_name
        print 'Total pages:%s' % N
        for i in range(N, 0, -1):
            try:
                req=urllib2.urlopen(self.baseURL+branch.commit_url+'?page='+str(i))
                result=req.read()
                soup=BeautifulSoup(result)
                commit_list=[]
                for d in soup.div():
                    if d.has_attr('class') and 'js-navigation-container' in d.attrs['class']:
                        h3_list=d.findAll('h3')
                        ol_list=d.findAll('ol')
                        if len(h3_list)==len(ol_list):
                            for index in range(len(h3_list)):
                                h3_date=datetime.datetime.strptime(h3_list[index].string, '%b %d, %Y').date()
                                for li in ol_list[index].findAll('li'):
                                    commit=Commit(li.p.a['href'], h3_date)
                                    commit.parse_parent_info()
                                    sys.stderr.write('Parent info %s\n' % '\t'.join(commit.parent_sha_list))
                                    commit_list.append(commit)
                        else:
                            print 'Error! h3 and ol do not match!'
                commit_list.reverse()
                for commit in commit_list:
#                    self.branch_commit_fp.write('%s %s %s %s\n' % (branch.branch_name, commit.commit_sha, commit.commit_date.strftime('%m/%d/%Y'), '\t'.join(commit.parent_sha_list)))
                    self.logger.info('Commit:%s (%s) in Branch:%s Parent:%s' % (commit.commit_sha, commit.commit_date.strftime('%m/%d/%Y'), branch.branch_name, '\t'.join(commit.parent_sha_list)))
                    if commit not in self.visited_commit:
#                        self.retrieve_commit(commit)
                        self.visited_commit.add(commit)
            except urllib2.HTTPError, e:
                print e
        print 'Number of commits until branch %s: %s' % (branch.branch_name, len(self.visited_commit))

    def retrieve_commit(self, commit):
#        print commit
        self.logger.info('Checkout %s' % commit.commit_sha)
        os.system(' '.join(['./retrieve_commit.sh', os.path.join(self.saveDir, self.target_repos.repos_name, 'latest'), commit.commit_sha]))


def parsing_parent_info(commit):
    commit.parse_parent_info()
    logger=logging.getLogger('ParentInfo')
    for sha in commit.parent_sha_list:
        logger.info('%s -> %s' % (sha, commit.commit_sha))

def crawling_branch(branch, baseURL, local_repos_dir):
    sys.stderr.write('%s %s %s\n' % (branch.branch_name, baseURL, local_repos_dir))
    logging.basicConfig(filename='crawler-threadpool.log', level = logging.DEBUG, format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    logger=logging.getLogger('-'.join(['Branch', branch.branch_name]))

    if os.path.isdir(os.path.join(local_repos_dir, 'branches', branch.branch_name)):
        os.system(' '.join(['rm', '-rf', os.path.join(local_repos_dir, 'branches', branch.branch_name)]))

    os.mkdir(os.path.join(local_repos_dir, 'branches', branch.branch_name))
    os.system(' '.join(['git', 'clone', '-b', branch.branch_name, baseURL+branch.repos.href, os.path.join(local_repos_dir, 'branches', branch.branch_name)]))

    N=test_last_page(baseURL+branch.commit_url)
    fp=open(os.path.join(local_repos_dir, 'logs', branch.branch_name), 'w')
    logger.info('Total pages:%s' % N)
    for i in range(N, 0, -1):
        try:
            req=urllib2.urlopen(baseURL+branch.commit_url+'?page='+str(i))
            result=req.read()
            soup=BeautifulSoup(result)
            commit_list=[]
            for d in soup.div():
                if d.has_attr('class') and 'js-navigation-container' in d.attrs['class']:
                    h3_list=d.findAll('h3')
                    ol_list=d.findAll('ol')
                    if len(h3_list)==len(ol_list):
                        for index in range(len(h3_list)):
                            h3_date=datetime.datetime.strptime(h3_list[index].string, '%b %d, %Y').date()
                            for li in ol_list[index].findAll('li'):
                                commit=Commit(li.p.a['href'], h3_date)
                                commit.parse_parent_info()
                                sys.stderr.write('Parent info %s\n' % '\t'.join(commit.parent_sha_list))
                                commit_list.append(commit)
                    else:
                        print 'Error! h3 and ol do not match!'
            commit_list.reverse()
            for commit in commit_list:
                fp.write('%s %s %s %s\n' % (branch.branch_name, commit.commit_sha, commit.commit_date.strftime('%m/%d/%Y'), '\t'.join(commit.parent_sha_list)))
                logger.info('Commit:%s (%s) in Branch:%s Parent:%s' % (commit.commit_sha, commit.commit_date.strftime('%m/%d/%Y'), branch.branch_name, '\t'.join(commit.parent_sha_list)))
#                if not os.path.isdir(os.path.join(local_repos_dir, 'previous_commits', commit.commit_sha)):
#                    os.mkdir(os.path.join(local_repos_dir, 'previous_commits', commit.commit_sha))
#                clone_commit(commit, os.path.join(local_repos_dir, 'branches', branch.branch_name))
        except urllib2.HTTPError, e:
            print e
    fp.close()

def clone_commit(commit, branch_dir):
    os.system(' '.join(['./retrieve_commit.sh', branch_dir, commit.commit_sha, '../']))


def crawling_specified_commit(repos_url, saveDir, commit_sha):
    '''
        Crawling specified commits directly
    '''
    if not os.path.isdir(saveDir):
        os.mkdir(saveDir)
    if os.path.isdir(os.path.join(saveDir, commit_sha)):
        os.system(' '.join(['rm', '-rf', os.path.join(saveDir, commit_sha)]))
    os.mkdir(os.path.join(saveDir, commit_sha))
    sys.stderr.write('Cloning %s\n' % commit_sha)
    os.system(' '.join(['git', 'clone', repos_url, os.path.join(saveDir, commit_sha)]))
    os.system(' '.join(['./retrieve_commit.sh', os.path.join(saveDir, commit_sha), commit_sha, 'null', 'null']))

def crawling_commits_directly(repos, save_dir, all_commit_file):
    '''
        all_commit_file is the file storing all commits' sha in the first column
    '''
#    done_commit=set()
#    for line in sys.stdin:
#        done_commit.add(line.strip())
    fp=open(all_commit_file)
    pool=ProcessPool(poolsize)
#    print 'https://github.com'+repos.href
    for line in fp.readlines():
        items=line.strip().split()
#        if len(items[0])>30 and items[0] not in done_commit:
#            print items[0]
        pool.apply_async(crawling_specified_commit, ('https://github.com'+repos.href, os.path.join(save_dir, 'previous_commits'), items[0], ))
#            crawling_specified_commit('https://github.com/voldemort/voldemort', 'tmp_commits', items[0])
    pool.close()
    pool.join()
    fp.close()
    sys.stderr.write('All processes has been terminated\n')

if __name__=='__main__':
#    repos=Repository('/voldemort/voldemort')
#    repos=Repository('/nathanmarz/storm')
#    repos=Repository('/elasticsearch/elasticsearch')
    repos=Repository('/facebook/presto')
    save_dir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'
#    deepCrawler=DeepCrawler(repos, '/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version', 'crawler-'+repos.repos_name+'.log')
#    deepCrawler.start_crawling(_multi_process)
#    deepCrawler=DeepCrawler(repos, '/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/thread_pool')
    crawling_commits_directly(repos, os.path.join(save_dir, repos.repos_name), os.path.join(save_dir, repos.repos_name, 'all_commits'))

#    sha_list=[]
#    for line in sys.stdin:
#        if len(line.strip())>0:
#            sha_list.append(line.strip())
#    sys.stderr.write('Number of commits is %s\n' % len(sha_list))
#    drepos=Repository('/voldemort/voldemort')eepCrawler.parse_specified_commits_parent(sha_list)

#    print 'Total number of commits:%s' % len(deepCrawler.visited_commit)
