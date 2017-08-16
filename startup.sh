#!/bin/bash

process="MonitoringBot.py"
pid=$(bash check_process.sh pgrep local $process)

if [[ "$pid" == "False " ]]; then
    python3 $process &
    echo "Running MonitoringBot"
fi;
