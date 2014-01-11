#!/bin/bash

repos_path='/nfs/neww/users6/maxwellmao/wxmao/umass/research/software/repository/diff_version'
repos_name='voldemort'

python multiplicative.py ${repos_path}/${repos_name}/Multi_factors_pdf ${repos_path}/${repos_name}/Multi_factors_bar ${repos_path}/${repos_name}/Multi_factors_conv ${repos_path}/${repos_name}/initial_commit_size ${repos_path}/${repos_name}/latest_commit_size
