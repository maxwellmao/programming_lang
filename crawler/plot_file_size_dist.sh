#!/bin/bash
awk '{split($2, a, ":");print a[1]}' $1/latest_commit | sort -n | uniq -c | awk '{print $2, $1}' > $1/latest_commit_all_token
awk '{split($2, a, ":");print a[2]}' $1/latest_commit | sort -n | uniq -c | awk '{print $2, $1}' > $1/latest_commit_program_token
awk '{print $3}' $1/latest_commit | sort -n | uniq -c | awk '{print $2, $1}' > $1/latest_commit_size
##
##awk '{split($2, a, ":");print a[1]}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_all_token
##awk '{split($2, a, ":");print a[2]}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_program_token
##awk '{print $3}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_size
##
python ../turn_to_ccdf.py $1/latest_commit_all_token $1/latest_commit_all_token_ccdf
python ../turn_to_ccdf.py $1/latest_commit_program_token $1/latest_commit_program_token_ccdf
python ../turn_to_ccdf.py $1/latest_commit_size $1/latest_commit_size_ccdf
##python ../turn_to_ccdf.py $2_all_token $2_all_token_ccdf
##python ../turn_to_ccdf.py $2_program_token $2_program_token_ccdf
##python ../turn_to_ccdf.py $2_size $2_size_ccdf
##
##python ../plot_ccdf.py $1_all_token_ccdf initial $2_all_token_ccdf latest all_token_ccdf
##python ../plot_ccdf.py $1_program_token_ccdf initial $2_program_token_ccdf latest program_token_ccdf
##python ../plot_ccdf.py $1_size_ccdf initial $2_size_ccdf latest size_ccdf
#
python ../plot_ccdf.py $1/latest_commit_all_token_ccdf all $1/latest_commit_program_token_ccdf program $1/latest_commit_size_ccdf size $1/size_ccdf
#
##awk '{if(NF==2 && $1>0)print $1}' TokenNum > TokenNum_all
##awk '{if(NF==2 && $2>0)print $2}' TokenNum > TokenNum_program
##awk '{if(NF==1 && $1>0)print $1}' FileSize > FileSize_all
awk '{if(NF==2 && $2>0)print $2}' $1/FileSize_with_path > $1/FileSize_all
python ../plot_dist.py $1/FileSize_all size $1/Multi_factors_pdf
python ../turn_to_ccdf.py $1/Multi_factors_pdf $1/Multi_factors_ccdf
python ../plot_ccdf.py $1/FileSize_all size $1/Multi_factors_ccdf
#python ../plot_dist.py TokenNum_all tokens_all TokenNum_program tokens_program FileSize_all file_size Multi_factors_ccdf
