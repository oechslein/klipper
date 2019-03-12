#!/bin/bash
# saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset

brightness=0

if [ -e "$HOME/.led_top_brightness" ] ; then
    brightness=$(cat "$HOME/.led_top_brightness")
fi


if [[ $# -gt 0 ]]; then
  brightness=$1
else
  if [[ $brightness -gt 0 ]]; then
    brightness=0
  else
    brightness=1023
  fi
fi

gpio -g mode 19 pwm; gpio -g pwm 19 $brightness

#save it output the file
rm "$HOME/.led_top_brightness"
echo $brightness > "$HOME/.led_top_brightness"

