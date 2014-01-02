#!/bin/bash

save_dir='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'

for repos in 'voldemort' 'storm' 'elasticsearch' 'presto'
do
    repos_path=${save_dir}/${repos}
    awk '{if(NF==2 && $2!~/^[a-z]/)print $1}' ${repos_path}/FileSize_with_path | sort | uniq -c | awk '{print $1}' | sort -n | uniq -c | awk '{print $2, $1}' > ${repos_path}/ModifiedTimes_pdf
    python ../turn_to_ccdf.py ${repos_path}/ModifiedTimes_pdf ${repos_path}/ModifiedTimes_cdf cdf
    python ../turn_to_ccdf.py ${repos_path}/ModifiedTimes_pdf ${repos_path}/ModifiedTimes_ccdf

    python ../plot_ccdf.py ${repos_path}/ModifiedTimes_ccdf ccdf ${repos_path}/ModifiedTimes_ccdf
    python ../plot_ccdf.py ${repos_path}/ModifiedTimes_cdf cdf ${repos_path}/ModifiedTimes_cdf

    cat ${repos_path}/ModifiedTimes_pdf | python turn_dist_to_data.py > ${repos_path}/ModifiedTimes_data
done
