#!/bin/bash
test1=$(grep -c "\#\* \* \* \* \* root pgrep svxlink" /etc/crontab)
 echo "$test1"

  if [ $test1 = 0 ]
  then
   echo "Add the #"
   sed -i '/root pgrep svxlink/ s/^/#/' /etc/crontab && service cron restart && pkill svxlink
 else 
#  then
   echo "Remove the #"
   sed -i '/root pgrep svxlink/s/^#//' /etc/crontab && service cron restart && /etc/spotnik/restart
fi
