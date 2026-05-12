#!/bin/bash

while true
do
    echo "Checking for remote updates..."

    git pull --rebase origin master

    if [[ -n $(git status --porcelain) ]]; then
        echo "Local changes detected..."

        git add .

        git commit -m "Auto sync $(date)" || true

        git push origin master
    fi

    sleep 10
done
