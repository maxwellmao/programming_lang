#!/bin/bash

function plot_observe_ccdf()
{
    dPath=$1
    bPath=$2
    allFilePath=''
    zipfFilePath=''
    for observe in 100 500 1000 5000 10000 50000 100000 500000 1000000 5000000 10000000 50000000 100000000 500000000 1000000000 5000000000 10000000000 50000000000
    do
        if [ -f $dPath/$bPath-$observe ];
        then
#            echo $dPath/$bPath-$observe
            if [ ! -f $dPath/$bPath-$observe-pdf ];
            then
                awk '{split($0, a, " "); print a[NF]}' $dPath/$bPath-$observe | sort -n -S 4G | uniq -c | awk '{print $2, $1}' > $dPath/$bPath-$observe-pdf
            fi
            if [ ! -f $dPath/$bPath-$observe-sort ];
            then
                awk '{split($0, a, " "); print a[NF]}' $dPath/$bPath-$observe | sort -n -S 4G > $dPath/$bPath-$observe-sort
            fi
            if [ ! -f $dPath/$bPath-$observe-ccdf ];
            then
                python turn_to_ccdf.py $dPath/$bPath-$observe-pdf $dPath/$bPath-$observe-ccdf
            fi
            allFilePath=$allFilePath' '$dPath/$bPath-$observe-ccdf
            zipfFilePath=$zipfFilePath' '$dPath/$bPath-$observe-sort
        fi
    done
    python plot_ccdf.py $allFilePath $dPath/$bPath-ccdf
#    echo "python plot_rank_freq.py $zipfFilePath $dPath/$bPath-zipf"
#    python plot_rank_freq.py $zipfFilePath $dPath/$bPath-zipf
}

reposPath=~/wxmao/umass/research/software/code/programming_lang_analysis/repos-final-
dirPath=$1
for lang in asm ada erlang fortran haskell lisp lua matlab newlisp octave pl sml java c c++
#php
#
#c c++
#asm ada erlang fortran haskell lisp lua matlab newlisp octave pl sml php java
#java php
do
    for base in file_token_pygment
#token_dict_pygment
#    token_dict_pygment
#    file_token_pygment 
    do
        dirPath=$reposPath$lang/finite_observation
        for gram in 1_gram 2_gram 3_gram
        do
            plot_observe_ccdf $dirPath $base-$gram &
#            echo $dirPath $dirPath/$base-$gram
        done
#        echo $dirPath $dirPath/$base
        plot_observe_ccdf $dirPath $base &
    done
done


