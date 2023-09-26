#!/bin/bash

TIMESTAMP=$(date "+%Y%m%d_%H%M%S")

files=$(ls /home/a.occelli/sm_demo/logs -t)
echo $files
num_to_keep=10
num_files=$(ls | wc -l)
echo $num_files
num_to_remove=$((num_files - num_to_keep))

if [ $num_to_remove -gt 0 ]; then
  files_to_remove=$(echo "$files" | tail -n $num_to_remove)
  rm $files_to_remove
  echo "$num_to_remove files removed."
else
  echo "No log file to remove."
fi

echo Logging into logs/log_$TIMESTAMP.txt
python /home/a.occelli/sm_demo/main.py >> log_$TIMESTAMP.txt 2>&1
