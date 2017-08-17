#!/bin/bash

process="MonitoringBot.py"
path=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
result=$(bash $path'/'check_process.sh pgrep local $process)
state=$(echo "$result" | cut -d' ' -f 1)

if [[ "$1" == "restart" ]]; then
    if [[ "$state" == "True" ]]; then
        pkill -f $process
	sleep 5
        pkill -f $process
        state="False"
    fi;
fi;

if [[ "$state" == "False" ]]; then
    python3 $path'/'$process &
    echo "Running MonitoringBot"
fi;
