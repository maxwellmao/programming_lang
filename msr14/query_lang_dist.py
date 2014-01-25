#!/usr/bin/python
from __future__ import division
import os, sys
import json
import urllib2
from bs4 import BeautifulSoup
'''
query the distribution of programming language in one specified projects
'''
apiBaseURL='https://api.github.com/repos'
baseURL='https://github.com'
nonEmpty=0

def crawling_lang_stat(repo_url):
    '''
        crawling language list of repo from the webpage of repo
    '''
    req=urllib2.urlopen(repo_url)
    soup=BeautifulSoup(req.read())
    lang_list=[]
    for ol in soup.findAll('ol', {'class':'repository-lang-stats-numbers'}):
        for li in ol.findAll('li'):
            for span in li.findAll('span'):
                if span.has_attr('class') and 'lang' in set(span.attrs['class']):
                    lang=span.contents[0].strip()
                    lang_list.append(lang)
    print repo_url, lang_list
    return lang_list

def search_lang_dist(repo_url, lang):
    '''
        crawling language list of repo from the search webpage of repo
    '''
    lang_dist={}
    try_time=0
    failure=True
    MAX_TRY_TIME=20
    while failure and try_time<MAX_TRY_TIME:
        try:
            req=urllib2.urlopen(repo_url+'/search?l=%s' % lang)
            soup=BeautifulSoup(req.read())
            for ul in soup.findAll('ul', {'class':'filter-list small', 'data-pjax':''}):
                for li in ul.findAll('li'):
                    if len(li.a.span.contents)>0:
                        lang_dist[li.a.contents[-1].strip()]=int(li.a.span.contents[0].replace(',', '').replace('+', ''))
            failure=False
        except urllib2.HTTPError as e:
            sys.stderr.write('%s %s %s\n' % (repo_url, lang, e))
            try_time+=1
    return lang_dist

def crawling_lang_dist(repo_url):
    if repo_url.startswith(apiBaseURL):
        repo_url=repo_url.replace(apiBaseURL, baseURL)
#    crawling_lang_stat(repo_url)
    lang_dict=search_lang_dist(repo_url, 'c')
    for lang, freq in search_lang_dist(repo_url, 'java').items():
        lang_dict[lang]=freq
    for lang, freq in search_lang_dist(repo_url, 'bash').items():
        lang_dict[lang]=freq
    if len(lang_dict)>0:
        print repo_url
        print '\t'.join(['%s:%s' % (lang, freq) for lang, freq in lang_dict.items()])

def query_lang_dist_api(repo_url):
    try:
        req=urllib2.urlopen(repo_url+'/languages')
        lang_dist=json.load(req)
        if len(lang_dist)>0:
            nonEmpty+=1
            print repo_url
            for lang, freq in lang_dist.items():
                print lang, freq
            return lang_dist
    except urllib2.HTTPError as e:
        print e
    return {}

def load_repo_url_from_stdin():
    for line in sys.stdin:
        if line.startswith('https'):
#            query_lang_dist_api(line.strip())
            crawling_lang_dist(line.strip())

if __name__=='__main__':
    load_repo_url_from_stdin()
    print 'NonEmpty:%s' % nonEmpty
