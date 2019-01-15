#!/bin/bash


cd /opt/weblar/
#echo "I am going to start" > /monroe/results/webrend.log
export DISPLAY=:11
Xvfb :11 -screen 0 1920x1080x24 &
echo "dispaly set to Xvfb at 11"

python weblar.py -e
