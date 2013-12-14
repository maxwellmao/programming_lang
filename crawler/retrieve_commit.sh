#/bin/bash
# $1 is the local directory of the repository
# $2 is the sha of the commit
cd $1
git checkout $2
if [ -d ../previous_commits/$2 ]
then
    rm -rf ../previous_commits/$2
fi
mkdir ../previous_commits/$2
cp -r * ../previous_commits/$2
