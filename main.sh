#!/bin/bash

# check if scripts are installed
echo "Env variable: $SM_DIR"
if env | grep "SM_DIR="; then

  TIMESTAMP=$(date "+%Y%m%d_%H%M%S")

  log_dir=$SM_DIR"/logs"

  # verify that the logs folder exists
  if [ ! -d "$log_dir" ]; then
      echo "Creating logs directory"
      mkdir -p "$log_dir"
      # shellcheck disable=SC2181
      if [ $? -eq 0 ]; then
          echo "Logs directory successfully created."
      else
          echo "Error during creation of folder"
      fi
  fi

  cd "$log_dir" || exit

  files=$(ls -t)
  num_to_keep=100
  num_files=$(ls | wc -l)
  num_to_remove=$((num_files - num_to_keep))

  if [ $num_to_remove -gt 0 ]; then
    files_to_remove=$(echo "$files" | tail -n $num_to_remove)
    rm $files_to_remove
    echo "$num_to_remove files removed."
  else
    echo "No log file to remove."
  fi

  echo Logging into logs/log_$TIMESTAMP.txt
  cd ..
  python $SM_DIR/main.py >> logs/log_$TIMESTAMP.txt 2>&1

else
  echo "Error: SM Demo not installed. Run source install.sh to install it"
fi
