#!/bin/bash

reposPath=~/wxmao/umass/research/software/code/programming_lang_analysis/repos-final-

#for lang in asm ada erlang fortran haskell lisp lua matlab newlisp octave pl sml rb java c c++
#do
#    gram_1=${reposPath}${lang}/token_dict_pygments-1_gram_refine
##    awk '{token[$2]+=$3}END{for(i in token){print length(i), token[i];}}' $gram_1 | awk '{token[$1]+=$2}END{for(i in token){print i, token[i]}}' | sort -k 1 -n | python plot_loglog.py $gram_1-tokenlength-zipf &
##    if [ ! -f $gram_1-tokenlength-pdf ]
##    then
#    awk '{token[$2]+=$3}END{for(i in token){print i, length(i), token[i];}}' $gram_1 | sort -k 2 -n > $gram_1-tokenlength
##    awk '{token[$2]+=$3}END{for(i in token){print i, token[i];}}' $gram_1-tokenlength | sort -k 1 -n  > $gram_1-tokenlength-pdf
##    fi
##    python turn_to_ccdf.py $gram_1-tokenlength-pdf $gram_1-tokenlength-ccdf &
##    cat $gram_1-tokenlength-ccdf | python plot_ccdf.py $gram_1-tokenlength-ccdf &
##| python plot_rank_freq.py $gram_1-tokenlength-zipf
#done
python plot_ccdf.py ${reposPath}pl/token_dict_pygments-1_gram_refine-tokenlength-ccdf pl ${reposPath}asm/token_dict_pygments-1_gram_refine-tokenlength-ccdf asm ${reposPath}erlang/token_dict_pygments-1_gram_refine-tokenlength-ccdf erlang ${reposPath}java/token_dict_pygments-1_gram_refine-tokenlength-ccdf java ${reposPath}c/token_dict_pygments-1_gram_refine-tokenlength-ccdf c ${reposPath}matlab/token_dict_pygments-1_gram_refine-tokenlength-ccdf matlab pl-asm-erlang-java-matlab-tokenlength-ccdf
#python plot_loglog.py ${reposPath}rb/token_dict_pygments-1_gram_refine-tokenlength-pdf ${reposPath}asm/token_dict_pygments-1_gram_refine-tokenlength-pdf ${reposPath}lisp/token_dict_pygments-1_gram_refine-tokenlength-pdf ${reposPath}java/token_dict_pygments-1_gram_refine-tokenlength-pdf ${reposPath}matlab/token_dict_pygments-1_gram_refine-tokenlength-pdf rb-asm-erlang-java-matlab-tokenlength

#python plot_rank_freq.py ${reposPath}rb/pygment_token_program-sort rb ${reposPath}asm/pygment_token_program-sort asm ${reposPath}lisp/pygment_token_program-sort lisp ${reposPath}java/pygment_token_program-sort java ${reposPath}matlab/pygment_token_program-sort matlab rb-asm-lisp-java-matlab_zipf
