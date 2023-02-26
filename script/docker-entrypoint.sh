#!/usr/bin/env bash
NAME="hpkchatbot" # Name of the application
# shellcheck disable=SC2034
PROJECT_DIR=/app # Project directory

echo "Starting $NAME as $(whoami)"

# Activate the virtual environment
# shellcheck disable=SC2164
cd $PROJECT_DIR

# Start your Application
exec python main.py
