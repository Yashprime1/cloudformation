#!/bin/bash
echo "Starting script"
git status
git checkout main
git pull origin main
branches=$(git branch -r --merged | grep -v "main$")
for branch in ${branches}
do
    
done