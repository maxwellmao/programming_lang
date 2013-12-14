#!/bin/bash

for lang in php
#lua sml haskell
#ada asm c c++ erlang fortran haskell lisp java lua matlab newlisp octave pl py php rb sml
#for lang in pl rb
#f90 py h c cpp java php
#m java pl rb php d
do
   hadoop jar test.jar util.BuildSequenceFileTextFromDir ../../repository/repos_dfs_path/${lang}_Path repository-dfs/${lang} &
done
