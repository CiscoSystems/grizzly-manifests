#!/usr/bin/env bash
. /root/openrc
vmlist=`nova list | grep ACTIVE | awk '{print $2}'`
c='\033[0m'
g='\033[00;32m'
y='\033[00;33m'

for i in $vmlist
do
  vol_id=`nova volume-list | grep $i | awk '{print $2}'`
  vm_name=`nova list | grep $i | awk '{print $4}'`
  if [ $vol_id ]; then
    echo -e "Server ${g}$vm_name${c} ($i) has volume ${y}$vol_id${c} attached."
  fi
done
