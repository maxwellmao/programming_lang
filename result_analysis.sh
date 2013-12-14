#!/bin/bash

function plot_file_size()
{
    if [ ! -f $reposDir-$1/file_size_all ]
    then
        awk '{split($0, a, " "); split(a[length(a)], b, ":"); print b[1]}' $reposDir-$1/file_size | sort -n | uniq -c  | awk '{print $2, $1}' > $reposDir-$1/file_size_all
    fi

    if [ ! -f $reposDir-$1/file_size_program ]
    then
        awk '{split($0, a, " "); split(a[length(a)], b, ":"); print b[2]}' $reposDir-$1/file_size | sort -n | uniq -c  | awk '{print $2, $1}' > $reposDir-$1/file_size_program
    fi
    python turn_to_ccdf.py $reposDir-$1/file_size_all $reposDir-$1/file_size_all-ccdf
    python turn_to_ccdf.py $reposDir-$1/file_size_program $reposDir-$1/file_size_program-ccdf

#   python plot_loglog.py $reposDir-$1/file_size_all all $reposDir-$1/file_size_program program $reposDir-$1/file_size
    python plot_ccdf.py $reposDir-$1/file_size_all-ccdf all $reposDir-$1/file_size_program-ccdf program $reposDir-$1/file_size-ccdf
}

#sed -n '2,$p' $1 | 
sufix=''
reposDir='repos-final'
#for lang in py cpp m java pl rb f90 php d c h
#python plot_dist.py $reposDir-lua/file_size lua $reposDir-fortran/file_size fortran $reposDir-erlang/file_size erlang $reposDir-haskell/file_size haskell lua-fortran-erlang-haskell_token-ratio-dist
#$reposDir-matlab/file_size matlab pl-asm-lisp-java-matlab_token-ratio-dist
for lang in asm ada erlang fortran haskell lisp lua matlab newlisp octave pl sml java py rb c c++
#java
#java
#
#
#java
##ada asm
##c h
do
#    echo $lang
###################################################################################
####    original token file -> pdf of tokens -> ccdf of tokens
####    
#    cat ${reposDir}-$lang/file_token${sufix} | awk '{split($0, a, " "); print a[NF]}' | sort -n -S 4G | uniq -c | awk '{print $2, $1}' > ${reposDir}-$lang/file_token${sufix}-pdf
#    python turn_to_ccdf.py ${reposDir}-$lang/file_token${sufix}-pdf ${reposDir}-$lang/file_token${sufix}-ccdf
#    cat ${reposDir}-$lang/file_token${sufix}-ccdf | python plot_ccdf.py ${reposDir}-$lang/file_token${sufix}-ccdf &
###################################################################################

    plot_file_size $lang &

#    allfile=''
#    zipffile=''
#    for token in pygment_token_all pygment_token_comment pygment_token_literal pygment_token_program pygment_token_program_operator token_dict_pygments-2_gram_refine token_dict_pygments-3_gram_refine
#    do
##        cat ${reposDir}-$lang/${token} | awk '{split($0, a, " "); print a[NF]}' | sort -n -S 4G | uniq -c | awk '{print $2, $1}' > ${reposDir}-$lang/${token}-pdf
#
#        if [ ! -f ${reposDir}-$lang/${token}-sort ];
#        then
#            awk '{split($0, a, " ");print a[NF]}' ${reposDir}-$lang/$token | sort -n > ${reposDir}-$lang/${token}-sort
#        fi
#        if [ ! -f ${reposDir}-$lang/${token}-pdf ];
#        then
#            uniq -c ${reposDir}-$lang/${token}-sort | awk '{print $2, $1}' > ${reposDir}-$lang/${token}-pdf
#        fi
#        if [ ! -f ${reposDir}-$lang/${token}-ccdf ];
#        then
#            python turn_to_ccdf.py ${reposDir}-$lang/${token}-pdf ${reposDir}-$lang/${token}-ccdf
#        fi
#        allfile=$allfile' '${reposDir}-$lang/${token}-ccdf
#        zipffile=$zipffile' '${reposDir}-$lang/${token}-sort
#    done
#    python plot_ccdf.py ${allfile} ${reposDir}-$lang/token-ccdf &
#    python plot_rank_freq.py ${zipffile} ${reposDir}-${lang}/zipf-law &


#    cat ${reposDir}-$lang/token_dict_pygments_name | python plot_rank_freq.py $lang ${reposDir}-$lang/token_dict_pygments_name-rank
#    if [ -f ${reposDir}-$lang/token_dict_pygments-1_gram ];
#    then
#    for token in token_dict_pygments file_token_pygments
#    do
#        echo ${reposDir}-$lang/${token}-sort-1_gram-ccdf
#        if [ ! -f ${reposDir}-$lang/${token}-sort-1_gram-ccdf ];
#        then
#            for n in 1 2 3
#            do
#                if [ ! -f ${reposDir}-$lang/${tokan}-sort-${n}_gram ]
#                then
#                    awk '{split($0, a, " ");print a[NF]}' ${reposDir}-$lang/${token}-${n}_gram | sort -n > ${reposDir}-$lang/${token}-sort-${n}_gram
#                fi
#                uniq -c ${reposDir}-$lang/${token}-sort-${n}_gram | awk '{print $2, $1}' > ${reposDir}-$lang/${token}-sort-${n}_gram-pdf
#                python turn_to_ccdf.py ${reposDir}-$lang/${token}-sort-${n}_gram-pdf ${reposDir}-$lang/${token}-sort-${n}_gram-ccdf
#            done
#        fi
#    done
#        python plot_rank_freq.py ${reposDir}-$lang/token_dict_pygments-sort-1_gram ${reposDir}-$lang/token_dict_pygments-sort-2_gram ${reposDir}-$lang/token_dict_pygments-sort-3_gram ${reposDir}-$lang/corpus_token ${reposDir}-$lang/zipf &
#        cat ${reposDir}-$lang/token_dict_pygments-1_gram | python plot_rank_freq.py $lang ${reposDir}-$lang/token_dict_pygments-1_gram-rank
#        cut -f 2 ${reposDir}-$lang/token_dict_pygments_name | uniq -c | awk '{print $2, $1}' > ${reposDir}-$lang/token_dict_pygments_name-pdf
#        python turn_to_ccdf.py ${reposDir}-$lang/token_dict_pygments_name-pdf ${reposDir}-$lang/token_dict_pygments_name-ccdf
#        cat ${reposDir}-$lang/token_dict_pygments_name-ccdf | python plot_ccdf.py ${reposDir}-$lang/token_dict_pygments_name-ccdf &
#    fi
##-f ${reposDir}-$lang/file_token${sufix} &&

#    for token in file_token corpus_token
#    do
#        if [ ! -f ${reposDir}-$lang/${token}${sufix}-ccdf ]
#        then
#            cat ${reposDir}-$lang/${token}${sufix} | awk '{split($0, a, " "); print a[NF]}' | sort -n -S 4G | uniq -c | awk '{print $2, $1}' > ${reposDir}-$lang/${token}${sufix}-pdf
#            python turn_to_ccdf.py ${reposDir}-$lang/${token}${sufix}-pdf ${reposDir}-$lang/${token}${sufix}-ccdf
##       cat ${reposDir}-$lang/file_token${sufix}-ccdf | python plot_ccdf.py ${reposDir}-$lang/file_token${sufix}-ccdf &
##        cat ${reposDir}-$lang/corpus_token${sufix} | python plot_rank_freq.py $lang ${reposDir}-$lang/corpus_token${sufix} &
#
#
##        cat ${reposDir}-$lang/heap_law | python plot_heap_law.py ${reposDir}-$lang/heap_law &
#       
##        cat ${reposDir}-$lang/corpus_token${sufix}-ccdf | python plot_ccdf.py ${reposDir}-$lang/corpus_token${sufix}-ccdf &
#        fi
#    done
#    if [ -f ${reposDir}-$lang/1-gram ]
#    then
#        for n in 1 2 3
#        do
#            awk '{split($0, a, " ");print a[length(a)-1]}' ${reposDir}-$lang/$n-gram| sort -n > ${reposDir}-$lang/$n-gram-corpus
#            awk '{split($0, a, " ");print a[length(a)]}' ${reposDir}-$lang/$n-gram| sort -n > ${reposDir}-$lang/$n-gram-file
##           echo ${reposDir}-$lang/$n-gram-corpus
#
#            sort -n -S 4G ${reposDir}-$lang/$n-gram-corpus | uniq -c | awk '{print $2, $1}' > ${reposDir}-$lang/$n-gram-corpus-pdf
#            sort -n -S 4G ${reposDir}-$lang/$n-gram-file | uniq -c | awk '{print $2, $1}' > ${reposDir}-$lang/$n-gram-file-pdf
#            python turn_to_ccdf.py ${reposDir}-$lang/$n-gram-corpus-pdf ${reposDir}-$lang/$n-gram-corpus-ccdf
#            python turn_to_ccdf.py ${reposDir}-$lang/$n-gram-file-pdf ${reposDir}-$lang/$n-gram-file-ccdf
##            cat ${reposDir}-$lang/corpus_token${sufix}-ccdf | python plot_ccdf.py ${reposDir}-$lang/corpus_token${sufix}-ccdf &
#        done
#    python plot_ccdf.py ${reposDir}-$lang/corpus_token${sufix}-ccdf ${reposDir}-$lang/token_dict_pygments-sort-1_gram-ccdf ${reposDir}-$lang/token_dict_pygments-sort-2_gram-ccdf ${reposDir}-$lang/token_dict_pygments-sort-3_gram-ccdf ${reposDir}-$lang/corpus_dist-ccdf &
#    python plot_ccdf.py ${reposDir}-$lang/file_token${sufix}-ccdf ${reposDir}-$lang/file_token_pygments-sort-1_gram-ccdf ${reposDir}-$lang/file_token_pygments-sort-2_gram-ccdf ${reposDir}-$lang/file_token_pygments-sort-3_gram-ccdf ${reposDir}-$lang/file_dist-ccdf &
#        python plot_rank_freq.py ${reposDir}-$lang/1-gram-corpus ${reposDir}-$lang/2-gram-corpus ${reposDir}-$lang/3-gram-corpus ${reposDir}-$lang/corpus_token${sufix} ${reposDir}-$lang/zipf &
#    fi
###################################################################################
####     plot_rank_freq.py -- show the zipf's law
####     the input should be sorted by the number of appearence(increasing order)
####    cat repos-$lang/corpus_token${sufix} | python plot_rank_freq.py $lang repos-$lang/corpus_token${sufix} &
###################################################################################
##    cat repos-$lang/token_dict_pygments_name | python plot_rank_freq.py $lang repos-$lang/token_dict_pygments_name-rank &
##    python turn_to_ccdf.py repos-$lang/file_token${sufix}-pdf repos-$lang/file_token${sufix}-ccdf
##    cat repos-$lang/file_token${sufix}-ccdf | python plot_ccdf.py repos-$lang/file_token${sufix}-ccdf &
##    cat repos-$lang/corpus_token${sufix} | python plot_rank_freq.py $lang repos-$lang/corpus_token${sufix} &
##    cut -f 2 repos-$lang/corpus_token${sufix} | uniq -c | awk '{print $2, $1}' > repos-$lang/corpus_token${sufix}-totaltime-pdf
##    python turn_to_ccdf.py repos-$lang/corpus_token${sufix}-totaltime-pdf repos-$lang/corpus_token${sufix}-totaltime-ccdf
##    cat repos-$lang/corpus_token${sufix}-totaltime-ccdf | python plot_ccdf.py repos-$lang/corpus_token${sufix}-totaltime-ccdf &
##    cat repos-$lang/file_token${sufix} | python filter_token.py > repos-$lang/file_token${sufix}-onlyEntity &
##    cat repos-$lang/corpus_token${sufix} | python filter_token.py > repos-$lang/corpus_token${sufix}-onlyEntity &

###################################################################################
####
####
#    echo $lang
#    python stat_token_ratio.py ${reposDir}-$lang/token_dict_pygments ${reposDir}-$lang/token_pygments_all ${reposDir}-$lang/token_pygments_reserved &

#    python refine_ngram.py ${reposDir}-$lang/token_dict_pygments-2_gram &
#    python refine_ngram.py ${reposDir}-$lang/token_dict_pygments-3_gram &
#    python refine_ngram.py ${reposDir}-$lang/token_dict_pygments-1_gram &
#    python stat_token_ratio.py ${reposDir}-$lang/token_dict_pygments ${reposDir}-$lang &

####
####
###################################################################################


done
para=''
##for file in corpus_token${sufix}-ccdf file_token${sufix}-ccdf
##file=file_token${sufix}-ccdf
##file=1-gram-corpus-ccdf
##file=corpus_token${sufix}
#file=1-gram-corpus
#file=heap_law
#name=''
#for lang in pl rb lua asm fortran java erlang haskell lisp matlab
#do
#    para=$para' '${reposDir}-$lang/$file
#    name=$name'-'$lang
#done
#echo $para ${name#-}_${file}
##python plot_ccdf.py $para ${name#-}_${file}
##python plot_rank_freq.py $para ${name#-}_${file}
#python plot_heap_law.py $para ${name#-}_${file}
