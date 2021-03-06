#!/bin/bash

remote={{ remote }}
host=`hostname`

api_response=''

local_ip=''
outside_ip=''
get_ips () {
  local_ip=`/sbin/ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | tr '\n' ','`
  outside_ip=`curl -s ifconfig.io`
}

api_call () {
  get_ips
  dfh=`df -h`
  uptime=`w`
  free=`free -m`  
  user=`whoami`
  ifconfig=`/sbin/ifconfig`
  route=`/sbin/route`
  api_response=`curl -s --data "route=$route&local_ip=$local_ip&outside_ip=$outside_ip&user=$user&uptime=$uptime&dfh=$dfh&free=$free&ifconfig=$ifconfig" $remote:{{port}}/api/$host`
}

# Parse response
api_call
set -- "$api_response" 
IFS=";"; declare -a Array=($*) 
port="${Array[0]}"
restart="${Array[1]}" 
user="${Array[2]}"
update_configs="${Array[3]}"

echo "Port given: $port"
echo "Restart: $restart"
echo "User: $user"
echo "Update SSH Config: $update_configs"

# See if the server is running
lines=`ps aux | grep $port | wc -l`

if [ $lines -eq 1 -o $restart == 'true' ]
then
  echo 'Killing old screen...'
  screen -X -S tnnl quit # clean up any existing tunnels
  echo 'Restarting tunnel...'
  screen -dmS tnnl autossh -M 12399 -oPubkeyAuthentication=yes -oPasswordAuthentication=no -oLogLevel=error  -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -R $port:localhost:22 $user@$remote
fi

if [ $update_configs == 'true' ]
then
  echo 'Updating SSH configs...'
  sed -i.bak '/#tnnlr/,+999 d' ~/.ssh/config
  curl -s "$remote:{{port}}/api/configs?user=$user" >> ~/.ssh/config
fi
