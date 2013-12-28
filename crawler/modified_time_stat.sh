#!/bin/bash

awk '{if(NF==2)print $1}' $1/FileSize_with_path | sort | uniq -c | awk '{print $1}' | sort -n | uniq -c | awk '{print $2, $1}' > $1/ModifiedTimes_pdf
python ../turn_to_ccdf.py $1/ModifiedTimes_pdf $1/ModifiedTimes_cdf cdf
python ../turn_to_ccdf.py $1/ModifiedTimes_pdf $1/ModifiedTimes_ccdf

python ../plot_ccdf.py $1/ModifiedTimes_ccdf ccdf $1/ModifiedTimes_ccdf

cat $1/ModifiedTimes_pdf | python turn_dist_to_data.py > $1/ModifiedTimes_data
