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
echo $(ssh pi@10.5.12.9 "set -- '$process'; $script")
}

function getPid()
{
echo $pid
}

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
	state="Running"
else
	state="Not running"
fi


echo $1"("$pid"): "$state
