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

headers = { 'User-Agent' : 'Mozilla/5.0' }
N=1000000
MAX_TRY_TIME=100

class Repository:
    def __init__(self, href):
        self.href=href
        info=self.href.split('/')[1:]
        self.user=info[0]
        self.repos_name=info[1]

    def __str__(self):
        return self.href

    __repr__=__str__

    def __hash__(self):
        return self.__str__().__hash__()

    def __cmp__(self, obj):
        return cmp(str(self), str(obj))

    def set_lang(self, lang):
        self.lang=lang

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
        self.baseURL='https://github.com'
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

    def crawling_user(self, user):
        try:
            if self.verbose:
                print 'Crawling user:', user.user
            if user.href not in self.visited_user:
                recording=False
                recordingH3=False
                print self.baseURL+user.href+'?tab=repositories'
                req=urllib2.urlopen(self.baseURL+user.href+'?tab=repositories')
                result=req.read()
                lines=result.split('\n')
                h3=''
                lang=''
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
            print self.baseURL+user.href+'?tab=repositories'
            print e

    def crawling_repos_followers(self, repos, item):
        failure=True
        while failure:
            try:
                print self.baseURL+repos.href+item
                req=urllib2.urlopen(self.baseURL+repos.href+item)
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
                print self.baseURL+repos.href+item
                req=urllib2.urlopen(self.baseURL+repos.href+item)
                result=req.read()
    #            print result
                soup=BeautifulSoup(result)
    #            for li in soup.find_all('li'):
    #                if li.attrs.has_key('class') and li.attrs['class']=='capped-card':
    #                   print li.h3.a
                for d in soup.div():
                    if d.attrs.has_key('id') and d.attrs['id']=='contributors':
                        print d
    #                    user=User(d.a['href'])
                            #self.crawler_user(user)
    #                    self.userQueue.put(user)
    #                    self.logger.info('Repository:%s %s:%s' % (repos.href, item.split('/')[1], user.user))
                failure=False
            except urllib2.URLError as e:
                sys.stderr.write('%s when crawling %s' % (e, repos.href+item))

    def crawling_repos_contributors_API(self, repos, item):
        '''
            API
        '''
        try:
            running=True
            try_times=0
            while running:
                try:
                    print self.baseURL+repos.href+item
                    req=urllib2.urlopen(self.baseURL+repos.href+item)
                    data=json.load(req)
                    for info in data:
                        user=User('/%s' % info['author']['login'])
                        self.userQueue.put(user)
                        self.logger.info('Repository:%s Lang:%s Contributor:%s Total:%s' % (repos.href, repos.lang, user.user, info['total']))
                    print 'Got it!'
                    running=False
                except ValueError as e:
                    print e
                    req=urllib2.urlopen(self.baseURL+repos.href+item)
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

    def crawling_repository(self, repos):
        if repos.href not in self.visited_repository:
            if self.verbose:
                print 'Crawling the repository:', repos.href, 'Language:', repos.lang
            if self.truelyClone:
                if not os.path.isdir(os.path.join(self.saveDir, repos.user)):
                    os.mkdir(os.path.join(self.saveDir, repos.user))
                if not os.path.isdir(os.path.join(self.saveDir, repos.user, repos.lang)):
                    os.mkdir(os.path.join(self.saveDir, repos.user, repos.lang))
                os.system(' '.join(['git', 'clone', self.baseURL+repos.href, os.path.join(self.saveDir, repos.user, repos.lang, repos.repos_name)]))
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
        t=''.join([self.baseURL, '/trending?', href])
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
               # print dir

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
        # crawling the users who watch or collaborate this repository
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
            print self.baseURL+repos.href+item
            req=urllib2.urlopen(self.baseURL+repos.href+item)
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
                os.system(' '.join(['git', 'clone', self.baseURL+repos.href, os.path.join(self.saveDir, repos.user, repos.lang, repos.repos_name)]))
            self.visited_repository.add(repos.href)
            self.crawling_repos_followers(repos, '/watchers')
            self.crawling_repos_followers(repos, '/stargazers')
            self.crawling_repos_followers(repos, '/collaborators')





#    def crawler_trending_api(self, href):
        
        

if __name__=='__main__':
    repoDir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/github-network-info'
    
    gitCrawler=GitHubCrawler(repoDir, 'contributors')
#    gitCrawler=GitHubCrawler_API(repoDir)
    gitCrawler.truelyClone=False
#    gitCrawler.loading_visited_user()
#    repos=Repository('/voldemort/voldemort')
#    repos=Repository('/facebook/presto')
#    for i in range(100):
#        print i
#        gitCrawler.crawling_repos_contributors(repos, '/graphs/contributors-data')
    gitCrawler.crawler_trending('l=python&since=monthly')
    gitCrawler.bfs_crawling()

#    gitCrawler.crawler_trending('l=php&since=monthly', os.path.join(repoDir, 'php-repository'))
#    gitCrawler.crawler_trending('l=java&since=monthly', os.path.join(repoDir, 'java-repository'))
#    user=User('/daveman692')
#    gitCrawler.crawling_user(user)
#    fp=open(sys.argv[1])
#    result=''
#    while True:
#        lines=fp.readlines(10000)
#        if not lines:
#            break
#        for line in lines:
#            result+=line
#    p=UserHTMLParser()
#    p.feed(result)
#    fp.close()
#    crawler('~/wxmao/umass/research/software/python-repository')

