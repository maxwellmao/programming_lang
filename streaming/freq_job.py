#!/~mypython/bin/python
import os, sys
import getopt
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

class Token:
    def __init__(self, tokenType, tokenValue):
        self.tokenType=tokenType
        self.tokenValue=tokenValue

    def __str__(self):
        return '-'.join([str(self.tokenType), str(self.tokenValue.encode('utf-8'))]).strip().replace('\n', '-').replace('\t', '-').replace(' ', '-')

    __repr__=__str__

    def __hash__(self):
        return self.__str__().__hash__()
    
    def __cmp__(self, obj):
        return cmp(self.__str__(), obj.__str__())

lexerDict=dict()
lexerDict['ada']=AdaLexer()
lexerDict['asm']=NasmLexer()
lexerDict['c']=CLexer()
lexerDict['c++']=CppLexer()
lexerDict['erlang']=ErlangLexer()
lexerDict['fortran']=FortranLexer()
lexerDict['haskell']=HaskellLexer()
lexerDict['java']=JavaLexer()
lexerDict['lisp']=CommonLispLexer()
lexerDict['lua']=LuaLexer()
lexerDict['matlab']=MatlabLexer()
lexerDict['newlisp']=NewLispLexer()
lexerDict['octave']=OctaveLexer()
lexerDict['pl']=PerlLexer()
lexerDict['py']=PythonLexer()
lexerDict['php']=PythonLexer()
lexerDict['rb']=RubyLexer()
lexerDict['php']=PhpLexer()
lexerDict['sml']=SMLLexer()

def process_code_str(code_str, lexer, n=1):
    tokenList=[Token(k,v) for k, v in lexer.get_tokens(code_str)]
    tokenGramList=[]
    fileTokens=dict()
    for token in tokenList:
        if str(token).startswith('Token'):
            if str(token).startswith('Token.Keyword') or str(token).startswith('Token.Name'):
                tokenGramList.append(token)
                if len(tokenGramList)==n:
                    n_gram=':'.join([str(t) for t in tokenGramList[:n]])
                    fileTokens[n_gram]=fileTokens.get(n_gram, 0)+1
                    del tokenGramList[0]
    for k,v in fileTokens.items():
        if len(str(k).strip())>0:
            print str(k).strip(), v
#            sys.stderr.write(str(k)+'\n')

stage=''
lang=''
n=1
optlist, arg=getopt.getopt(sys.argv[1:], 'l:s:n:', ['lang=', 'stage='])
for opt in optlist:
    if opt[0].startswith('-l') or opt[0].startswith('--lang'):
        lang=opt[1].lower()
#        print lang
    elif opt[0].startswith('-s') or opt[0].startswith('--stage'):
        stage=opt[1]
#        print stage
    elif opt[0].startswith('-n'):
        n=int(opt[1])

def mapper(n, countNum=False):
    code=''
    index=0
    lexer=lexerDict[lang]
    for line in sys.stdin:
        if line.startswith('../../repository/github-repository'):
            index+=1
            if len(code)>0:
                if not countNum:
                    process_code_str(code, lexer, n)
            code=' '.join(line.split()[1:])
        else:
            code+=line
    if countNum:
        print index

def reducer():
    lastToken=''
    freq=0
    numFiles=0
    for line in sys.stdin:
        item=line.strip().split()
        if len(item)>1:
            if len(lastToken)>0 and item[0]!=lastToken:
                print lastToken, freq, numFiles
                freq=0
                numFiles=0
            lastToken=' '.join(item[:-1])
            freq+=int(item[-1])
            numFiles+=1
        else:
            sys.stderr.write(line)
    print lastToken, freq, numFiles
        

if __name__=='__main__':
    if stage.startswith('reducer'):
        reducer()
    elif stage.startswith('mapper'):
        mapper(n)
    else:
        mapper(n, True)
