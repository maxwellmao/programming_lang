#!~/usr/bin/python
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
        self.logger=logging.getLogger('_'.join(['ProjectStat', proj_dir.split('/')[-1]]))
   
    def add_file(self, code_path):
        for token in parse_file_str(self.lexer, code_path):
            if token.startswith('Program:'):
                self.program_corpus[token]=self.program_corpus.get(token, 0)+1
            self.all_corpus[token]=self.all_corpus.get(token, 0)+1

    def del_file(self, code_path):
        for token in parse_file_str(self.lexer, code_path):
            if token.startswith('Program:'):
#                current_num=self.program_corpus.get(token, 0)
#                if current_num==0:
#                    print code_path
#                    print self.proj_dir
                self.program_corpus[token]=self.program_corpus[token]-1
                if self.program_corpus[token]==0:
                    del self.program_corpus[token]
            
#            current_num=self.all_corpus.get(token, 0)
#            if current_num==0:
#                print code_path
#                print self.proj_dir
            self.all_corpus[token]=self.all_corpus[token]-1
            if self.all_corpus[token]==0:
                del self.all_corpus[token]

    def incremental_parse(self, last_commit, new_commit):
#        file_list, allNum, programNum=new_commit.find_change_files()
#        print new_commit
        self.logger.info('Parsing commit %s whose parent is %s' % (new_commit.commit_sha, last_commit.commit_sha))
        file_list=new_commit.find_change_files(self.ext)
        for code_path in file_list:
#            if code_path.endswith('LoggingStore.java'):
#                print 'Modify LogingStore.java', last_commit
#                print 'Modify LogingStore.java', new_commit
            if len(last_commit.commit_sha)>0:
                self.del_file(os.path.join(self.proj_dir, 'previous_commits', last_commit.commit_sha, code_path))
            self.add_file(os.path.join(self.proj_dir, 'previous_commits', new_commit.commit_sha, code_path))

        commit_stat=CommitStat(sum(self.all_corpus.values()), sum(self.program_corpus.values()), len(self.all_corpus), len(self.program_corpus))
        self.commit_stat_dict[new_commit.commit_sha]=commit_stat
#        print new_commit.commit_sha
        return commit_stat
