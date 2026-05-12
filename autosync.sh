#!/bin/bash

while true
do
    if [[ -n $(git status --porcelain) ]]; then
        git add .
        git commit -m "Auto sync $(date)"
        git push
    fi

    sleep 10
done
