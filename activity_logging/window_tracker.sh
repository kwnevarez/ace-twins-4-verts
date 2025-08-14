#!/bin/bash

while true
do
  LOG_FILE="activity_log_$(date +%Y_%m_%d).jsonl"
  osascript -l JavaScript ./script.jxa >> "$LOG_FILE" 2>&1
  sleep 10
done
