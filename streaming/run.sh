#!/bin/bash

run_hadoop()
{
    for lang in py c++ c
#java haskell
#ada asm erlang fortran haskell lisp lua matlab sml pl rb
    do
        hadoop dfs -rmr result-dfs/$lang-$n
        hadoop jar ~/myhadoop/hadoop/contrib/streaming/hadoop-streaming-1.2.1.jar -D mapred.task.timeout=1800000 -mapper "/nfs/neww/users6/maxwellmao/mypython/bin/python freq_job.py -l $lang -s mapper -n $n" -reducer "/nfs/neww/users6/maxwellmao/mypython/bin/python freq_job.py -l $lang -s reducer" -inputformat SequenceFileAsTextInputFormat -input repository-dfs/$lang -output result-dfs/$lang-$n -file freq_job.py -numReduceTasks 1
        hadoop dfs -cat result-dfs/$lang-$n/part* > ../${reposDir}-$lang/$n-gram
    done
}

run_local()
{
    for lang in java
    do
#        awk 'BEGIN{OFS=""};{print "echo ../../repository/github-repository;","cat ../", $1}' ../../../repository/repos_dfs_path/${lang}_Path | sh
        ~/mypython/bin/python read_code_file.py ../../../repository/repos_dfs_path/${lang}_Path | ~/mypython/bin/python freq_job.py -l $lang -n $n -s mapper | sort -S 4G | ~/mypython/bin/python freq_job.py -l $lang -s reducer > ../${reposDir}-$lang/$n-gram_local &
    done
}

n=1
reposDir='repos-new'
#rb java
# ada erlang fortran haskell lisp lua matlab pl sml asm ada 
#rb py java c c++
#f90
# py pl php h c
#py
#h c cpp java pl rb php d m
#f90
for n in 1 2 3
#for lang in ada asm erlang fortran haskell lisp lua matlab sml pl rb haskell java
do
    run_hadoop
#    run_local &
#    echo $lang
#    hadoop dfs -cat num-dfs/$lang/part*
#    hadoop dfs -rmr num-dfs/$lang
#    hadoop jar ~/myhadoop/hadoop/contrib/streaming/hadoop-streaming-1.2.1.jar -D mapred.task.timeout=1800000 -mapper "/nfs/neww/users6/maxwellmao/mypython/bin/python freq_job.py -l $lang -s countNum" -reducer "awk '{total+=\$1};END{print total}'" -inputformat SequenceFileAsTextInputFormat -input repository-dfs/$lang -output num-dfs/$lang -file freq_job.py -numReduceTasks 1 &
done
