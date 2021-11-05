#!/bin/bash

set -e

echo

die(){
    echo
    exit 2
}

current_branch=`git rev-parse --abbrev-ref HEAD`
if [ "$current_branch" != "master" ]; then
    echo "Please select master!"
    die
fi

last_version=`git tag | sort -n -k1,1 -k2,2 -k3,3 -t '.' | tail -n 1`
echo "Current version: $last_version"

IFS='.' read -r -a versions_array <<< "$last_version"

if [ "$1" == "major" ]; then
    versions_array[0]=$((versions_array[0]+1))
    versions_array[1]=0
    versions_array[2]=0
elif [ "$1" == "minor" ]; then
    versions_array[1]=$((versions_array[1]+1))
    versions_array[2]=0
elif [ "$1" == "patch" ]; then
    versions_array[2]=$((versions_array[2]+1))
else
    echo "Please select mode: major, minor, patch!"
    die
fi

new_version=$(IFS=. ; echo "${versions_array[*]}")
echo "New version: $new_version"

if [ "$2" == "push" ]; then
    echo
    echo "PUSHING!"
    git tag -a $new_version -m "$new_version"
    git push origin $new_version
else
    echo
    echo "DRY MODE, NOT PUSHING!"
fi

echo
