#!/bin/bash
echo "Starting script"
git status
git checkout main
git pull origin main
git branch -r --merged