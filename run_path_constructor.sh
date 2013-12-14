#!/bin/bash

for dir in $1/*
do
#    echo 'List':$dir
#    echo ${dir#$1/}
    python construct_repository_path.py $dir $2 ${dir#$1/} &
done
