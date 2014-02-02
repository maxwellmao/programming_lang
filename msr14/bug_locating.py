#!/usr/bin/python
from __future__ import division
import urllib2
import os, sys
from bs4 import BeautifulSoup
from multiprocessing import Pool as ProcessPool
from pymongo import Connection
import logging
import codecs

MAX_TRY_TIME=20

def crawling_commit_info(commit_info_td):
    '''
        finding the author of each line of code in blame pages
    '''
    author_info=''
    commit_sha=''
    for a_info in commit_info_td.code.findAll('a'):
        if a_info.attrs.has_key('rel') and a_info.attrs['rel']=='author':
            author_info=a_info.attrs['href'].split('/')[-1]
        elif a_info.attrs.has_key('href') and a_info.attrs['href'].find('commit')>-1:
            commit_sha=a_info.attrs['href'].split('/')[-1]
            
#    for a_info in commit_info_td.code.findAll('a', {'rel':'author'}):
#        author_info=a_info.attrs['href'].split('/')[-1]
    if len(author_info)==0:
        for s_info in commit_info_td.code.findAll('span', {'rel':'author'}):
            author_info=s_info.contents[0]
#    print author_info
    return author_info, commit_sha


def finding_change_introducer(repo_url, current_commit_sha, previous_commit_sha, filename, tracing_lineno_set, fixer, logger):
    '''
        finding the author of previous version of code, can be used to find the bug introducer
    '''
    blame_url=os.path.join(repo_url, 'blame', previous_commit_sha, filename)
    failure=True
    try_time=0
    print blame_url
#    print 'Line no:', tracing_lineno_set
    while failure and try_time<MAX_TRY_TIME:
        try:
            req=urllib2.urlopen(blame_url)
            soup=BeautifulSoup(req.read())
            for code_table in soup.findAll('table', {'class':'file-code file-blame js-blame-heat'}):
                current_author=''
                for tr in code_table.findAll('tr'):
                    if tr.attrs.has_key('class'):
                        for commit_td in tr.findAll('td', {'class':'commitinfo'}):
                            current_author, bug_commit_sha=crawling_commit_info(commit_td)
#                    print current_author, commit_td
                    for code_td in tr.findAll('td', {'class':'diff-line-num line-number'}):
                        lineno=int(code_td.contents[0])
#                        print current_author, lineno
                        if len(tracing_lineno_set)==0 or lineno in tracing_lineno_set:
                            if logger is None:
                                print 'Current-sha:%s BugIntroducing-sha:%s File-name:%s Line-no:%s Introducer:%s Fixer:%s' % (current_commit_sha, bug_commit_sha, filename, lineno, current_author, fixer)
                            else:
                                logger.info('Current-sha:%s BugIntroducing-sha:%s File-name:%s Line-no:%s Introducer:%s Fixer:%s' % (current_commit_sha, bug_commit_sha, filename, lineno, current_author, fixer))
            failure=False
        except urllib2.URLError as e:
            sys.stderr.write('%s\n' % e)
            try_time+=1


def identifying_changing_line_no(patch):
    '''
        identifying the start line of add/del from the string like,
        @@ -0,0 +1 1,3 @@
    '''
    add_line_list=[]
    del_line_list=[]
    patch_list=patch.split('\n')
#    stat_del=int(patch_list[0].split()[1].split(',')[1])
#    stat_add=int(patch_list[0].split()[2].split(',')[1])
    count_add_line=0
    count_del_line=0
    current_del_line=0
    current_add_line=0
    for line in patch_list:
        if line.startswith('@@') and line.find('@@')!=line.rfind('@@'):
#            print line
            current_del_line=int(line.split()[1].split(',')[0][1:])
            current_add_line=int(line.split()[2].split(',')[0][1:])
        elif line.startswith('+'):
            add_line_list.append(current_add_line)
            current_add_line+=1
            count_add_line+=1
        elif line.startswith('-'):
            del_line_list.append(current_del_line)
            current_del_line+=1
            count_del_line+=1
        else:
            current_add_line+=1
            current_del_line+=1
#    print 'Counting add line: %s, counting del line: %s' % (count_add_line, count_del_line)
#    print 'Stat add line: %s, stat del line: %s' % (stat_add, stat_del)
#    if count_add_line!=stat_add or count_del_line!=stat_del:
#        print 'Error when parsing patch'
#    print add_line_list
#    print del_line_list
    return add_line_list, del_line_list

def identifying_user_name(commit_result):
    if commit_result['committer'] is not None:
        userInfo=commit_result['committer'].get('login', 'null')
    elif commit_result['author'] is not None:
        userInfo=commit_result['author'].get('login', 'null')
    elif commit_result['commit'].get('committer', None) is not None:
        userInfo=commit_result['commit']['committer'].get('name', 'null')
    elif commit_result['commit'].get('author', None) is not None:
        userInfo=commit_result['commit']['author'].get('name', 'null')
    else:
        userInfo='null null'
    return userInfo

def finding_change_in_commit(sha, logger, fix_info_file=None):
    for result in db.commits.find({'sha':sha}):
        repo_url=result['html_url'][:result['html_url'].find('/commit/')]
        if result.has_key('files'):
            for change_file in result['files']:
                parent_sha=result['parents'][0]['sha']
                filename=change_file['filename']
                if change_file.has_key('patch'):
                    current_url=os.path.join(repo_url, 'blame', sha, filename)
#                    print current_url
                    add_line_list, del_line_list=identifying_changing_line_no(change_file['patch'])
                    tracing_lineno_set=set(del_line_list)
                    fixer=identifying_user_name(result)
                    try:
                        if len(tracing_lineno_set)>0:
#                            print '%s %s %s %s %s %s' % (repo_url, sha, parent_sha, filename, '-'.join([str(no) for no in tracing_lineno_set]), fixer)
                            if fix_info_file is not None:
                                fix_info_file.write('%s %s %s %s %s %s\n' % (repo_url, sha, parent_sha, filename, '-'.join([str(no) for no in tracing_lineno_set]), fixer))
                    except Exception as e:
                        print e
#                    if len(tracing_lineno_set)>0:
#                        finding_change_introducer(repo_url, sha, parent_sha, filename, tracing_lineno_set, fixer, logger)

def finding_list_of_change_in_commit(sha_list, logger):
    for sha in sha_list:
        finding_change_in_commit(sha, logger)

def single_process_identifying():
    sha_list=[]
    fix_info_file=codecs.open('results/BugFixingInfo', 'w', 'utf-8')
    for line in sys.stdin:
        finding_change_in_commit(line.strip().split()[0], logging.getLogger('BugLocating'), fix_info_file)
    fix_info_file.close()

def single_line_fixing_info(line_list, i):
    logger = logging.getLogger('Fixing-list-%s' % i)
    for line in line_list:
        item=line.strip().split()
        fixer=' '.join(item[5:])
        tracing_set=set([int(no) for no in item[4].split('-')])
        finding_change_introducer(item[0], item[1], item[2], item[3], tracing_set, fixer, logger)

def reading_from_fixing_info_file():
    fix_info_file=codecs.open('results/BugFixingInfo', 'r', 'utf-8')
    all_line=[]
    for line in fix_info_file.readlines():
        all_line.append(line.strip())
    fix_info_file.close()
    allocating_to_multi_process(all_line)

def allocating_to_multi_process(all_line, N=40):
    pool=ProcessPool(N)
    num_per_process=int((len(all_line)-1)/N)+1
    for i in range(N):
        sub_list=[line for line in all_line[i*num_per_process:(i+1)*num_per_process]]
        pool.apply_async(single_line_fixing_info, (sub_list, i, ))
    pool.close()
    pool.join()


def multi_processes_identifying(N=40):
    '''
        run it as multi-processes, N is the number of processors
    '''
    pool=ProcessPool(N)
    sha_list=[]
    for sha in sys.stdin:
        sha_list.append(sha.strip())
    sha_num_per_process=int((len(sha_list)-1)/N)+1
    for i in range(N):
        sub_list=sha_list[i*sha_num_per_process:(i+1)*sha_num_per_process]
        logger = logging.getLogger('SHA-list-%s' % i)
        pool.apply_async(finding_list_of_change_in_commit, (sub_list, logger, ))
    pool.close()
    pool.join()

if __name__=='__main__':
    logging.basicConfig(filename='results/BugIntroducerFixerFromFile.log', level = logging.DEBUG, filemode='w', format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
#    multi_processes_identifying()
    con=Connection()
    db=con.msr14
    db.authenticate('msr14', 'msr14')
#    single_process_identifying()
    con.close()
    reading_from_fixing_info_file()
#    finding_change_introducer('https://github.com/TrinityCore/TrinityCore', '', '839abe4dca9ae326b7c8397212318d98acdbcb05', 'src/server/scripts/Spells/spell_paladin.cpp', set(), '', None)
#    finding_change_in_commit('1fc4ebb302cc50ba0f5f9cad73f1437a510e8e1d', logging.getLogger('crawler-1'))
#    finding_change_in_commit('f8ca5aaa9b070ecff4d43c71e44a19c0cf4fdab6', logging.getLogger('crawler-1'))

