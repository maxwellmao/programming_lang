#!/~mypython/bin/python

import os, sys

langDict={
#    'py':'py',
#    'pl':'pl',
#    'pm':'pl',
#    'rb':'rb',
#    'lua':'lua',
#    'wlua':'lua',
#    'asm':'asm',
#    'c':'c',
#    'h':{'c++':'c++', '/c/':'c'},
#    'hpp':'c++',
#    'cpp':'c++',
#    'java':'java',
#    'f':'fortran',
#    'f90':'fortran',
#    'adb':'ada',
#    'ads':'ada',
#    'ada':'ada',
#    'erl':'erlang',
#    'hrl':'erlang',
#    'es':'erlang',
#    'escript':'erlang',
#    'hs':'haskell',
#    'sml':'sml',
#    'sig':'sml',
#    'fun':'sml',
#    'cl':'lisp',
#    'lisp':'lisp',
#    'el':'lisp',
#    'lsp':'newlisp',
#    'nl':'newlisp',
    'php':'php',
    'php3':'php',
    'php4':'php',
    'php5':'php'
#    'm':{'matlab':'matlab', 'octave':'octave'}
}

def construct_reposity_path_db_dfs(dir, fpDict):
    fileList=[]
    for item in os.listdir(dir):
#        print os.path.join(dir, d)
        if os.path.isdir(os.path.join(dir, item)):
#            print os.path.join(dir, item)
            construct_reposity_path_db_dfs(os.path.join(dir, item), fpDict)
        else:
            fileList.append(os.path.join(dir, item))
    for file in fileList:
        if fpDict.has_key(file.split('.')[-1]):
            fpDict[file.split('.')[-1]].write(os.path.join(dir, file)+'\n')

def construct_reposity_path_db_more_dfs(dir, fpDict):
    fileList=[]
    for item in os.listdir(dir):
#        print os.path.join(dir, d)
        fPath=os.path.join(dir, item)
        if not os.path.islink(fPath) and os.path.isdir(fPath):
#            print os.path.join(dir, item)
            construct_reposity_path_db_more_dfs(fPath, fpDict)
        elif not os.path.islink(fPath) and os.path.isfile(fPath):
            fileList.append(fPath)
    for file in fileList:
#        print file
        lang=langDict.get(file.split('.')[-1], '')
        if isinstance(lang, str):
            if len(lang)>0:
                fpDict[lang].write(file+'\n')
#                print lang, os.path.join(dir, file)
        else:
            for k, v in lang.items():
                if file.lower().find(k)!=-1:
                    fpDict[v].write(file+'\n')
#                    print v, os.path.join(dir, file)
                    break

def construct_reposity_path_db(dir, fpDict):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if fpDict.has_key(file.split('.')[-1]):
                fpDict[file.split('.')[-1]].write(os.path.join(root, file)+'\n')



if __name__=='__main__':
    langSet=set()
    fpDict=dict()
    for k, v in langDict.items():
        if isinstance(v, str):
            langSet.add(v)
        else:
            for i, j in v.items():
                langSet.add(j)
    #print langSet
    if not os.path.isdir(sys.argv[2]):
        os.mkdir(sys.argv[2])

    for i in langSet:
        dirPath=os.path.join(sys.argv[2], i)+'_Path'
    #    print 'Dir:', dirPath
        if not os.path.isdir(dirPath):
            os.mkdir(dirPath)
        fPath=os.path.join(dirPath, sys.argv[3])
        fpDict[i]=open(fPath, 'w')
        print i, fPath
    construct_reposity_path_db_more_dfs(sys.argv[1], fpDict)
#    construct_reposity_path_db(sys.argv[1], fpDict)
#    construct_reposity_path_db_dfs(sys.argv[1], fpDict)
    for k, v in fpDict.items():
        v.close()
