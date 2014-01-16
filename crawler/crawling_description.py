#!/usr/bin/python
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
import sqlite3
from crawling_github import Repository

MAX_TRY_TIME=50
baseURL='https://github.com'


class DB_sqlite:
    def __init__(self, db_path):
        self.conn=sqlite3.connect(db_path)
        self.cursor=self.conn.cursor()
        self.repository_info_table_name='RepositoryInfo'

    def drop_repository_info_table(self):
        self.cursor.execute('DROP TABLE IF EXISTS %s' % self.repository_info_table_name)
    
    def create_repository_info_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                    (href text, lang text, commits integer, branches integer, releases integer, contributors integer, readme text)''' % self.repository_info_table_name)

    def insert_repository(self, repos):
#        print "INSERT INTO %s VALUES ('%s', '%s', '%s')" % (self.repository_info_table_name, repos.href, repos.lang, description)
#        self.cursor.execute("INSERT INTO %s VALUES ('%s', '%s', '%s')" % (self.repository_info_table_name, repos.href, repos.lang, description))
        self.cursor.execute(("INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?, ?)" % (self.repository_info_table_name)), (repos.href, repos.lang, repos.commits, repos.branches, repos.releases, repos.contributors, repos.description,))

    def commit_repository_update(self):
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def construct_repository_info(self, log_path, alias_path='', create_new_table=True):
        if create_new_table:
            self.create_repository_info_table()
        alias_dict=dict()
        if len(alias_path)>0:
            fp=open(alias_path)
            for line in fp.readlines():
                items=line.strip().split()
                alias_dict[items[6].split(':')[1]]=items[7].split(':')[1]
            fp.close()
        repos_index=6
        repos_lang_index=7
        visited_repos_href=set()
        fp=open(log_path)
        index=0
        for line in fp.readlines():
            items=line.strip().split()
            if items[repos_index].startswith('Repository'):
                if alias_dict.has_key(items[repos_index].split(':')[-1]):
                    repos=Repository(alias_dict[items[repos_index].split(':')[-1]])
                else:
                    repos=Repository(items[repos_index].split(':')[-1])
                repos.set_lang(items[repos_lang_index].split(':')[-1])
            if repos.href not in visited_repos_href:
                while repos.contributors==0:
                    repos.crawling_details()
                self.insert_repository(repos)
                visited_repos_href.add(repos.href)
            index+=1
            if index%1000==0:
                self.commit_repository_update()
                index=0
        self.commit_repository_update()
        fp.close()

if __name__=='__main__':
    if len(sys.argv)==2:
        repos=Repository(sys.argv[1])
        repos.crawling_details()
    else:
        db=DB_sqlite(sys.argv[1])
        db.drop_repository_info_table()
        if len(sys.argv)>3:
            db.construct_repository_info(sys.argv[2], sys.argv[3])
        elif len(sys.argv)==3:
            db.construct_repository_info(sys.argv[2])
        
