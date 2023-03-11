#!/bin/bash
echo "Starting script"
git status
git checkout main
git pull origin main
merged_branches=$(git branch -r --merged | grep -v "main$")
for branch in ${merged_branches}
do
    echo "Checking latest commit timestamp for $branch :"
    latest_commit_id=$(git log $branch | grep commit | head -1 | awk -F ' ' '{print $2}')
    echo "Latest commit_id for $branch is $latest_commit_id"
done