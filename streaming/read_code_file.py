#!~/mypython/bin/pthon

import os, sys

if __name__=='__main__':
    fp=open(sys.argv[1])
    while True:
        lines=fp.readlines(10000)
        if not lines:
            break
        for line in lines:
            try:
        #        print '../../repository/github-repository'
#                print line
                print line.strip()
                rp=open('../'+line.strip())
                code_str='\n'.join([l for l in rp.readlines()])
                print code_str
                rp.close()
            except IOError,e:
#                print e
#                sys.stderr.write(str(e))
                pass
    fp.close()
