#!/bin/bash

save_dir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'
for repos in 'voldemort' 'storm' 'elasticsearch' 'presto'
do
    repos_path=${save_dir}/${repos}
    
    awk '{split($2, a, ":");print a[1]}' ${repos_path}/latest_commit | sort -n | uniq -c | awk '{print $2, $1}' > ${repos_path}/latest_commit_all_token
    awk '{split($2, a, ":");print a[2]}' ${repos_path}/latest_commit | sort -n | uniq -c | awk '{print $2, $1}' > ${repos_path}/latest_commit_program_token
    awk '{print $3}' ${repos_path}/latest_commit | sort -n | uniq -c | awk '{print $2, $1}' > ${repos_path}/latest_commit_size
##
##awk '{split($2, a, ":");print a[1]}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_all_token
##awk '{split($2, a, ":");print a[2]}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_program_token
##awk '{print $3}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_size
##
    python ../turn_to_ccdf.py ${repos_path}/latest_commit_all_token ${repos_path}/latest_commit_all_token_ccdf
    python ../turn_to_ccdf.py ${repos_path}/latest_commit_program_token ${repos_path}/latest_commit_program_token_ccdf
    python ../turn_to_ccdf.py ${repos_path}/latest_commit_size ${repos_path}/latest_commit_size_ccdf
##python ../turn_to_ccdf.py $2_all_token $2_all_token_ccdf
##python ../turn_to_ccdf.py $2_program_token $2_program_token_ccdf
##python ../turn_to_ccdf.py $2_size $2_size_ccdf
##
##python ../plot_ccdf.py $1_all_token_ccdf initial $2_all_token_ccdf latest all_token_ccdf
##python ../plot_ccdf.py $1_program_token_ccdf initial $2_program_token_ccdf latest program_token_ccdf
##python ../plot_ccdf.py $1_size_ccdf initial $2_size_ccdf latest size_ccdf
#
#
##awk '{if(NF==2 && $1>0)print $1}' TokenNum > TokenNum_all
##awk '{if(NF==2 && $2>0)print $2}' TokenNum > TokenNum_program
##awk '{if(NF==1 && $1>0)print $1}' FileSize > FileSize_all
    python ../plot_ccdf.py ${repos_path}/latest_commit_all_token_ccdf all ${repos_path}/latest_commit_program_token_ccdf program ${repos_path}/latest_commit_size_ccdf size ${repos_path}/size_ccdf

    awk '{if(NF==3)print $2}' ${repos_path}/TokenNum_with_path > ${repos_path}/TokenNum_all
    awk '{if(NF==3)print $3}' ${repos_path}/TokenNum_with_path > ${repos_path}/TokenNum_program

    awk '{if(NF==2 && $2!~/^[a-z]/ && $2>0)print $2}' ${repos_path}/FileSize_with_path > ${repos_path}/FileSize_all

    awk '{if(NF==5){split($5, a, ":");if(length(a[2])>0)print a[2]}}' ${repos_path}/Proj_Size > ${repos_path}/Proj_Size_factors
    
    sort -n ${repos_path}/FileSize_all | uniq -c | awk '{print $2, $1}' > ${repos_path}/Multi_factors_pdf
    python ../plot_dist.py  ${repos_path}/TokenNum_all token_all ${repos_path}/TokenNum_program token_program ${repos_path}/FileSize_all file_size ${repos_path}/Proj_Size_factors proj_size ${repos_path}/Multi_factors_pdf
    
    python ../plot_dist.py ${repos_path}/TokenNum_all token_all ${repos_path}/TokenNum_program token_program ${repos_path}/FileSize_all file_size ${repos_path}/Proj_Size_factors proj_size ${repos_path}/Multi_factors_ccdf

#    python ../plot_dist.py ${repos_path}/TokenNum_all token_all ${repos_path}/TokenNum_program token_program ${repos_path}/FileSize_all size ${repos_path}/Multi_factors_pdf

#    python ../turn_to_ccdf.py ${repos_path}/Multi_factors_pdf ${repos_path}/Multi_factors_ccdf
#    python ../turn_to_ccdf.py ${repos_path}/Multi_factors_pdf ${repos_path}/Multi_factors_cdf cdf
#    python ../plot_ccdf.py ${repos_path}/Multi_factors_ccdf size ${repos_path}/Multi_factors_ccdf
#    python ../plot_ccdf.py ${repos_path}/Multi_factors_cdf size ${repos_path}/Multi_factors_cdf
#    python ../plot_dist.py ${repos_path}/TokenNum_all tokens_all ${repos_path}/TokenNum_program tokens_program ${repos_path}/FileSize_all file_size ${repos_path}/Multi_factors_ccdf
done    
