#!/bin/bash

process="MonitoringBot.py"
result=$(bash check_process.sh pgrep local $process)
state=$(echo "$result" | cut -d' ' -f 1)

if [[ "$1" -eq "restart" && "$state" -eq "True" ]]; then
    pkill -f $process
    state="False"
fi;

if [[ "$state" == "False" ]]; then
    python3 $process &
    echo "Running MonitoringBot"
fi;
