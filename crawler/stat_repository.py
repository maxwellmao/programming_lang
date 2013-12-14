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

def parse_file_str(self, lexer, codePath, n=1):
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
                tokenList.append(Token(k,v))
        tokenGramList=[]
        for token in tokenList:
            subTokenList=[Token(token.tokenType, t.name) for t in stat_token_ratio.process_code_line(str(token.tokenValue.encode('utf-8')), True)]
            allNum+=len(subTokenList)
            if (not filterToken) or (str(token).startswith('Token.Keyword') or str(token).startswith('Token.Name')):
                tokenGramList+=subTokenList
                while len(tokenGramList)>=n:
                    n_gram=':'.join([str(t) for t in tokenGramList[:n]])                
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
   
    def add_file(self, code_path):
        for token in parse_file_str(self.lexer, code_path):
            self.corpus[token]=self.corpus.get(token, 0)+1

    def del_file(self, code_path):
        for token in parse_file_str(self.lexer, code_path):
            self.corpus[token]=self.corpus[token]-1
            if self.corpus[token]==0:
                del self.corpus[token]

    def incremental_parse(self, last_commit_sha, new_commit):
#        file_list, allNum, programNum=new_commit.find_change_files()
        file_list=new_commit.find_change_files(self.ext)
        for code_path in file_list:
            if len(last_commit_sha)>0:
                self.del_file(os.path.join(self.proj_dir, 'previous_commits', last_commit_sha, code_path))
            self.add_file(os.path.join(self.proj_dir, 'previous_commits', new_commit.commit_sha, code_path))
        commit_stat=CommitStat(sum(self.all_corpus.values()), sum(self.program_corpus.values()), len(self.all_corpus), len(self.program_corpus))
        self.commit_stat_dict[new_commit.commit_sha]=commit_stat
        return commit_stat
