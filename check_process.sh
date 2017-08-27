#!/bin/bash

function getPid()
{
pattern='s/\([0-9]\{1,6\}\) [\/a-zA-Z0-9]*python3 [\/\._a-zA-Z0-9]*'$1'/\1/p'
pid=$(sed -n "$pattern" <<< $result)

if [[ "$pid" != "" ]]; then
    echo "True "$pid
else
    echo "False "
fi
}

if [[ "$1" == "pgrep" ]]; then
    if [[ "$2" == "Pi" ]]; then
        result=$(ssh pi@10.5.12.9 "pgrep -a python3")
        getPid $3
    elif [[ "$2" == "local" ]]; then
        result=$(pgrep -a python3)
        getPid $3
    elif [[ "$2" == "Uberspace" ]]; then
       result=$(ssh abasche@abasche.de "pgrep -fl python3")
       getPid $3
    elif [[ "$2" == "VPS" ]]; then
       result=$(ssh andre@cloud.abasche.de "pgrep -a python3")
       getPid $3
    fi
elif [[ "$1" == "fhem" ]]; then
    if [[ "$2" == "Pi" ]]; then
        result=$(ssh pi@10.5.12.9 "/etc/init.d/fhem status")
	echo $result
    elif [[ "$2" == "local" ]]; then
        result=$(/etc/init.d/fhem status)
        echo $result
    fi
fi
