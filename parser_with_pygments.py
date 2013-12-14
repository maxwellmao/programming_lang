#~/mypython/bin/python

import os, sys
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import PhpLexer
from pygments.lexers import PerlLexer
from pygments.lexers import Python3Lexer
from pygments.lexers import RubyLexer
from pygments.lexers import CLexer
from pygments.lexers import CppLexer
from pygments.lexers import DLexer
from pygments.lexers import FortranLexer
from pygments.lexers import JavaLexer
from pygments.lexers import AdaLexer
from pygments.lexers import NasmLexer
from pygments.lexers import ErlangLexer
from pygments.lexers import HaskellLexer
from pygments.lexers import NewLispLexer
from pygments.lexers import CommonLispLexer
from pygments.lexers import LuaLexer
from pygments.lexers import MatlabLexer
from pygments.lexers import OctaveLexer
from pygments.lexers import SMLLexer
from pygments.token import Error, Text, Other, _TokenType
import stat_token_ratio
import math
import getopt

class Token:
    def __init__(self, tokenType, tokenValue):
        self.tokenType=tokenType
        self.tokenValue=tokenValue
#        print 'Init', self.tokenType, self.tokenValue

    def __str__(self):
        return '\t'.join([str(self.tokenType), str(self.tokenValue.encode('utf-8'))]).strip().replace('\n', ' ')

    __repr__=__str__

    def __hash__(self):
        return self.__str__().__hash__()
    
    def __cmp__(self, obj):
        return cmp(self.__str__(), obj.__str__())

class Parser:
    def __init__(self):
        self.globalTokens=dict()
        self.fileTokens=dict()
        self.lexerDict=dict()
        self.lexerDict['ada']=AdaLexer()
#        self.lexerDict['ads']=AdaLexer
#        self.lexerDict['adb']=AdaLexer
        self.lexerDict['asm']=NasmLexer()
        self.lexerDict['c']=CLexer()
        self.lexerDict['c++']=CppLexer()
        self.lexerDict['erlang']=ErlangLexer()
        self.lexerDict['fortran']=FortranLexer()
        self.lexerDict['haskell']=HaskellLexer()
        self.lexerDict['java']=JavaLexer()
        self.lexerDict['lisp']=CommonLispLexer()
        self.lexerDict['lua']=LuaLexer()
        self.lexerDict['matlab']=MatlabLexer()
        self.lexerDict['newlisp']=NewLispLexer()
        self.lexerDict['octave']=OctaveLexer()
        self.lexerDict['pl']=PerlLexer()
        self.lexerDict['py']=PythonLexer()
        self.lexerDict['php']=PythonLexer()
        self.lexerDict['rb']=RubyLexer()
        self.lexerDict['php']=PhpLexer()
        self.lexerDict['sml']=SMLLexer()
        self.finiteObservation=100
        self.finiteMultiplier=5
    
    def parser_file_str(self, lexer, codePath, n=1, filterToken=False):
        program_token_num=0
        all_token_num=0
        try:
            fp=open(codePath)
            code=''.join(fp.readlines())
            fp.close()
#            tokens=set([Token(k, v) for k,v in lexer.get_tokens(code)])
#            print type(tokens[0][0]), type(tokens[0][1])
#            tokensType=set([k[0] for k in tokens])
            tokenList=[]
            for k,v in lexer.get_tokens(code):
                if len(v.strip())>0:
                    tokenList.append(Token(k,v))
#            tokenList=[Token(k,v) for k, v in lexer.get_tokens(code)]
            tokenGramList=[]
            tokenSet=set()
            for token in tokenList:
                subTokenList=[Token(token.tokensType, t.name) for t in stat_token_ratio.process_code_line(str(token.tokenValue.encode('utf-8')), True)]
                num=len(subTokenList)
#                print tokenList
                all_token_num+=num
                if (not filterToken) or (str(token).startswith('Token.Keyword') or str(token).startswith('Token.Name')):
                    program_token_num+=num
#                    tokenGramList.append(token)
                    tokenGramList+=subTokenList
                    while len(tokenGramList)>=n:
                        n_gram=':'.join([str(t) for t in tokenGramList[:n]])
                        self.globalTokens[n_gram]=self.globalTokens.get(n_gram, 0)+1
                        tokenSet.add(n_gram)
                        del tokenGramList[0]
#                    self.globalTokens[token]=self.globalTokens.get(token,0)+1
            for t in tokenSet:
                self.fileTokens[t]=self.fileTokens.get(t, 0)+1
#            self.globalTokens=self.globalTokens.union(tokensType)
        except IOError, e:
            sys.stderr.write("%s, %s\n" % (codePath, e.strerror))
#        sys.stderr.write('\t'.join([str(t) for t in tokensType])+'\n')
        return all_token_num, program_token_num

    def parsing_file_and_print(self, codePath):
        lexer=self.lexerDict[codePath.split('.')[-1]]
        fp=open(codePath)
        code=''.join(fp.readlines())
        fp.close()

        tokenList=[]
        for k,v in lexer.get_tokens(code):
            if len(v.strip())>0:
                tokenList.append(Token(k,v))
#        tokenList=[Token(k,v) for k, v in lexer.get_tokens(code)]
        for token in tokenList:
            print token

    def from_repos_path(self, code_lang, repos_path, file_token_path, global_dict_path, file_size_path, n=1, filterToken=False, finite=False, threshold=-1):
        if self.lexerDict.has_key(code_lang):
#            print self.lexerDict[code_lang]
            finiteObservationPath=os.path.join(global_dict_path[:global_dict_path.rfind('/')], 'finite_observation')
            if finite and not os.path.isdir(finiteObservationPath):
                os.mkdir(finiteObservationPath)
            fp=open(repos_path, 'r')
            fileNum=0
            sizeFP=open(file_size_path, 'w')
            while True:
                lines=fp.readlines(100000)
                if not lines:
                    break
                for line in lines:
                    (all_token, program_token)=self.parser_file_str(self.lexerDict[code_lang], line.strip(), n, filterToken)
                    sizeFP.write('%s %d:%d\n' % (line.strip(), all_token, program_token))
                    fileNum+=1
                    if finite:
                        if len(self.globalTokens)>=self.finiteObservation:
                            typeStr=''
                            if filterToken:
                                typeStr='-'+str(n)+'_gram'
                            wp=open(os.path.join(finiteObservationPath, '-'.join(['file_token_pygment'+typeStr, str(self.finiteObservation)])), 'w')
                            wp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in self.fileTokens.items()]))
                            wp.close()
                            wp=open(os.path.join(finiteObservationPath, '-'.join(['token_dict_pygment'+typeStr, str(self.finiteObservation)])), 'w')
                            wp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in self.globalTokens.items()]))
                            wp.close()
                            self.finiteObservation*=self.finiteMultiplier
                            if self.finiteMultiplier==2:
                                self.finiteMultiplier=5
                            else:
                                self.finiteMultiplier=2
                            sys.stderr.write('Finite: %d\n' % self.finiteObservation)
                if threshold>0 and fileNum>=threshold:
                    break
            fp.close()
            sizeFP.close()
            wp=open(global_dict_path, 'w')
            wp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in self.globalTokens.items()]))
            wp.close()
            wp=open(file_token_path, 'w')
            wp.write('\n'.join(['\t'.join([str(k), str(v)]) for k, v in self.fileTokens.items()]))
            wp.close()

    def filter_name(self, fPath):
        nameToken=dict()
        if os.path.isfile(fPath):
            fp=open(fPath)
            while True:
                lines=fp.readlines(10000)
                if not lines:
                    break
                for line in lines:
                    if line.startswith('Token.Name') or line.startswith('Token.Keyword'):
                        item=line.strip().split()
                        if len(item)==3:
                            for t in item[1].split('.'):
                                for q in t.split(':'):
                                    if len(q.strip())>0:
                                        nameToken[q]=nameToken.get(q, 0)+int(item[-1])
                        elif len(item)==2:
                            for t in item[1].split('.'):
                                for q in t.split(':'):
                                    if len(q.strip())>0:
                                        nameToken[q]=nameToken.get(q, 0)+1
                        else:
                            sys.stderr.write(line)
            print '\n'.join(['\t'.join([str(item[0]), str(item[1])]) for item in sorted(nameToken.items(), key=lambda x:x[1])])
            fp.close()

def usage():
    print 'parser_with_pygments '
    print '-l language'
    print '-i inputPath(repos path)'
    print '-o output dir'
    print '-n n_gram'
    print '-f whether filter out comments/literal or not'
    print '-h involving finite horizon observation'

if __name__=='__main__':
    parser=Parser()
    optlist, arg=getopt.getopt(sys.argv[1:], 'l:i:o:n:fht:s:')
    n=1
    filterToken=False
    finiteObservation=False
    threshold=-1
    for opt in optlist:
        if opt[0].startswith('-i'):
            inputPath=opt[1]
        elif opt[0].startswith('-o'):
            outputPath=opt[1]
        elif opt[0].startswith('-l'):
            codeLang=opt[1]
        elif opt[0].startswith('-n'):
            n=int(opt[1])
        elif opt[0].startswith('-f'):
            filterToken=True
        elif opt[0].startswith('-h'):
            finiteObservation=True
        elif opt[0].startswith('-t'):
            threshold=int(opt[1])
        elif opt[0].startswith('s'):
            file_size_path=opt[1]
    if len(sys.argv)>5:
        if filterToken:
            parser.from_repos_path(codeLang, inputPath, os.path.join(outputPath, '-'.join(['file_token_pygments', '_'.join([str(n), 'gram'])])), os.path.join(outputPath, '-'.join(['token_dict_pygments', '_'.join([str(n), 'gram'])])), os.path.join(outputPath, 'file_size'), n, filterToken, finiteObservation, threshold)
        else:
            parser.from_repos_path(codeLang, inputPath, os.path.join(outputPath, 'file_token_pygments'), os.path.join(outputPath, 'token_dict_pygments'), os.path.join(outputPath, 'file_size'), n, filterToken, finiteObservation, threshold)
    elif len(sys.argv)==2:
        parser.filter_name(sys.argv[1])
#    elif len(sys.argv)==2:
#        parser.parsing_file_and_print(sys.argv[1])
