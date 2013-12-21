#!/bin/bash
#awk '{split($2, a, ":");print a[1]}' $1 | sort -n | uniq -c | awk '{print $2, $1}' > $1_all_token
#awk '{split($2, a, ":");print a[2]}' $1 | sort -n | uniq -c | awk '{print $2, $1}' > $1_program_token
#awk '{print $3}' $1 | sort -n | uniq -c | awk '{print $2, $1}' > $1_size
#
#awk '{split($2, a, ":");print a[1]}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_all_token
#awk '{split($2, a, ":");print a[2]}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_program_token
#awk '{print $3}' $2 | sort -n | uniq -c | awk '{print $2, $1}' > $2_size
#
#python ../turn_to_ccdf.py $1_all_token $1_all_token_ccdf
#python ../turn_to_ccdf.py $1_program_token $1_program_token_ccdf
#python ../turn_to_ccdf.py $1_size $1_size_ccdf
#python ../turn_to_ccdf.py $2_all_token $2_all_token_ccdf
#python ../turn_to_ccdf.py $2_program_token $2_program_token_ccdf
#python ../turn_to_ccdf.py $2_size $2_size_ccdf
#
#python ../plot_ccdf.py $1_all_token_ccdf initial $2_all_token_ccdf latest all_token_ccdf
#python ../plot_ccdf.py $1_program_token_ccdf initial $2_program_token_ccdf latest program_token_ccdf
#python ../plot_ccdf.py $1_size_ccdf initial $2_size_ccdf latest size_ccdf

awk '{if(NF==2 && $1>0)print $1}' TokenNum > TokenNum_all
awk '{if(NF==2 && $2>0)print $2}' TokenNum > TokenNum_program
awk '{if(NF==1 && $1>0)print $1}' FileSize > FileSize_all

python ../plot_dist.py TokenNum_all tokens_all TokenNum_program tokens_program FileSize_all file_size Muli_factors_ccdf
