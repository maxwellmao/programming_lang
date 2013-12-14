#!/usr/bin/python
import os, sys

def get_token(str):
    token=[]
    lastIndex=0
    token_list=str.split(':')
    for i in range(len(token_list)):
        if token_list[i].startswith('Token.') and i!=0:
#            token.append('\t'.join(token_list[lastIndex:i]))
            yield ':'.join(token_list[lastIndex:i])
            lastIndex=i
#    if lastIndex!=0:
#        token.append('\t'.join(token_list[lastIndex, -1]))
    yield ':'.join(token_list[lastIndex:])

def refine_n_gram(original_file, save_file, n=2):
    n_gram_dict=dict()
    fp=open(original_file)
    wp=open(save_file, 'w')
    for line in fp.readlines():
#        print line.strip()
        freq=int(line.strip().split()[-1])
        tokenStr='\t'.join(line.strip().split()[:-1])
#        print items
#        items='\t'.join(line.strip().split()[:-1]).split(':')
        gram=[]
        for token in get_token(tokenStr):
            if len(token.strip())==0:
                continue
            contents=token.split()
            if len(contents)<=1:
#                print 'error'
                print save_file
                print token
                print line.strip()
            contents[1]=contents[1].replace('%', '.').replace('#', '.').replace('&', '.').replace('@', '.').replace(':', '.').replace(',', '.').replace('=', '.').replace('[', '.').replace(']', '.')
            dotIndex=contents[1].find('.')
#            dotRIndex=contents[1].rfind('.')
            if dotIndex>-1:
                for para in contents[1].split('.'):
#                    print para
                    if len(para)>0:
                        gram.append('\t'.join([contents[0], para]))
                        if len(gram)>=n:
                            n_gram=':'.join(gram[:n])
                            del gram[0]
                            n_gram_dict[n_gram]=n_gram_dict.get(n_gram, 0)+freq
#                            print n_gram
            else:
                gram.append(token)
                if len(gram)>=n:
                    n_gram=':'.join(gram[:n])
                    del gram[0]
                    n_gram_dict[n_gram]=n_gram_dict.get(n_gram, 0)+freq
#                    print n_gram
        
#        print gram
        if len(gram)>=n:
            n_gram=':'.join([gram[:n]])
            n_gram_dict[n_gram]=n_gram_dict.get(n_gram, 0)+freq
#            print n_gram
#        else:
#             sys.stderr.write('Error!\n')
    fp.close()
    wp=open(save_file, 'w')
    wp.write('\n'.join(['\t'.join([item[0], str(item[1])]) for item in sorted(n_gram_dict.items(), key=lambda x:x[1])]))
    wp.close()

if __name__=='__main__':
    n=int(sys.argv[1].split('-')[-1].split('_')[0])
    #print n, 'gram'
    refine_n_gram(sys.argv[1], sys.argv[1]+'_refine', n)
