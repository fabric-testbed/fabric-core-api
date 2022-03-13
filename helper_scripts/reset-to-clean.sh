#!/usr/bin/env bash

# variables
SCRIPTS_DIR=$(pwd)
BASE_DIR=$(dirname "$SCRIPTS_DIR")


# run this script from the scripts directory
cd ../

# directories to remove - relative to BASE_DIR
DIRS_TO_REMOVE=(
  data/pg_data
  migrations
)

# directories to restore - relative to BASE_DIR
DIRS_TO_RESTORE=(
  migrations
)

# stop and remove docker containers
echo "[INFO] stop and remove docker containers"
docker-compose stop
docker-compose rm -fv

# remove directories from DIRS_TO_REMOVE
for f in "${DIRS_TO_REMOVE[@]}"; do
  echo "[INFO] remove directory: ${f}"
  rm -rf $BASE_DIR/${f}
done

# restore directories from DIRS_TO_RESTORE
for f in "${DIRS_TO_RESTORE[@]}"; do
  echo "[INFO] restore directory: ${f}"
  mkdir -p $BASE_DIR/${f}
done

# completed
echo "[INFO] completed - check files prior to use"

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;