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
import datetime
from multiprocessing import Pool as ProcessPool
from deep_crawling import test_last_page
from crawling_github import COOKIE
from crawling_github import baseURL
from crawling_github import N
from crawling_github import HEADERS

MAX_TRY_TIME=50

(_org, _individual)=range(2)

class User:
    def __init__(self, href):
        self.href=href
        self.baseURL='https://github.com'
        self.user=self.href.split('/')[1]
        self.organization=''
        self.location=''
#        self.email=''
        self.link=''
        self.join_label=''
        self.join_date=datetime.datetime(1999,1,1)
        self.user_type=_individual
        self.belong_organization=[]

    def __str__(self):
        return self.href

    __repr__=__str__

    def __hash__(self):
        return self.__str__().__hash__()

    def __cmp__(self, obj):
        return cmp(str(self), str(obj))

    def all_info_str(self):
        return u'href:%s, user_type:%s ,org:%s, loc:%s, link:%s, join_label:%s, join_date:%s, belong_org:%s' % (self.href, self.user_type, self.organization.encode("utf-8"), self.location.encode("utf-8"), self.link, self.join_label, self.join_date, ';'.join(self.belong_organization))

    def crawling_details(self):
        try_time=0
        failure=True
        self.belong_organization=[]
        while failure and try_time<MAX_TRY_TIME:
            try:
                opener=urllib2.build_opener()
                opener.addheaders.append(('Cookie', COOKIE))
                opener.addheaders.append(('User-Agent', HEADERS))
                req=opener.open(self.baseURL+self.href)
                soup=BeautifulSoup(req.read(), from_encoding='utf-8')
                for div in soup.findAll('div'):
                    if div.has_attr('class') and 'vcard' in set(div.attrs['class']):
                        for card_detail in div.findAll('li', {'class':'vcard-detail'}):
                            for span in card_detail.findAll('span'):
                                if span.has_attr('class') and len(span['class'])==2:
                                    item=span['class'][1].split('-')[-1]
                                    value=''
                                    for c in card_detail.contents:
                                        if not unicode(c).strip().startswith('<'):
                                            value=unicode(c).strip()
                                    
#                                    try:
#                                        for c in card_detail.contents:
#                                            print c
#                                #.contents:
##                                        print c.encode('utf-8')
#                                            if not unicode(c, 'utf-8').strip().startswith('<'):
##                                        if not unicode(c).strip().decode('utf-8').startswith('<'):
##                                            print c.decode('utf-8')
#                                                value=unicode(c, 'utf-8').strip()
#                                    except Exception as e:
#                                        print e
#                                        print c
                                    if item=='location':
                                        self.location=value
                                    elif item=='organization':
                                        self.organization=value
#                                    elif item=='mail' or item=='email':
#                                        print card_detail
#                                        self.email=card_detail.a['href']
#                                        print card_detail.a['href']
#                                        print card_detail.a.contents
                                    elif item=='link':
                                        self.link=card_detail.a['href']
                                elif span.has_attr('class') and len(span['class'])==1:
                                    if str(span['class'][0])=='join-label':
                                        self.join_label=str(span.contents[0]).strip()
                                    elif str(span['class'][0])=='join-date':
                                        self.join_date=datetime.datetime.strptime(str(span.contents[0]), '%b %d, %Y')
                    elif div.has_attr('class') and 'vcard-stats' in set(div.attrs['class']):
                        stats=div.findAll('a')
                        if len(stats)==3:
                            self.user_type=_individual
                        elif len(stats)==2:
                            self.user_type=_org
                    elif div.has_attr('class') and 'avatars' in set(div.attrs['class']):
                        for org in div.findAll('a'):
                            self.belong_organization.append(org['href'])
                failure=False
            except urllib2.URLError as e:
                time.sleep(1)
                try_time+=1
                print e
        try:
            print self.all_info_str()
        except Exception as e:
            print e


class FollowCrawler:
    def __init__(self, saveDir='', logname='user_follow', do_log=True):
        self.visited_user=set()
        self.userQueue=Queue.Queue()
        self.do_log=do_log
        if self.do_log:
            logging.basicConfig(filename=os.path.join(saveDir, ('crawling-%s.log' % logname)), level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
            self.logger=logging.getLogger('Crawler-Follow')

    def bfs_crawling(self, initial_user_path):
        '''
            crawling the following/follower relationship between individual users, initialized the crawling queue with initial_user_path
        '''
        fp=open(initial_user_path)
        for line in fp.readlines():
            if len(line.strip())>0:
                self.userQueue.put(User('/'+line.strip()))
                self.visited_user.add('/'+line.strip())
        fp.close()
        crawling_num=0
        while not self.userQueue.empty() and crawling_num<N:
            user=self.userQueue.get()
            print 'Crawling %s' % user.href
            self.crawling_user_follow(user, '/following')
            self.crawling_user_follow(user, '/followers')
            crawling_num+=1


    def crawling_user_follow(self, user, item):
        if user.user_type==_individual:
            last_page=test_last_page(baseURL+user.href+item)
            for n in range(1, last_page+1):
                try_time=0
                failure=True
                while failure and try_time<MAX_TRY_TIME:
                    try:
                        req=urllib2.urlopen(baseURL+user.href+item+'?page='+str(n))
                        soup=BeautifulSoup(req.read())
                        follow_list=[]
                        for li in soup.findAll('li', {'class':'follow-list-item'}):
                            follow_list.append(li.a['href'])
                            if self.do_log:
                                self.logger.info('User:%s %s:%s' % (user.href.split('/')[1], item.split('/')[1], li.a['href'].split('/')[1]))
                            if li.a['href'] not in self.visited_user:
                                self.userQueue.put(User(li.a['href']))
                                self.visited_user.add(li.a['href'])
                        failure=False
                        if len(follow_list)==0:
                            n=last_page+1
                    except urllib2.URLError as e:
                        try_time+=1
                        print e
                if n>last_page:
                    break

poolsize=10

def crawling_user_follow_process(user, item, logger):
    if user.user_type==_individual:
        last_page=test_last_page(baseURL+user.href+item)
        for n in range(1, last_page+1):
            try_time=0
            failure=True
            while failure and try_time<MAX_TRY_TIME:
                try:
                    req=urllib2.urlopen(baseURL+user.href+item+'?page='+str(n))
                    soup=BeautifulSoup(req.read())
                    follow_list=[]
                    for li in soup.findAll('li', {'class':'follow-list-item'}):
                        follow_list.append(li.a['href'])
                        logger.info('User:%s %s:%s' % (user.href.split('/')[1], item.split('/')[1], li.a['href'].split('/')[1]))
                    failure=False
                    if len(follow_list)==0:
                        n=last_page+1
                except urllib2.URLError as e:
                    try_time+=1
                    print e
            if n>last_page:
                break


def crawling_process(initial_user_path):
    userQueue=Queue.Queue()
    fp=open(initial_user_path)
    logger=logging.getLogger('Crawler-Follow-%s' % initial_user_path.split('/')[-1])
    for line in fp.readlines():
        if len(line.strip())>0:
            userQueue.put(User('/'+line.strip()))
    fp.close()
    crawling_num=0
    while not userQueue.empty():
        user=userQueue.get()
        print user.href
        crawling_user_follow_process(user, '/following', logger)
        crawling_user_follow_process(user, '/followers', logger)
        crawling_num+=1

def crawling_follow_multi_process(saveDir, init_dir, logname='user_follow'):
    logging.basicConfig(filename=os.path.join(saveDir, ('crawling-%s.log' % logname)), level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    pool=ProcessPool(poolsize)
    for file in os.listdir(init_dir):
        if os.path.isfile(os.path.join(init_dir, file)):
            print os.path.join(init_dir, file)
            pool.apply_async(crawling_process, (os.path.join(init_dir, file), ))
    pool.close()
    pool.join()


if __name__=='__main__':
    if len(sys.argv)==2:
        user=User(sys.argv[1])
        user.crawling_details()
        crawler=FollowCrawler(do_log=False)
        crawler.crawling_user_follow(user, '/following')
        crawler.crawling_user_follow(user, '/followers')
    elif len(sys.argv)==3:
#        crawler=FollowCrawler(sys.argv[1])
#        crawler.bfs_crawling(sys.argv[2])
        crawling_follow_multi_process(sys.argv[1], sys.argv[2])
