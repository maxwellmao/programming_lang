#!~/usr/bin/python
from __future__ import division
import os, sys
sys.path.append('..')
import random
from crawling_github import Repository
import logging
import datetime
import matplotlib.pyplot as plt
from parser_with_pygments import Parser
import stat_token_ratio
import token_parser
import parser_with_pygments
import logging
import subprocess

logging.basicConfig(filename='parse_branch.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')

def parse_file_str(lexer, codePath, n=1, filterToken=True):
    try:
        retlist=[]
        if not os.path.isfile(codePath):
            return retlist
        fp=open(codePath)
        code=''.join(fp.readlines())
        fp.close()
        tokenList=[]
        allNum=0
        programNum=0
        for k,v in lexer.get_tokens(code):
            if len(v.strip())>0:
                tokenList.append(parser_with_pygments.Token(k,v))
        tokenGramList=[]
        for token in tokenList:
            subTokenDict=dict([parser_with_pygments.Token(token.tokenType, t[0]), t[1]] for t in stat_token_ratio.process_code_line(str(token.tokenValue.encode('utf-8')), True).items())
            allNum+=sum(subTokenDict.values())
#            if str(token).startswith('Token.Keyword') or str(token).startswith('Token.Name'):
            for t, num in subTokenDict.items():
                tokenGramList+=[t]*num
            while len(tokenGramList)>=n:
                n_gram=':'.join([str(t.tokenValue) for t in tokenGramList[:n]])
                if str(tokenGramList[0]).startswith('Token.Keyword') or str(tokenGramList[0]).startswith('Token.Name'):
                    n_gram=':'.join(['Program', n_gram])
                retlist.append(n_gram)
                del tokenGramList[0]
                programNum+=1
    except IOError, e:
        sys.stderr.write('%s, %s\n' % (codePath, e.strerror))
    return retlist

class CommitStat:
    def __init__(self, all, program, uniq_all, uniq_program):
        self.all_tokens_num=all
        self.program_tokens_num=program
        self.uniq_all_num=uniq_all
        self.uniq_program_num=uniq_program

    def __str__(self):
        return '%s\t%s\t%s\t%s' % (self.uniq_all_num, self.all_tokens_num, self.uniq_program_num, self.program_tokens_num)

    __repr__=__str__

class ProjectStat:
    def __init__(self, proj_dir, lang, ext):
        self.proj_dir=proj_dir
        self.all_corpus=dict()
        self.program_corpus=dict()
        parser=Parser()
        self.lexer=parser.lexerDict[lang]
        self.ext=ext
        self.current_all_tokens=0
        self.current_program_tokens=0
        self.commit_stat_dict=dict()
        self.files_modified_time=dict()
        self.logger=logging.getLogger('_'.join(['ProjectStat', proj_dir.split('/')[-1]]))


    def commit_stat(self, commit_sha):
        '''
            Statistics on specified commit
        '''
#        for root, dir, files in os.walk(os.path.join(self.proj_dir, 'previous_commits', commit_sha)):
        for root, dir, files in os.walk(os.path.join(self.proj_dir, commit_sha)):
            for file in files:
                if file.endswith(self.ext):
                    all_num, program_num=self.add_file_only_num(os.path.join(root, file))
                    print '%s\t%s:%s\t%s' % (os.path.join(root, file), all_num, program_num, os.path.getsize(os.path.join(root, file)))
   

    def add_file(self, code_path):
        '''
            Statistics on new adding files of new commits
        '''
        all_num=0
        program_num=0
        for token in parse_file_str(self.lexer, code_path):
            if token.startswith('Program:'):
                self.program_corpus[token]=self.program_corpus.get(token, 0)+1
                program_num+=1
            self.all_corpus[token]=self.all_corpus.get(token, 0)+1
            all_num+=1
        self.files_modified_time[code_path]=self.files_modified_time.get(code_path, 0)+1
        return program_num, all_num

    def add_file_only_num(self, code_path):
        '''
            Similar to the function 'add_file', only statistic on number however
        '''
        all_num=0
        program_num=0
        for token in parse_file_str(self.lexer, code_path):
            if token.startswith('Program:'):
                program_num+=1
            all_num+=1
        return program_num, all_num

    def del_file(self, code_path):
        '''
            Statistics on modifying files of previous commits
        '''
        all_num=0
        program_num=0
        for token in parse_file_str(self.lexer, code_path):
            try:
                if token.startswith('Program:'):
                    self.program_corpus[token]=self.program_corpus[token]-1
                    program_num+=1
                    if self.program_corpus[token]==0:
                        del self.program_corpus[token]
                self.all_corpus[token]=self.all_corpus[token]-1
                all_num+=1
                if self.all_corpus[token]==0:
                    del self.all_corpus[token]
            except KeyError, e:
                print e
                print code_path
        return program_num, all_num

    def del_file_only_num(self, code_path):
        '''
            Similar to the function 'del_file', only statistic on number however
        '''
        all_num=0
        program_num=0
        for token in parse_file_str(self.lexer, code_path):
            if token.startswith('Program:'):
                program_num+=1
            all_num+=1
        return program_num, all_num

    def heap_law_parse(self, commit):
        self.all_corpus=dict()
        self.program_corpus=dict()
        for root, dir, files in os.walk(os.path.join(self.proj_dir, 'previous_commits', commit.commit_sha)):
            for file in files:
                if file.endswith(self.ext):
                    code_path=os.path.join(root, file)
                    for token in parse_file_str(self.lexer, code_path):
                        if token.startswith('Program:'):
                            self.program_corpus[token]=self.program_corpus.get(token, 0)+1
                        self.all_corpus[token]=self.all_corpus.get(token, 0)+1
                    self.files_modified_time[code_path]=self.files_modified_time.get(code_path, 0)+1
        commit_stat=CommitStat(sum(self.all_corpus.values()), sum(self.program_corpus.values()), len(self.all_corpus), len(self.program_corpus))
#        self.commit_stat_dict[commit.commit_sha]=commit_stat
        print commit_stat

    def heap_law_incremental_parse(self, last_commit, new_commit):
        self.logger.info('Parsing commit %s whose parent is %s' % (new_commit.commit_sha, last_commit.commit_sha))
        file_list=new_commit.find_change_files(self.ext)
        for code_path in file_list:
            if len(last_commit.commit_sha)>0:
                self.del_file(os.path.join(self.proj_dir, 'previous_commits', last_commit.commit_sha, code_path))
            self.add_file(os.path.join(self.proj_dir, 'previous_commits', new_commit.commit_sha, code_path))

        commit_stat=CommitStat(sum(self.all_corpus.values()), sum(self.program_corpus.values()), len(self.all_corpus), len(self.program_corpus))
        self.commit_stat_dict[new_commit.commit_sha]=commit_stat
#        print new_commit.commit_sha
        return commit_stat

    def token_word_freq_doc_freq_stat(self, commit_sha):
        word_freq=dict()
        doc_freq=dict()
        for root, dir, files in os.walk(os.path.join(self.proj_dir, 'previous_commits', commit_sha)):
            for file in files:
                if file.endswith(self.ext) and os.path.isfile(os.path.join(root, file)):
                    sys.stderr.write('Parsing: %s\n' % os.path.join(root, file))
                    retlist=parse_file_str(self.lexer, os.path.join(root, file))
                    token=set(retlist)
                    for t in retlist:
                        word_freq[t]=word_freq.get(t, 0)+1
                    for t in token:
                        doc_freq[t]=doc_freq.get(t, 0)+1
        return word_freq, doc_freq


    def token_num_increment_parse(self, last_commit, new_commit):
        '''
            gauge the multiplicative factors of incremental of file sizes, here the file size means the number of tokens in files, including two kinds of sizes, all tokens and program-only token
        '''
        self.logger.info('Parsing commit %s whose parent is %s' % (new_commit.commit_sha, last_commit.commit_sha))
        file_list=new_commit.find_change_files(self.ext)
        old_all=0
        old_program=0
        new_all=0
        new_program=0
        for code_path in file_list:
            if len(last_commit.commit_sha)>0:
                old_program, old_all=self.del_file_only_num(os.path.join(self.proj_dir, 'previous_commits', last_commit.commit_sha, code_path))
            new_program, new_all=self.add_file_only_num(os.path.join(self.proj_dir, 'previous_commits', new_commit.commit_sha, code_path))
            factors=[]
            if old_all!=0:
                factors.append(new_all/old_all)
            else:
                factors.append(-1)
    
            if old_program!=0:
                factors.append(new_program/old_program)
            else:
                factors.append(-1)
            print '%s\t%s' % (code_path, '\t'.join([str(f) for f in factors]))

    def file_size_increment_parse(self, last_commit, new_commit):
        '''
            gauge the multiplicative factors of incremental of file sizes, here the file size means the size of file in file system
        '''
        self.logger.info('Parsing commit %s whose parent is %s' % (new_commit.commit_sha, last_commit.commit_sha))
        file_list=new_commit.find_change_files(self.ext)
        old_size=0
        new_size=0
        for code_path in file_list:
            if len(last_commit.commit_sha)>0:
                old_file=os.path.join(self.proj_dir, 'previous_commits', last_commit.commit_sha, code_path)
                if os.path.isfile(old_file):
                    old_size=os.path.getsize(old_file)
            new_file=os.path.join(self.proj_dir, 'previous_commits', new_commit.commit_sha, code_path)
            if os.path.isfile(new_file):
                new_size=os.path.getsize(new_file)
#        print 'Old size:%s new size:%s' % (old_size, new_size)
            if old_size==0:
                print code_path, -1
            else:
                print code_path, new_size/old_size

    def project_size_parse(self, last_commit, new_commit):
        '''
            gauge the multiplicative factors of incremental of file sizes of whole project, here the file size means the size of file in file system
        '''
        if len(last_commit.commit_sha)>0:
            p = subprocess.Popen(['du', '-bs', os.path.join(self.proj_dir, 'previous_commits', last_commit.commit_sha)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            last_proj_size=int(out.split()[0])
            p = subprocess.Popen(['du', '-bs', os.path.join(self.proj_dir, 'previous_commits', new_commit.commit_sha)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            new_proj_size=int(out.split()[0])
#        sys.stderr.write('Commit:%s\n' % last_commit.commit_sha)
            print '%s\t%s\tLast:%s\tNew:%s\tFactor:%.6f' % (last_commit.commit_sha, new_commit.commit_sha, last_proj_size, new_proj_size, new_proj_size/last_proj_size)
