#!/bin/bash

while true
do
  LOG_FILE="/Users/kwn/the_lab/time-tracker/data/activitylog_$(date +%Y-%m-%d).jsonl"
  osascript -l JavaScript /Users/kwn/the_lab/time-tracker/script.jxa >> "$LOG_FILE" 2>&1
  sleep 10
done
