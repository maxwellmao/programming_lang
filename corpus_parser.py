#~/mypython/bin/python

import os, sys
from token_parser import Python_Parser
from token_parser import Naive_Parser
import getopt
#the type of parser
(_python, _java, _php, _js, _as, _fortran)=range(6)
(_freqInDoc, _freqInCorpus)=range(2)
class Corpus:
    def __init__(self, type, omit=True, reservecomment=False):
        self.corpus_token=dict()
        self.token_in_file=dict()
        self.docNum=0
        self.nonEmptyDoc=0
        self.set_type(type)
        self.omitNumber=omit
        self.reserveComment=reservecomment
        self.freqType=_freqInDoc
#        self.globalTokenSet=set()
        self.uniqueAppearNo=0
        self.totalAppearNo=0
        self.finiteObservation=100
        self.finiteMultiplier=5

    def set_freq_type(self, freqtype):
        self.freqType=freqtype

    def set_type(self, type):
        self.type=type
        if self.type==_python:
            self.parser=Python_Parser()
            self.ext='.py'
        elif self.type==_java:
            self.parser=Python_Parser()
            self.ext='.java'
        elif self.type==_php:
            self.parser=Python_Parser()
            self.ext='.php'
        elif self.type==_js:
            self.ext='.js'
        elif self.type==_as:
            self.ext=='.as'
        elif self.type==_fortran:
            self.ext=='.f90'
        elif self.type==_ruby:
            self.ext=='.rb'
        elif self.type==_d:
            self.ext=='.d'

    def set_ext(self, ext):
        self.ext=ext

    def whole_dir(self, dir):
        self.parser=Python_Parser()
        self.parser.set_omit_number(self.omitNumber)
        for root, dir, files in os.walk("."):
            for file in files:
                if file.endswith(self.ext):
                    self.parser.set_file_path(os.path.join(root,file))
                    self.parser.parse_file(os.path.join(root, file))
        self.docNum+=1
        for k in self.parser.fileToken.keys():
            self.corpus_token[k]=self.corpus_token.get(k, 0)+1
        self.parser.fileToken=dict()

    def from_repos_path(self, repos_path, outputPath, generateHeapLaw=False, finite=False, threshold=-1):
        fp=open(repos_path, 'r')
        finiteObservationPath=os.path.join(outputPath, 'finite_observation')
        if finite and not os.path.isdir(finiteObservationPath):
            os.mkdir(finiteObservationPath)
        fileNum=0
        while True:
            lines=fp.readlines(100000)
            if not lines:
                break
            for line in lines:
                fileNum+=1
                self.parser=Naive_Parser(self.corpus_token, self.totalAppearNo, self.uniqueAppearNo, generateHeapLaw)
#                    self.parser=Python_Parser()
#                    self.parser.set_reserve_comment(self.reserveComment)
#                    self.parser.set_omit_number(self.omitNumber)
                self.parser.set_file_path(line.strip())
                self.parser.parse_file(line.strip())
                self.corpus_token=self.parser.globalTokenDict
                self.totalAppearNo=self.parser.totalAppearNo
                self.uniqueAppearNo=self.parser.uniqueAppearNo
        #        sys.stderr.write('\t'.join([str(self.totalAppearNo), str(self.uniqueAppearNo)])+'\n')
#                    print os.path.join(root, file)
                self.docNum+=1
                    #print os.path.join(root, file)
                    #print self.parser.fileToken.keys()
                for  k, v in self.parser.fileToken.items():
                    self.corpus_token[k]=self.corpus_token.get(k, 0)+v
                    self.token_in_file[k]=self.token_in_file.get(k,0)+1
                if len(self.parser.fileToken.keys())>1:
                    self.nonEmptyDoc+=1
                self.parser.fileToken=dict()
                if finite:
                    if len(self.corpus_token)>=self.finiteObservation:
                        self.saveToken(os.path.join(finiteObservationPath, '-'.join(['corpus_token', str(self.finiteObservation)])), os.path.join(finiteObservationPath, '-'.join(['file_token', str(self.finiteObservation)])))
                        self.finiteObservation*=self.finiteMultiplier
                        if self.finiteMultiplier==2:
                            self.finiteMultiplier=5
                        else:
                            self.finiteMultiplier=2
                        sys.stderr.write('Finite: %d\n' % len(self.corpus_token))
            if threshold>0 and fileNum>=threshold:
                break

        self.saveToken(os.path.join(outputPath, 'corpus_token'), os.path.join(outputPath, 'file_token'))

    def saveToken(self, corpusPath, fileTokenPath):
        fpCorpus=open(corpusPath, 'w')
        sys.stderr.write(' '.join(['Corpus size:', str(corpus.docNum), ' Nonempty:', str(corpus.nonEmptyDoc), '\n']))
        for k in sorted(corpus.corpus_token.items(), key=lambda x:x[1]):
            fpCorpus.write('\t'.join([str(k[0]), str(k[1])])+'\n')
        fpCorpus.close()
        fpTokenInFile=open(fileTokenPath, 'w')
        for k in sorted(corpus.token_in_file.items(), key=lambda x:x[1]):
            fpTokenInFile.write('\t'.join([str(k[0]), str(k[1])])+'\n')
        fpTokenInFile.close()

    def file_as_doc(self, dir):
        for root, dir, files in os.walk(dir):
            for file in files:
                if file.endswith(self.ext):
#                    sys.stderr.write(file+'\n')
                    self.parser=Naive_Parser(self.corpus_token, self.totalAppearNo, self.uniqueAppearNo)
#                    self.parser=Python_Parser()
#                    self.parser.set_reserve_comment(self.reserveComment)
#                    self.parser.set_omit_number(self.omitNumber)
                    self.parser.set_file_path(os.path.join(root,file))
                    self.parser.parse_file(os.path.join(root, file))
                    self.corpus_token=self.parser.globalTokenDict
                    self.totalAppearNo=self.parser.totalAppearNo
                    self.uniqueAppearNo=self.parser.uniqueAppearNo
                    sys.stderr.write('\t'.join([str(self.totalAppearNo), str(self.uniqueAppearNo)])+'\n')
#                    print os.path.join(root, file)
                    self.docNum+=1
                    #print os.path.join(root, file)
                    #print self.parser.fileToken.keys()
                    for  k, v in self.parser.fileToken.items():
                        self.corpus_token[k]=self.corpus_token.get(k, 0)+v
                        self.token_in_file[k]=self.token_in_file.get(k,0)+1
                    if len(self.parser.fileToken.keys())>1:
                        self.nonEmptyDoc+=1
                    self.parser.fileToken=dict()

    def project_as_doc(self, repoLangDir):
        for root, dirs, files in os.walk(repoLangDir):
            for dir in dirs:
                for r, d, fs in os.walk(os.path.join(root, dir)):
                    for project in d:
                        self.whole_dir(os.path.join(r, project))
                    break
            break

    def language_as_doc(self, repoRootDir):
        for root, dirs, files in os.walk(repoRootDir):
            for dir in dirs:
                if dir.find('java')!=-1:
                    self.set_type(_java)
                elif dir.find('python')!=-1:
                    self.set_type(_python)
                elif dir.find('php')!=-1:
                    self.set_type(_php)
                self.whole_dir(os.path.join(root, dir))
            break

def usage():
    print 'corpus_parser'
    print '-i input path(repos path)'
    print '-o output path'
    print '-f whether involving finite horizon observation or not'
    print '-h whether generating heap\'s law or not'

if __name__=='__main__':
    corpus=Corpus(_python, omit=True, reservecomment=False)
#    corpus.project_as_doc(sys.argv[1])
    print len(sys.argv)
    if len(sys.argv)==5:
        corpus.set_ext(sys.argv[1])
        corpus.file_as_doc(sys.argv[2])
#    corpus.set_freq_type(_freqInCorpus)
        fpCorpus=open(sys.argv[3], 'w')
        sys.stderr.write(' '.join(['Corpus size:', str(corpus.docNum), ' Nonempty:', str(corpus.nonEmptyDoc), '\n']))
        for k in sorted(corpus.corpus_token.items(), key=lambda x:x[1]):
            fpCorpus.write('\t'.join([str(k[0]), str(k[1])])+'\n')
        fpCorpus.close()
        fpTokenInFile=open(sys.argv[4], 'w')
        for k in sorted(corpus.token_in_file.items(), key=lambda x:x[1]):
            fpTokenInFile.write('\t'.join([str(k[0]), str(k[1])])+'\n')
        fpTokenInFile.close()
    else:
        optlist, arg=getopt.getopt(sys.argv[1:], 'i:o:fht:')
        finiteObservation=False
        generateHeapLaw=False
        threshold=-1
        for opt in optlist:
            if opt[0].startswith('-i'):
                inputPath=opt[1]
            elif opt[0].startswith('-o'):
                outputPath=opt[1]
                if not os.path.isdir(outputPath):
                    os.mkdir(outputPath)
            elif opt[0].startswith('-f'):
                finiteObservation=True
            elif opt[0].startswith('-h'):
                generateHeapLaw=True
            elif opt[0].startswith('-t'):
                threshold=int(opt[1])
        corpus.from_repos_path(inputPath, outputPath, generateHeapLaw, finiteObservation, threshold)

    #fpHeapLaw=open(sys.argv[5], 'w')
    #fpHeapLaw.write('\n'.join(['\t'.join([str(i), str(corpus.appearList[i])]) for i in range(len(corpus.appearList))]))
    #fpHeapLaw.close()
