#~/mypython/bin/python
import os, sys
import token_parser

# since removed comment/literal lead to different distribution of token
# do the statistics on the ratio of reserved tokens

def process_code_line(code_str, onlyCode=False):
    lineParser=token_parser.Naive_Parser()
    item=code_str.split()
    if onlyCode:
        lineParser.parse_line(code_str)
    else:
        tokenLine='\t'.join(item[1:-1])
        lineParser.parse_line(tokenLine)
    return lineParser.fileToken

def parser_token_file(pygmentTokenCorpusFile, allTokenPath, reserveTokenPath):
    fp=open(pygmentTokenCorpusFile)
    corpusToken=dict()
    reservedToken=dict()
    codeStr=''
    while True:
        lines=fp.readlines(10000)
        if not lines:
            break
        for line in lines:
            if line.startswith('Token'):
                if len(codeStr)>0:
                    codeStr=codeStr.strip()
                    lineToken=process_code_line(codeStr)
                    freq=int(codeStr.split()[-1])
                    for k, v in lineToken.items():
                        corpusToken[k]=corpusToken.get(k, 0)+v*freq
                    if codeStr.startswith('Token.Keyword') or codeStr.startswith('Token.Name'):
                        for k, v in lineToken.items():
                            reservedToken[k]=reservedToken.get(k, 0)+v*freq
                    codeStr=''
            codeStr+=''.join(['\t', line.strip()])
#            item=line.strip().split()
    lineToken=process_code_line(codeStr)
    freq=int(codeStr.split()[-1])
    for k, v in lineToken.items():
        corpusToken[k]=corpusToken.get(k, 0)+v*freq
    if codeStr.startswith('Token.Keyword') or codeStr.startswith('Token.Name'):
        for k, v in lineToken.items():
            reservedToken[k]=reservedToken.get(k, 0)+v*freq
    fp.close()

    wp=open(allTokenPath, 'w')
    wp.write('\n'.join(['\t'.join([item[0], str(item[1])]) for item in sorted(corpusToken.items(), key=lambda x:x[1])]))
    wp.close()
    wp=open(reserveTokenPath, 'w')
    wp.write('\n'.join(['\t'.join([item[0], str(item[1])]) for item in sorted(reservedToken.items(), key=lambda x:x[1])]))
    wp.close()
    
    corpusNum=reduce(lambda x,y: x+y, corpusToken.values(), 0)
    reservedNum=reduce(lambda x,y: x+y, reservedToken.values(), 0)
    lang=allTokenPath.split('/')[-2].split('-')[-1]
    print lang, 'All token v.s. reserved token: %d:%d' % (len(corpusToken), len(reservedToken))
    print lang, 'All token v.s. reserved token: %d:%d' % (corpusNum, reservedNum)

def save_token_dict(filePath, token_dict):
    wp=open(filePath, 'w')
    wp.write('\n'.join(['\t'.join([item[0], str(item[1])]) for item in sorted(token_dict.items(), key=lambda x:x[1])]))
    wp.close()

def seperate_file_into_different_tokens(pygmentTokenCorpusFile, saveDirPath):
    fp=open(pygmentTokenCorpusFile)
    corpusToken=dict()
    commentToken=dict()
    literalToken=dict()
    programToken=dict()
    program_operator_Token=dict()
    codeStr=''
    while True:
        lines=fp.readlines(10000)
        if not lines:
            break
        for line in lines:
            if line.startswith('Token'):
                if len(codeStr)>0:
                    codeStr=codeStr.strip()
                    lineToken=process_code_line(codeStr)
                    freq=int(codeStr.split()[-1])
                    for k, v in lineToken.items():
                        corpusToken[k]=corpusToken.get(k, 0)+v*freq
                    if codeStr.startswith('Token.Keyword') or codeStr.startswith('Token.Name'):
                        for k, v in lineToken.items():
                            programToken[k]=programToken.get(k, 0)+v*freq
                            program_operator_Token[k]=program_operator_Token.get(k, 0)+v*freq
                    elif codeStr.startswith('Token.Literal'):
                        for k, v in lineToken.items():
                            literalToken[k]=literalToken.get(k, 0)+v*freq
                    elif codeStr.startswith('Token.Comment'):
                        for k, v in lineToken.items():
                            commentToken[k]=commentToken.get(k, 0)+v*freq
                    elif codeStr.startswith('Token.Operator'):
                        for k, v in lineToken.items():
                            program_operator_Token[k]=program_operator_Token.get(k, 0)+v*freq
                    codeStr=''
            codeStr+=''.join(['\t', line.strip()])
    lineToken=process_code_line(codeStr)
    freq=int(codeStr.split()[-1])
    for k, v in lineToken.items():
        corpusToken[k]=corpusToken.get(k, 0)+v*freq
    if codeStr.startswith('Token.Keyword') or codeStr.startswith('Token.Name'):
        for k, v in lineToken.items():
            programToken[k]=programToken.get(k, 0)+v*freq
            program_operator_Token[k]=program_operator_Token.get(k, 0)+v*freq
    elif codeStr.startswith('Token.Literal'):
        for k, v in lineToken.items():
            literalToken[k]=literalToken.get(k, 0)+v*freq
    elif codeStr.startswith('Token.Comment'):
        for k, v in lineToken.items():
            commentToken[k]=commentToken.get(k, 0)+v*freq
    elif codeStr.startswith('Token.Operator'):
        for k, v in lineToken.items():
            program_operator_Token[k]=program_operator_Token.get(k, 0)+v*freq
    fp.close()
    save_token_dict(os.path.join(saveDirPath, 'pygment_token_all'), corpusToken)
    save_token_dict(os.path.join(saveDirPath, 'pygment_token_comment'), commentToken)
    save_token_dict(os.path.join(saveDirPath, 'pygment_token_literal'), literalToken)
    save_token_dict(os.path.join(saveDirPath, 'pygment_token_program'), programToken)
    save_token_dict(os.path.join(saveDirPath, 'pygment_token_program_operator'), program_operator_Token)
    corpusNum=reduce(lambda x,y: x+y, corpusToken.values(), 0)
    commentNum=reduce(lambda x,y: x+y, commentToken.values(), 0)
    literNum=reduce(lambda x,y: x+y, literalToken.values(), 0)
    programNum=reduce(lambda x,y: x+y, programToken.values(), 0)
    program_op_Num=reduce(lambda x,y: x+y, program_operator_Token.values(), 0)

    lang=saveDirPath.split('/')[-1].split('-')[-1]
    print lang, '(Unique number) All token %d, comment token: %d, literal token: %d, program token: %d, program_op token:%d ' % (len(corpusToken), len(commentToken), len(literalToken), len(programToken), len(program_operator_Token))
    print lang, '(Total number) All token:%d, comment token: %d, literal token:%d, program token: %d, program_op token:%d' % (corpusNum, commentNum, literNum, programNum, program_op_Num)

def usage():
    print 'Usage <pygment token file> <file of all tokens> <file of reserved tokens>'

if __name__=='__main__':
    if len(sys.argv)==4:
        parser_token_file(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv)==3:
        seperate_file_into_different_tokens(sys.argv[1], sys.argv[2])
