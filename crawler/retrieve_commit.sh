#/bin/bash
# $1 is the local directory of the repository
# $2 is the sha of the commit
cd $1
git checkout $2
if [ -z $4 ];
then
    cp -r * $3../previous_commits/$2
fi
