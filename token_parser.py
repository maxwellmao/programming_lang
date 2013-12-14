#!~/mypython/bin/python
import os, sys
import pycparser
(_normal, _entity, _number, _comment, _inString, _define, _header, _operator)=range(8)
#string type
(_single, _double, _trible)=range(3)
#token type, the environment of current token

#(_var, _fun, _type, _constant, _misc)=range()

def isOperator(c):
    op=set(['+', '-', '*', '/', '%', '~', '&', '|', '^', '=', '<', '>', '?', ':', '!'])
    return c in op

def isParentheses(c):
    par=set(['(', ')', '{', '}', '[', ']'])
    return c in par

#means new token starts, except for number
def isPunctuation(c):
    punc=set([',', ';', ' ', '.'])
    return c in punc

def isStringIndicator(c):
    return c=='\'' or c=='\"'

def isEntity(c):
    return c.isalpha() or c=='_'

def isMeaningless(c):
    mean=set(['@', '$', '`', '#'])
    return c in mean

def isBiCharOp(c):
    op=set(['==', '!=', '<=',  '&&' , '~=', '||', '::' , '<<' , '>>', '>=', '++', '--', '-=', '+=', '*=', '/=', '%=', '^=', '&=', '|=', '//', '/*', '*/'])
    return c in op

class Token:
    def __init__(self, t, name):
        self.env=t
        self.name=name
    
    def __hash__(self):
        return hash(self.name)

    def __cmp__(self, obj):
        return cmp(self.name, obj.name)

    def __eq__(self, obj):
        return self.name==obj.name

class Parser(object):
    def __init__(self, tokenDict=None, totalNum=0, uniqNo=0, heapLaw=False):
        self.omitNumber=False
        self.reserveComment=False
        if tokenDict is not None:
            self.globalTokenDict=tokenDict
        else:
            self.globalTokenDict=dict()
        self.totalAppearNo=totalNum
        self.uniqueAppearNo=uniqNo
        self.generateHeapLaw=heapLaw
#        sys.stderr.write('init\n')

    def parse_line(self, line):
        token=[]
#        for i in xrange(len(line)):
        pass

    def set_omit_number(self, omit):
        self.omitNumber=omit

    def set_reserve_comment(self, omit):
        self.reserveComment=omit

    def add_token(self, token):
        if token is not None and token.name is not None and len(token.name)>0 and not token.name.isspace():
            lastNum=len(self.globalTokenDict)
            if self.omitNumber:
                if not token.name[0].isdigit():
                    if self.generateHeapLaw:
                        self.totalAppearNo+=1
                        self.globalTokenDict[token.name]=self.globalTokenDict.get(token.name, 0)+1
                        if lastNum!=len(self.globalTokenDict):
                            self.uniqueAppearNo+=1
                        print self.totalAppearNo, self.uniqueAppearNo
                    self.fileToken[token.name]=self.fileToken.get(token.name, 0)+1
            else:
                if self.generateHeapLaw:
                    self.totalAppearNo+=1
                    self.globalTokenDict[token.name]=self.globalTokenDict.get(token.name, 0)+1
                    if lastNum!=len(self.globalTokenDict):
                        self.uniqueAppearNo+=1
                        print self.totalAppearNo, self.uniqueAppearNo
                self.fileToken[token.name]=self.fileToken.get(token.name, 0)+1

    def parse_file(self, filePath):
        try:
            fp=open(filePath)
            fileToke=dict()
            lineNo=1
            while True:
                lines=fp.readlines(10000)
                if not lines:
                    break
                for line in lines:
                    line=line.strip()
                    self.parse_line(line)
#                    print 'LineNo:', lineNo
                    lineNo+=1
            fp.close()
        except IOError as e:
            sys.stderr.write(str(e)+'\n')

class Naive_Parser(Parser):
    def __init__(self, globalToken=None, totalNum=0, uniqNo=0, heapLaw=False):
        super(Naive_Parser, self).__init__(globalToken, totalNum, uniqNo, heapLaw)
        self.fileToken=dict()
        self.verbose=False
        self.hasToken=False
        self.state=_normal
        self.omitNumber=False
        self.reserveComment=True

    def set_file_path(self, p):
        self.file_path=p

    def parse_line(self, line):
        lastC=None
        currentToken=Token(None, '')
        self.hasToken=False
        isEscape=False
        for i in xrange(len(line)):
            if isEscape:
                currentToken.name+=line[i]
                lastC=''
                self.add_token(currentToken)
                currentToken=Token(self.state, '')
                isEscape=False
                continue
            elif line[i]=='\\':
                self.add_token(currentToken)
                if i<len(line)-1:
                    isEscape=True
                    currentToken=Token(self.state, '')
                else:
                    self.add_token(Token(self.state, '\\'))
            elif isEntity(line[i]) or line[i].isdigit():
                if lastC is not None and not isEntity(lastC) and not lastC.isdigit():
                    self.add_token(currentToken)
                    currentToken=Token(self.state, '')
            elif isParentheses(line[i]) or isPunctuation(line[i]) or isMeaningless(line[i]) or line[i].isspace()or isStringIndicator(line[i]) or isOperator(line[i]):
                self.add_token(currentToken)
                currentToken=Token(self.state, '')
#            elif isStringIndicator(line[i]):
#                if lastC is not None and line[i-1]!=line[i]:
#                    self.add_token(currentToken)
#                    currentToken=Token(self.state, '')
#                if i>=len(line)-1 or not line[i]!=line[i+1]:
#                    currentToken.name+=line[i]
#                    self.add_token(currentToken)
#                    currentToken=Token(self.state, '')
#                    continue
            elif isOperator(line[i]):
                self.add_token(currentToken)
                currentToken=Token(self.state, '')
            else:
                sys.stderr.write(line[i]+'\n')
            if not line[i].isspace():
                currentToken.name+=line[i]
#                if isOperator(currentToken.name) and isBiCharOp()
            lastC=line[i]
        self.add_token(currentToken)


class Python_Parser(Parser):
    def __init__(self):
        self.state=_normal
        self.fileToken=dict()
        self.stringIndicator=''
        self.verbose=False
        self.hasToken=False

    def set_file_path(self, p):
        self.file_path=p

    
    def deal_with_comment(self, currentToken):
        if self.reserveComment:
            self.add_token(currentToken)
            return
        if self.verbose:
            sys.stderr.write('String Indicator: '+self.stringIndicator)
        strAbbr=''
#        if currentToken.name.find('\'')!=-1:
#            if len(currentToken)%2==0:
#                currentToken.name=''
#            else:
#                strAbbr='\''
#        elif currentToken.name.find('\"')!=-1:
        if len(currentToken.name)%2==0:
            currentToken.name=''
        else:
            if len(currentToken.name)>=3:
                strAbbr=''.join([currentToken.name[1] for i in range(3)])
            else:
                strAbbr=currentToken.name[0]
        #if len(self.stringIndicator)==0:
        #    self.stringIndicator=strAbbr
        #else:
        if self.stringIndicator==strAbbr:
            self.state=_normal
            self.add_token(Token(_normal, self.stringIndicator))
            self.add_token(Token(_normal, self.stringIndicator))
            self.stringIndicator=''
        elif len(self.stringIndicator)==0:
            self.stringIndicator=strAbbr
            self.state=_inString
        else:
            if len(self.stringIndicator)==1 and len(strAbbr)==3 and strAbbr[0]==self.stringIndicator[0]:
                self.state=_normal
                self.add_token(Token(_normal, self.stringIndicator))
                self.add_token(Token(_normal, self.stringIndicator))
                self.stringIndicator=''
        if self.verbose:
            sys.stderr.write('strAbbr: '+strAbbr+'\n')

    def parse_line(self, line):
        lastC=None
        currentToken=Token(None, '')
        self.hasToken=False
        isEscape=False
        if self.state==_inString:
            if len(self.stringIndicator)<3:
                self.state=_normal
                self.stringIndicator==''
#        print line
        if self.verbose:
            sys.stderr.write('Line: '+line+'\n')
            print self.state
#            print '(',self.fileToken.get('(', 0)
#            print ')',self.fileToken.get(')', 0)
#            print self.fileToken.keys()
#            print 'Line string indicator:', self.stringIndicator
        for i in xrange(len(line)):
            if isEscape:
                currentToken.name+=line[i]
                lastC=''
                self.add_token(currentToken)
                currentToken=Token(self.state, '')
                isEscape=False
                continue
            elif line[i]=='\\':
                if i!=len(line)-1:
                    self.add_token(currentToken)
                    isEscape=True
                    currentToken=Token(self.state, '')
                else:
                    continue
            elif not self.reserveComment and (self.state==_inString or isStringIndicator(line[i])):
                if self.state!=_inString:
                    self.state=_inString
                    self.add_token(currentToken)
                    currentToken=Token(_inString, '')
                if isStringIndicator(line[i]):
                    currentToken.name+=line[i]
                    if i==len(line)-1 or line[i]!=line[i+1]:
                        if self.verbose:
                            sys.stderr.write('Deal with '+currentToken.name+'\n')
                            sys.stderr.write(self.stringIndicator+'\n')
                        self.deal_with_comment(currentToken)
                        currentToken.name=''
#                    if line[i]==lastC:
#                        currentToken.name+=line[i]
#                    else:
#                        if not isStringIndicator(lastC):
#                            currentToken.name=line[i]
#                        else:
#                            if self.stringIndicator.find(line[i])!=-1:
#                                self.deal_with_comment(currentToken)
#                                if self.state==_normal:
#                                    currentToken.name=line[i]
#                                    self.state=_inString
#                            else:
#                                currentToken.name=line[i]
                else:
                   # if len(self.stringIndicator)==0:
#                    if isStringIndicator(lastC):
#                        self.deal_with_comment(currentToken)
                    currentToken.name=''
                lastC=line[i]
                continue
            elif line[i]=='#':
                self.state=_comment
                if currentToken.env is not None:
                    self.add_token(currentToken)
                currentToken=Token(self.state,'')
                if self.hasToken:
                    return 1
                else:
                    return 0
            elif isOperator(line[i]):
                if(line[i]=='+' or line[i]=='-') and (lastC=='E' or lastC=='e') and self.state==_number:
                    lastC=line[i]
                    currentToken.name+=line[i]
                    continue
                if self.state!=_operator:
                    self.add_token(currentToken)
                    currentToken=Token(self.state, '')
                else:
#                    if lastC is None:
#                       print self.file_path
#                        print line
                    if  lastC is not None and isBiCharOp(lastC+line[i]):
                        currentToken.name+=line[i]
                        self.add_token(currentToken)
                        self.state=_normal
                        currentToken=Token(self.state, '')
                        lastC=line[i]
                        continue
                    else:
                        self.add_token(currentToken)
                        currentToken=Token(self.state, '')
                self.state=_operator
            elif isParentheses(line[i]) or isPunctuation(line[i]) or line[i].isspace():
                if line[i]!='.' or self.state!=_number:
                    self.add_token(currentToken)
                    self.state=_normal
                    currentToken=Token(self.state,'')
#            elif isStringIndicator(line[i]):
#                if line[i]!=lastC:
#                print 'String indicator', line[i]
#                self.add_token(currentToken)
#                currentToken=Token(_normal,'')
#                self.stringIndicator=''
#                self.state=_inString
            elif isEntity(line[i]):
                if (line[i]=='e' or line[i]=='E') and self.state==_number:
                    lastC=line[i]
                    currentToken.name+=line[i]
                    continue
                if lastC is not None and not isEntity(lastC) and not lastC.isdigit():
                    self.add_token(currentToken)
                    currentToken=Token(self.state, '')
                self.state=_entity
            elif line[i].isdigit():
                if self.state==_number:
                    currentToken.name+=line[i]
                    lastC=line[i]
                    continue
                if lastC is not None and lastC!='.' and not isEntity(lastC) and not lastC.isdigit():
                    self.add_token(currentToken)
                    currentToken=Token(self.state, '')
                    self.state=_number
                else:
                    self.state=_normal
            elif isMeaningless(line[i]):
                if currentToken.env is not None:
                    self.add_token(currentToken)
                currentToken=Token(self.state, line[i])
                self.add_token(currentToken)
                self.state=_normal
                currentToken=Token(self.state, '')
                lastC=line[i]
                continue
            elif isStringIndicator(line[i]):
                if lastC is not None and not isStringIndicator(line[i]):
                    self.add_token(currentToken)
                    currentToken=TOken(self.state, '')
            else:
                sys.stderr.write(line[i]+'\n')
                 #raise Exception('Unhandled token', line[i])
            if not line[i].isspace():
                currentToken.name+=line[i]
            lastC=line[i]
        self.add_token(currentToken)


if __name__=='__main__':
    parser=Naive_Parser()
    if len(sys.argv)>1:
        sys.stderr.write(str(len(sys.argv))+'\n')
        dir=sys.argv[1]
        parser.set_file_path(sys.argv[1])
        parser.verbose=True
        parser.parse_file(sys.argv[1])
    else:
        for line in sys.stdin:
            parser.parse_line(line.strip())
#    print set([k.name for k in parser.fileToken.keys()])
    for k in sorted(parser.fileToken.items(), key=lambda x:x[1]):
        print k[0], k[1]
#    for root, dirs, files in os.walk(dir):
#        for name in files:
#            if name.endswith('.py'):
#                parser=Python_Parser()
#                print os.path.join(root, name)
#                parser.parse_file(os.path.join(root, name))
