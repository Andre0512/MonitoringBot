#!/bin/bash

function UberspaceProcessi()
{
process=$1
read -d '' -r script <<'ENDSSH'
    #out=$(pgrep -fl python3)
    clear
    pid=$(pgrep -fl python3 | sed 's/.*?\([0-9]\{1,6\}\) python3 '$1'.*/\1/g')
    echo "$pid"
    exit
    if [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo "Running"
    else
        echo "Not running"
    fi
    exit
ENDSSH
$script
#echo $(ssh abasche@abasche.de "set -- '$process'; $script")
}

function UberspaceProcess()
{
    test=$(ssh abasche@abasche.de "pgrep -fl python3")
    pid=$(sed 's/.*?\([0-9]\{1,6\}\) python3 '$1'.*/\1/g' <<< $test)
    echo $pid 
}


function PiProcess()
{
process=$1
read -d '' -r script <<'ENDSSH'
    out=$(pgrep -a python3)
    pid=$(echo $out | sed 's/.*\([0-9]\{1,6\}\) python3 [\/a-zA-Z0-9]*'$1'.*/\1/g')
    echo $pid
    exit
    if [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo "Running"
    else
        echo "Not running"
    fi
    exit
ENDSSH
echo $(ssh pi@10.5.12.9 "set -- '$process'; $script")
}

function LocalProcess()
{
process=$1
out=$(pgrep -a python3)
pid=$(echo $out | sed 's/.*\([0-9]\{1,6\}\) python3 [\/a-zA-Z0-9]*'$1'.*/\1/g')
if [[ "$pid" =~ ^[0-9]+$ ]]; then
    echo "Running"
else
    echo "Not running"
fi
echo $(ssh pi@10.5.12.9 "set -- '$process'; $script")
}

if [[ "$2" == "Pi" ]];
then
    result=$(PiProcess $1)
elif [[ "$2" == "local" ]];
then
    result=$(LocalProcess $1)
else
    result=$(UberspaceProcess $1)
fi



echo $1": "$result
