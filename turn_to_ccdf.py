#coding=gbk
import os, sys

def turn_to_cdf(savePath):
    print 'Turn to cdf'
    fp=open(savePath, 'w')
    lastIndex=-1
    cumulate=0
    for line in sys.stdin:
        item=[int(i) for i in line.strip().split()]
        if lastIndex!=-1:
            for i in xrange(lastIndex+1, item[0]):
                fp.write('\t'.join([str(i), str(cumulate)])+'\n')
        cumulate+=item[1]
        fp.write('\t'.join([str(item[0]), str(cumulate)])+'\n')
        lastIndex=item[0]
    fp.close()

def read_freq(filePath=None):
    freq=[]
    if filePath is None:
        for line in sys.stdin:
            items=line.strip().split()
            if len(items)==2:
                freq.append([int(items[0]), int(items[1])])
    else:
        rfile=open(filePath, 'r')
        while True:
            lines=rfile.readlines(10000)
            if not lines:
                break
            for line in lines:
                line=line.strip()
                items=line.split(' ')
                if len(items)==2:
                    freq.append([int(items[0]), int(items[1])])
        rfile.close()
    return freq

def turn_to_cdf(filePath, savePath):
    #the line of filePath (input file) is degree, freq
    freq=read_freq(filePath)
    if len(freq)==0:
        print filePath
        return
    wfile=open(savePath, 'w')
    cdf=[]
    lastSum=0
    lastIndex=-1
    for f in freq:
        if lastIndex!=-1:
            for i in xrange(lastIndex, f[0]):
                cdf.append(lastSum)
        lastIndex=f[0]
        lastSum+=f[1]
	#print lastSum
        cdf.append(lastSum)
    for i in range(0, freq[0][0]-len(cdf)):
        cdf.append(lastSum)
    print len(cdf), freq[0][0]
    index=1
    #print ccdf
    for c in cdf:
	#print c
        wfile.write('\t'.join([str(index), str(c)]))
        wfile.write('\n')
	index+=1
    wfile.close()

def turn_to_ccdf(filePath, savePath):
    #the line of filePath (input file) is degree, freq
    freq=read_freq(filePath)
    if len(freq)==0:
        print filePath
        return
    wfile=open(savePath, 'w')
    ccdf=[]
    lastSum=0
    lastIndex=-1
    freq.reverse()
    for f in freq:
        if lastIndex!=-1:
            for i in xrange(f[0]+1,lastIndex):
                ccdf.append(lastSum)
        lastIndex=f[0]
        lastSum+=f[1]
	#print lastSum
        ccdf.append(lastSum)
    for i in range(0, freq[0][0]-len(ccdf)):
        ccdf.append(lastSum)
    print len(ccdf), freq[0][0]
    index=1
    #print ccdf
    ccdf.reverse()
    for c in ccdf:
	#print c
        wfile.write('\t'.join([str(index), str(c)]))
        wfile.write('\n')
	index+=1
    wfile.close()
    
if __name__=='__main__':
    if len(sys.argv)>=3:
#        turn_to_ccdf(sys.argv[1], sys.argv[2])
        turn_to_cdf(sys.argv[1], sys.argv[2])
    else:
#        turn_to_cdf(sys.argv[1])
        turn_to_ccdf(None, sys.argv[1])
