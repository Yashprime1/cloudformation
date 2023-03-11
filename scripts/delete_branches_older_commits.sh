#!/bin/bash
echo "Starting script"
max_difference_days=0
merged_branches=$(git checkout main | git pull | git branch  -r --merged | grep -v "main$")
for branch in ${merged_branches}
do
    echo "Checking latest commit timestamp for $branch :"
    latest_commit_id=$(git log $branch | grep commit | head -1 | awk -F ' ' '{print $2}')
    echo "Latest commit_id for $branch is $latest_commit_id"
    latest_commit_timestamp=$(git show --format="%aI" $latest_commit_id | head -1)
    latest_commit_timestamp=$(date -u -d "$latest_commit_timestamp" +"%Y-%m-%dT%H:%M:%SZ")
    current_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "Latest commit timestamp - $latest_commit_timestamp" 
    echo "Current timestamp - $current_timestamp"
    latest_commit_timestamp_in_seconds=$(date -d $latest_commit_timestamp +%s)
    current_timestamp_in_seconds=$(date -d $current_timestamp +%s)
    difference_in_seconds=$(($current_timestamp_in_seconds-$latest_commit_timestamp_in_seconds))
    difference_in_days=$(($difference_in_seconds/60/60/24))
    if [ $difference_in_days -ge $max_difference_days ]
    then
        echo "Deleting $branch" 
        git push origin --delete $branch
        if [$? -ne 0]
        then
            echo "Failed to delete $branch"
            exit 1
        else
            echo "Successfully deleted $branch"
        fi
    else
        echo "Skipped $branch since latest-commit:$latest_commit_id is not greater than $max_difference_days days (currently just $difference_in_days days behind today)"
    fi
done