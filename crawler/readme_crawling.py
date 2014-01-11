#!/usr/bin/python
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

poolsize=40

def crawling_readme(file_path):
    '''
        Crawling the readme file of each repository
        file_path is the file with URLs of repositories
    '''
    fp=open(file_path)
    for line in fp.readlines():
        failure=True
        while failure:
            try:
                req=urllib2.urlopen(line.strip())
                result=req.read()
                soup=BeautifulSoup(result)
                art=soup.article
                failure=False
            except urllib2.HTTPError, e:
                print e
    fp.close()
