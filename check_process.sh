#!/bin/bash

if [[ "$2" == "Pi" ]];
then
    result=$(ssh pi@10.5.12.9 "pgrep -a python3")
elif [[ "$2" == "local" ]];
then
    result=$(pgrep -a python3)
else
    result=$(ssh abasche@abasche.de "pgrep -fl python3")

fi
pattern='s/\([0-9]\{1,6\}\) [\/a-zA-Z0-9]*python3 [\/a-zA-Z0-9]*'$1'/\1/p'
pid=$(sed -n "$pattern" <<< $result)

if [[ "$pid" != "" ]]; then
    echo "True "$pid
else
    echo "False "
fi


