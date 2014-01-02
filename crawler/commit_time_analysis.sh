#!/bin/bash

save_dir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'
for url in 'storm' 'elasticsearch' 'presto' 'voldemort'
do
#    awk '{if($1~/.java$/)}print NF-1, $0' ${save_dir}/${url}/Change_files | sort -k1 -n | tail -
    awk '{if($1~/.java$/)print NF-1"\t"$0}' ${save_dir}/${url}/Change_files | sort -k1 -n | tail -n 10 | cut -f 2- > ${save_dir}/${url}/Query_files
    cat ${save_dir}/${url}/logs/* | python commit_time_analysis.py ${save_dir}/${url}/Query_files ${save_dir}/${url}/FilesCommitTimeInterval
done
