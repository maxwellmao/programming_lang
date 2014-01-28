#!/usr/bin/python
from __future__ import division
import os, sys
from pymongo import Connection
import codecs
'''
identifying files that users touch
'''

def touch_file_stat():
    fp=codecs.open('results/UserTouchFiles', 'w', encoding='utf-8')
    for result in db.commits.find():
        if result.has_key('files'):
            if result['committer'] is not None:
                userInfo='committer-login:%s %s' % (result['committer'].get('login', 'null'), result['committer'].get('id', 'null'))
            elif result['author'] is not None:
                userInfo='author-login:%s %s' % (result['author'].get('login', 'null'), result['author'].get('id', 'null'))
            elif result['commit'].get('committer', None) is not None:
                userInfo='committer-name:%s %s' % (result['commit']['committer'].get('name', 'null').replace(' ', '-'), result['commit']['committer'].get('email', 'null'))
            elif result['commit'].get('author', None) is not None:
                userInfo='author-name:%s %s' % (result['commit']['author'].get('name', 'null').replace(' ', '-'), result['commit']['author'].get('email', 'null'))
            else:
                userInfo='null null'
#            commiter=result['commit']['committer']
            for change_file in result['files']:
                repo_info=result['url'].replace('https://api.github.com/repos', '')
                fp.write(repo_info)
                fp.write(' ')
                fp.write(userInfo)
                fp.write(' ')
                fp.write(change_file.get('filename', 'null'))
                fp.write(' ')
                fp.write(str(change_file.get('additions', -1)))
                fp.write(' ')
                fp.write(str(change_file.get('deletions', -1)))
                fp.write('\n')
    fp.close()
#        print 'yes'

if __name__=='__main__':
    con=Connection()
    db=con.msr14
    db.authenticate('msr14', 'msr14')
    touch_file_stat()
