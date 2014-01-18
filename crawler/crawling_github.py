#!~/usr/bin/python
from __future__ import division
import urllib2
import os, sys
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
import json
import Queue
import random
import time
import logging
from multiprocessing import Pool as ProcessPool

poolsize=40

#HEADERS = { 'User-Agent' : 'Mozilla/5.0' }
HEADERS = 'Mozilla/5.0'
N=1000000
MAX_TRY_TIME=20

COOKIE=''
if os.path.isfile('cookie.log'):
    cookie_fp=open('cookie.log')
    COOKIE=cookie_fp.read().strip()
    cookie_fp.close()

baseURL='https://github.com'

def has_content(contents, num_name):
    for c in contents:
        if c.find(num_name)>-1:
            return True
    return False

def get_num(root_tag, num_name, attr_dict={}):
    num=0
    for li in root_tag.findAll('li'):
        if li.a['href'].find(num_name)>-1 or has_content(li.a.contents, num_name):
            for c in li.a.span.contents:
                for line in str(c).strip().split('\n'):
                    if line is not None and line.strip().replace(',', '').replace('+', '').isdigit():
                        num=line.replace(',', '')
#    if (num==0 or len(num)==0) and (num_name=='commits' or num_name=='contributors'):
#        print num, root_tag.findAll('li')
    return num

class Repository:
    def __init__(self, href):
        self.href=href
        self.user=''
        self.repos_name=''
        if len(href)>0:
            info=self.href.split('/')[1:]
            self.user=info[0]
            self.repos_name=info[1]
        self.commits=0
        self.releases=0
        self.contributors=0
        self.branches=0
        self.lang=''
        self.lang_percent=dict()
        self.watchers=0
        self.stargazers=0
        self.forks=0
        self.description=''

    def get_contributors(self):
        failure=True
        try_time=0
        while failure and try_time<MAX_TRY_TIME:
            try:
                req=urllib2.urlopen(baseURL+self.href+'/graphs/contributors-data')
                data=json.load(req)
                self.contributors=len(data)
                failure=False
            except Exception as e:
                try_time+=1
                print self.href, e

    def is_empty_info(self):
        return self.commits==0 and self.branches==0 and self.releases==0 and self.contributors==0 and self.watchers==0 and self.stargazers==0 and self.forks==0 and len(self.description)==0

    def __str__(self):
        return self.href

    __repr__=__str__

    def all_info_str(self):
        return 'href:%s, lang:%s, commits:%s, branches: %s, releases:%s, contributors:%s, watchers:%s, stargazers:%s, forks:%s\nLang:%s' % (self.href, self.lang, self.commits, self.branches, self.releases, self.contributors, self.watchers, self.stargazers, self.forks, ';'.join([('%s:%s' % (k,v)) for k, v in self.lang_percent.items()]))

    def get_from_db(self, record):
        self.href=record[0]
        if len(record[1])>0:
            for item in record[1].split(';'):
                self.lang_percent[item.split(':')[0]]=float(item.split(':')[1])
        self.commits=record[2]
        self.branches=record[3]
        self.releases=record[4]
        self.contributors=record[5]
        self.watchers=record[6]
        self.stargazers=record[7]
        self.forks=record[8]
        self.description=record[9]

    def __hash__(self):
        return self.__str__().__hash__()

    def __cmp__(self, obj):
        return cmp(str(self), str(obj))

    def set_lang(self, lang):
        self.lang=lang

    def set_commit_num(self, num):
        self.commits=num

    def set_branches_num(self, num):
        self.branches=num

    def set_releases_num(self, num):
        self.releases=num

    def set_contributors_num(self, num):
        self.contributors=num

    def set_description(self, des):
        self.description=des

    def crawling_details(self):
        print 'Crawling: %s' % self.href
        repos=Repository(self.href)
        failure=True
        try_time=0
        description=''
        while failure and try_time<MAX_TRY_TIME:
            try:
                opener=urllib2.build_opener()
                if len(COOKIE)>0:
                    opener.addheaders.append(('Cookie', COOKIE))
                req=opener.open(baseURL+self.href)
                soup=BeautifulSoup(req.read())
                for readme in soup.findAll('div', {'id':'readme'}):
                    description=unicode(readme)
                repos.set_description(description)
                num_summary=soup.findAll('ul', {'class':'numbers-summary'})
                if len(num_summary)>0:
                    num_summary=num_summary[0]
                    self.commits=get_num(num_summary, 'commits')
                    self.branches=get_num(num_summary, 'branch')
                    self.contributors=get_num(num_summary, 'contributor')
                    self.releases=get_num(num_summary, 'releases')
#                if self.commits==0 or self.contributors==0:
#                    print num_summary.findAll('li')
                    
                for counter in soup.findAll('a'):
                    if counter.has_attr('class') and 'social-count' in set(counter.attrs['class']):
                        if counter['href'].find('stargazers')>-1:
                            self.stargazers=counter.contents[0].strip().replace(',', '')
                        elif counter['href'].find('watchers')>-1:
                            self.watchers=counter.contents[0].strip().replace(',', '')
                        elif counter['href'].find('network')>-1:
                            self.forks=counter.contents[0].strip().replace(',', '')
#                for color in soup.findAll('span', {'class':'language-color'}):
#                for div in soup.findAll('div', {'class':'repository-lang-stats'}):
                for ol in soup.findAll('ol', {'class':'repository-lang-stats-numbers'}):
                    for li in ol.findAll('li'):
                        lang=''
                        percent=0
                        for span in li.findAll('span'):
                            if span.has_attr('class') and 'lang' in set(span.attrs['class']):
                                lang=span.contents[0].strip()
                            elif span.has_attr('class') and 'percent' in set(span.attrs['class']):
                                percent=float(span.contents[0].strip().split('%')[0])/100
                        self.lang_percent[lang]=percent
                self.description=description
                failure=False
            except urllib2.URLError as e:
                time.sleep(1)
                try_time+=1
                print e
        print self.all_info_str()


class User:
    def __init__(self, href):
        self.href=href
        self.user=self.href.split('/')[1]

    def __str__(self):
        return self.href

    __repr__=__str__

    def __hash__(self):
        return self.__str__().__hash__()

    def __cmp__(self, obj):
        return cmp(str(self), str(obj))

def deal_with_line(line, tagList):
    item=line.strip().split()
    start='<\s*\S+'
    end='</\s*\S+\s*>'
    for index in range(len(line)):
        if line[index]=='<' and line[index+1]!='-' and line[index+1]!='!':
            pass

class GitHubCrawler:
    def __init__(self, saveDir, logname='info'):
        self.visited_repository=set()
        self.visited_user=set() 
        self.success_num=0
        self.saveDir=saveDir
        self.verbose=True
        # whether to clone the repository or not
        self.truelyClone=True
        self.userQueue=Queue.Queue()
        if not os.path.isdir(saveDir):
            os.mkdir(saveDir)
        logging.basicConfig(filename=os.path.join(saveDir, ('crawling-%s.log' % logname)), level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        self.logger=logging.getLogger('Crawler-BFS')

    def loading_visited_user(self):
        for root, dirs, files in os.walk(self.saveDir):
            for dir in dirs:
                self.visited_user.add(User('/'+dir))
                print dir
            break

    def parse_repos(self, langContent, h3Content):
        lines=h3Content.split('\n')
        for line in lines:
            if line.find('href')!=-1:
                indexBegin=line.find('"', line.find('href'))
                href=line[indexBegin+1:line.find('"', indexBegin+1)]
                repos=Repository(href)
                repos.set_lang(langContent)
                print langContent, href
                return repos
    
    def crawler_user(self, user):
        try:
            if user.href not in self.visited_user:
                print baseURL+user.href+'?tab=repositories'
                req=urllib2.urlopen(baseURL+user.href+'?tab=repositories')
                soup=BeautifulSoup(req.read())
                for li in soup.findAll('li', {'class':'public source'}):
                    lang=''
                    for lang_li in li.ul.findAll('li', {'class':'language'}):
                        lang=lang_li.contents[0]
                    repos=Repository(li.h3.a['href'])
                    repos.set_lang(lang)
                    self.crawling_repository(repos)

                for li in soup.findAll('li', {'class':'public fork'}):
                    lang=''
                    for lang_li in li.ul.findAll('li', {'class':'language'}):
                        lang=lang_li.contents[0]
                    repos=Repository(li.p.a['href'])
                    repos.set_lang(lang)
                    self.crawling_repository(repos)
                self.visited_user.add(user.href)
        except urllib2.URLError as e:
            print e

    def crawling_user_old(self, user):
        '''
            deprecated
        '''
        try:
            if self.verbose:
                print 'Crawling user:', user.user
            if user.href not in self.visited_user:
                recording=False
                recordingH3=False
                recording_fork=False
                print baseURL+user.href+'?tab=repositories'
                req=urllib2.urlopen(baseURL+user.href+'?tab=repositories')
                result=req.read()
                lines=result.split('\n')
                h3=''
                lang=''
                fork_flag=''
                for line in lines:
                    if recording:
                        if recordingH3:
                            h3+=line
                            if line.find('</h3')!=-1:
                                #print h3
                                repos=self.parse_repos(lang, h3)
                                self.crawling_repository(repos)
                                recordingH3=False
                                h3=''
                        else:
                            if line.find('<h3')!=-1:
    #                            print line
                                recordingH3=True
                                h3+=line
                            if line.find('</h3')!=-1:
                                h3+=line
    #                            print h3
                                repos=self.parse_repos(lang, h3)
                                self.crawling_repository(repos)
                                recordingH3=False
                                h3=''
                            if line.find('class="language"')!=-1:
                                lang=line[line.find('>')+1:line.find('<', line.find('>'))]
    #                            print lang
                    elif line.find('ul')!=-1 and line.find('repolist js-repo-list')!=-1:
                        recording=True
                self.visited_user.add(user.href)
        except urllib2.URLError as e:
            print baseURL+user.href+'?tab=repositories'
            print e

    def crawling_repos_followers(self, repos, item):
        failure=True
        while failure:
            try:
                print baseURL+repos.href+item
                req=urllib2.urlopen(baseURL+repos.href+item)
                result=req.read()
                soup=BeautifulSoup(result)
                for d in soup.div():
                    if d.attrs.has_key('class') and 'follow-list-container' in d.attrs['class']:
                        user=User(d.a['href'])
                            #self.crawler_user(user)
                        self.userQueue.put(user)
                        self.logger.info('Repository:%s Lang:%s %s:%s' % (repos.href, repos.lang, item.split('/')[1], user.user))
                failure=False
            except urllib2.URLError as e:
                sys.stderr.write('%s when crawling %s' % (e, repos.href+item))
    
    def crawling_repos_contributors(self, repos, item):
        failure=True
        while failure:
            try:
                print baseURL+repos.href+item
                req=urllib2.urlopen(baseURL+repos.href+item)
                result=req.read()
                soup=BeautifulSoup(result)
                for d in soup.div():
                    if d.attrs.has_key('id') and d.attrs['id']=='contributors':
                        print d
                failure=False
            except urllib2.URLError as e:
                sys.stderr.write('%s when crawling %s' % (e, repos.href+item))

    def crawling_repos_contributors_API(self, repos, item):
        '''
            crawling via API
        '''
        try:
            running=True
            try_times=0
            while running:
                try:
                    print baseURL+repos.href+item
                    req=urllib2.urlopen(baseURL+repos.href+item)
                    data=json.load(req)
                    for info in data:
                        user=User('/%s' % info['author']['login'])
                        self.userQueue.put(user)
                        self.logger.info('Repository:%s Lang:%s Contributor:%s Total:%s' % (repos.href, repos.lang, user.user, info['total']))
                    print 'Got it!'
                    running=False
                except ValueError as e:
                    print e
                    req=urllib2.urlopen(baseURL+repos.href+item)
                    result=req.read()
                    if result.find('<!DOCTYPE html>')>0:
                        running=False
                    else:
                        try_times+=1
                        time.sleep(1)
                        running=True
                    if try_times>MAX_TRY_TIME:
                        self.logger.warning('Repository:%s Lang:%s Exceeds MAX_TRY_TIME:%s' % (repos.href, repos.lang, MAX_TRY_TIME))
                        print 'After %s times, we still cannot fetch the result!' % try_times
                        running=False
                        break
        except urllib2.URLError as e:
            print e

    def crawling_repository_fork_info(self, repos):
        try:
            req=urllib2.urlopen(baseURL+repos.href)
            soup=BeautifulSoup(req.read())
            for fork in soup.findAll('span', {'class':'fork-flag'}):
                self.logger.info('Repository:%s ForkFrom:%s' % (repos.href, fork.span.a['href']))
        except urllib2.URLError as e:
            print e

    def crawling_repository(self, repos):
        if repos.href not in self.visited_repository:
            if self.verbose:
                print 'Crawling the repository:', repos.href, 'Language:', repos.lang
            if self.truelyClone:
                if not os.path.isdir(os.path.join(self.saveDir, repos.user)):
                    os.mkdir(os.path.join(self.saveDir, repos.user))
                if not os.path.isdir(os.path.join(self.saveDir, repos.user, repos.lang)):
                    os.mkdir(os.path.join(self.saveDir, repos.user, repos.lang))
                os.system(' '.join(['git', 'clone', baseURL+repos.href, os.path.join(self.saveDir, repos.user, repos.lang, repos.repos_name)]))
            self.visited_repository.add(repos.href)
            self.crawling_repos_contributors_API(repos, '/graphs/contributors-data')
#            self.crawling_repos_followers(repos, '/watchers')
#            self.crawling_repos_followers(repos, '/stargazers')
#            self.crawling_repos_contributors(repos, '/graphs/contributors')

#            self.crawling_repos_followers(repos, '/collaborators')

    def bfs_crawling(self):
        while not self.userQueue.empty():
#            time.sleep(random.randrange(2, 20)/10)
            self.crawling_user(self.userQueue.get())
            if len(self.visited_user)>N:
                break
        while not self.userQueue.empty():
            user=self.userQueue.get()
            if user.href not in self.visited_user:
                self.logger.info('Unfinished user:%s', user.user)

    def crawler_trending(self, href):
        t=''.join([baseURL, '/trending?', href])
        print t
        try:
            req=urllib2.urlopen(t)
            result=req.read()
            soup=BeautifulSoup(result)
            for d in soup.div():
                if d.attrs.has_key('class') and 'leaderboard-list-content' in d.attrs['class']:
                    repos=Repository(d.a['href'])
                    self.userQueue.put(User('/'+repos.user))
        except urllib2.URLError as e:
            print e.reason

class GitHubCrawler_API(GitHubCrawler):
    def __init__(self, saveDir):
        GitHubCrawler.__init__(self, saveDir)
        self.apiURL='https://api.github.com'

    def parse_repos_info(self, content):
        try:
            for repoDict in content:
                lang=repoDict['language']
                private=repoDict['private']
                updateTime=repoDict['updated_at']
                fullName=repoDict['full_name']
                repo=Repository('/'+fullName)
                repo.set_lang(lang)
                self.crawling_repository(repo)
        except urllib2.URLError as e:
            print e.reason
        except urllib2.HTTPError as e:
            print e.reason

    def crawling_user(self, user):
        #crawling user by GitHub API
        repos=[]
        if user.href not in self.visited_user:
            p=1
            if self.verbose:
                print 'Start crawling user:', user.user
            try:
                while True:
                    req=urllib2.urlopen(self.apiURL+'/users'+user.href+'/repos?page='+str(p))
                    result=req.read()
                    content=json.loads(result)
                    if len(content)==0:
                        break
                    repos.extend(content)
                    p+=1
                self.parse_repos_info(repos)
                self.visited_user.add(user.href)
            except urllib2.URLError as e:
                print self.apiURL+'/users'+user.href+'/repos?page='+str(p)
                self.userQueue.put(user)
                print e
            except urllib2.HTTPError as e:
                print self.apiURL+'/users'+user.href+'/repos?page='+str(p)
                self.userQueue.put(user)
                print e


    def parse_user_info(self, content):
        try:
            for userDict in content:
                user=User('/'+userDict['login'])
                self.userQueue.put(user)
#                crawling_user_api(self, user)
        except urllib2.URLError as e:
            print e.reason

    def crawling_repos_followers(self, repos, item):
        '''
            crawling the users who watch or collaborate this repository
        '''
        p=1
        users=[]
        try:
            while True:
                print self.apiURL+'/repos'+repos.href+item+'?page='+str(p)
                req=urllib2.urlopen(self.apiURL+'/repos'+repos.href+item+'?page='+str(p))
                content=json.loads(req.read())
                if len(content)==0:
                    break
                users.extend(content)
                p+=1
            self.parse_user_info(users)
        except urllib2.URLError as e:
            print e.reason
        except urllib2.HTTPError as e:
            print self.apiURL+'/users'+repos.href+item+'?page='+str(p)
            print e.reason

    def crawling_repos_contributors(self, repos, item):
        '''
            API
        '''
        try:
            print baseURL+repos.href+item
            req=urllib2.urlopen(baseURL+repos.href+item)
            data=json.load(req)
            for info in data:
                user=User('/%s' % info['author']['login'])
                self.userQueue.put(user)
                print user
                self.logger.info('Repository:%s Lang:%s Contributor:%s Total:%s' % (repos.href, repos.lang, user.user, info['total']))
        except urllib2.URLError as e:
            print e

    def crawling_repository(self, repos):
        if repos.href not in self.visited_repository:
            if self.verbose:
                print 'Crawling the repository:', repos.href, 'Language:', repos.lang
            if self.truelyClone:
                if not os.path.isdir(os.path.join(self.saveDir, repos.user)):
                    os.mkdir(os.path.join(self.saveDir, repos.user))
                if not os.path.isdir(os.path.join(self.saveDir, repos.user, repos.lang)):
                    os.mkdir(os.path.join(self.saveDir, repos.user, repos.lang))
                os.system(' '.join(['git', 'clone', baseURL+repos.href, os.path.join(self.saveDir, repos.user, repos.lang, repos.repos_name)]))
            self.visited_repository.add(repos.href)
            self.crawling_repos_followers(repos, '/watchers')
            self.crawling_repos_followers(repos, '/stargazers')
            self.crawling_repos_followers(repos, '/collaborators')


def crawling_repository_fork_info(repos):
    '''
        crawling where is the repository forked from, to deal with the problem of alias
    '''
    try:
        sys.stderr.write('%s\n' % repos.href)
        logger=logging.getLogger('Crawler-ForkInfo-%s' % repos.href)
        req=urllib2.urlopen('https://github.com'+repos.href)
        soup=BeautifulSoup(req.read())
        for fork in soup.findAll('span', {'class':'fork-flag'}):
            logger.info('Repository:%s ForkFrom:%s' % (repos.href, fork.span.a['href']))
    except urllib2.URLError as e:
        print e

def only_crawling_fork(log_path, save_log_path):
    logging.basicConfig(filename=save_log_path, level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    pool=ProcessPool(poolsize)
    fp=open(log_path)
    visited_repos=set()
    for line in fp.readlines():
        href=line.strip().split()[6].split(':')[-1]
        if href not in visited_repos:
#            crawling_repository_fork_info(Repository(href))
#            print href           
            pool.apply_async(crawling_repository_fork_info, (Repository(href),))
            visited_repos.add(href)
    fp.close()
#    pool.close()
#    pool.join()

#    def crawler_trending_api(self, href):

if __name__=='__main__':
    repoDir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/github-network-info'
    only_crawling_fork(os.path.join(repoDir, 'crawling-watchers.log'), os.path.join(repoDir, 'crawling-watchers-fork_info.log'))

    
#    gitCrawler=GitHubCrawler(repoDir, 'contributors')
##    gitCrawler=GitHubCrawler_API(repoDir)
#    gitCrawler.truelyClone=False
##    gitCrawler.loading_visited_user()
##    repos=Repository('/voldemort/voldemort')
##    repos=Repository('/facebook/presto')
##    for i in range(100):
##        print i
##        gitCrawler.crawling_repos_contributors(repos, '/graphs/contributors-data')
#    gitCrawler.crawler_trending('l=python&since=monthly')
#    gitCrawler.bfs_crawling()
#
##    gitCrawler.crawler_trending('l=php&since=monthly', os.path.join(repoDir, 'php-repository'))
##    gitCrawler.crawler_trending('l=java&since=monthly', os.path.join(repoDir, 'java-repository'))
##    user=User('/daveman692')
##    gitCrawler.crawling_user(user)
##    fp=open(sys.argv[1])
##    result=''
##    while True:
##        lines=fp.readlines(10000)
##        if not lines:
##            break
##        for line in lines:
##            result+=line
##    p=UserHTMLParser()
##    p.feed(result)
##    fp.close()
##    crawler('~/wxmao/umass/research/software/python-repository')
#
