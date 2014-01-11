#!/bin/bash
repos_path=/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version
repos_name=voldemort
python file_size_change_stat.py ${repos_path}/${repos_name}/FileSize_with_path ${repos_path}/${repos_name}/SizeChange_factor
