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
import crawling_github
from crawling_github import Repository
from crawling_github import COOKIE
from crawling_github import MAX_TRY_TIME
from crawling_github import baseURL
from crawling_user import User


class DB_sqlite:
    def __init__(self, db_path):
        self.conn=sqlite3.connect(db_path)
        self.cursor=self.conn.cursor()
        self.repository_info_table_name='RepositoryInfo'
        self.user_info_table_name='UserInfo'

    def drop_repository_info_table(self):
        self.cursor.execute('DROP TABLE IF EXISTS %s' % self.repository_info_table_name)
    
    def create_repository_info_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                (href text, lang text, commits integer, branches integer, releases integer, 
                 contributors integer, watchers integer, stargazers integer, forks integer, 
                 readme text)''' % self.repository_info_table_name)

    def create_user_info_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                (href text, organization text, location text, link text, join_label text, join_date text, user_type text, belong_organization text)''' % self.user_info_table_name)
    
    def drop_user_info_table(self):
        self.cursor.execute('DROP TABLE IF EXISTS %s' % self.user_info_table_name)

    def update_repository_info(self, repos):
        '''
            updating the information of repository according to the href
        '''
        pass

    def update_contributors_in_repository_info(self):
        '''
            update the number of contributors for whose contributors was 0 in the database
        '''
        self.cursor.execute('SELECT * from %s where contributors=0' % self.repository_info_table_name)
        result = self.cursor.fetchall()
        for row in result:
            print row
            repos=Repository(row[0])
            repos.get_from_db(row)
            repos.get_contributors()
            print repos.all_info_str()
            self.cursor.execute("""UPDATE %s SET contributors=%s WHERE href='%s'""" % (self.repository_info_table_name, repos.contributors, repos.href))
            self.commit_update()

    def insert_repository(self, repos):
#        print "INSERT INTO %s VALUES ('%s', '%s', '%s')" % (self.repository_info_table_name, repos.href, repos.lang, description)
#        self.cursor.execute("INSERT INTO %s VALUES ('%s', '%s', '%s')" % (self.repository_info_table_name, repos.href, repos.lang, description))
        self.cursor.execute(("INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % (self.repository_info_table_name)), (repos.href, ';'.join([('%s:%s' % (k,v)) for k,v in repos.lang_percent.items()]), repos.commits, repos.branches, repos.releases, repos.contributors, repos.watchers, repos.stargazers, repos.forks, repos.description,))

    def insert_user(self, user):
#        print user.href, user.organization, user.location, user.link, user.join_label, user.join_date.strftime('%Y-%m-%d'), user.user_type, ';'.join(user.belong_organization)
        self.cursor.execute(("INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?, ?, ?)" % (self.user_info_table_name)), (user.href, user.organization, user.location, user.link, user.join_label, user.join_date.strftime('%Y-%m-%d'), user.user_type, ';'.join(user.belong_organization),))

    def commit_update(self):
        print 'Commit!'
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def query_repository_info(self):
        tableListQuery = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY Name"
        self.cursor.execute(tableListQuery)
        tables = map(lambda t: t[0], self.cursor.fetchall())
        print tables

        self.cursor.execute('SELECT COUNT(*) from %s where contributors=0' % self.repository_info_table_name)
        result=self.cursor.fetchone()
        print '0-contributor Repository table:%s' % result[0]

        self.cursor.execute('SELECT COUNT(*) from %s ' % self.user_info_table_name)
        result=self.cursor.fetchone()
        print 'User table:%s' % result[0]
#        result=self.cursor.execute('SELECT * from %s' % self.repository_info_table_name)
#        for row in result:
#            repos=Repository(row[0])
#            repos.get_from_db(row)
#            print repos.all_info_str()

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
                try_time=0
                while repos.contributors==0 and try_time<1:
                    repos.crawling_details()
                    try_time+=1
                if not repos.is_empty_info():
                    self.insert_repository(repos)
                visited_repos_href.add(repos.href)
            index+=1
            if index%1000==0:
                self.commit_update()
                index=0
        self.commit_update()
        fp.close()

    def construct_user_info(self, log_path, create_new_table=True):
        if create_new_table:
            self.create_user_info_table()
        fp=open(log_path)
        visited_user_href=set()
        user_index=6
        follow_index=7
        index=0
        for line in fp.readlines():
            items=line.strip().split()
            user=User('/'+items[user_index].split(':')[-1])
            if user.href not in visited_user_href:
                user.crawling_details()
                visited_user_href.add(user.href)
#            self.insert_user(user)
            follow=User('/'+items[follow_index].split(':')[-1])
            if follow.href not in visited_user_href:
                follow.crawling_details()
                visited_user_href.add(follow.href)
#            self.insert_user(follow)
            index+=1
            if index>=1000:
                self.commit_update()
                index=0
        self.commit_update()
        fp.close()

if __name__=='__main__':
    if len(sys.argv)==2:
        db=DB_sqlite(sys.argv[1])
        db.query_repository_info()
#        db.update_contributors_in_repository_info()
    elif len(sys.argv)==2:
        repos=Repository(sys.argv[1])
        repos.crawling_details()
    else:
        db=DB_sqlite(sys.argv[1])
        if sys.argv[-1].startswith('repos'):
            db.drop_repository_info_table()
            if len(sys.argv)>3:
                db.construct_repository_info(sys.argv[2], sys.argv[3])
            elif len(sys.argv)==3:
                db.construct_repository_info(sys.argv[2])
        else:
            db.drop_user_info_table()
            db.construct_user_info(sys.argv[2])
        
