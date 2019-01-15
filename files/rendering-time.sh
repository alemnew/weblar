#!/bin/bash

if [ -z "$1" ]; then
        echo "Usage: $0 <URL>"
        exit 1
fi
#trap killer SIGINT
killer(){
        echo "Closing ..."
        kill 0
}

BASEDIR=/experiments/user
WORKINGDIR=/opt/weblar
OUTDIR=/monroe/results
browser=Chrome
pid=0
scr=99
nodeid=$5
metadata=$6
ifname=$7

java -jar CaptureScreen.jar $1 $2 

#check if the video is successfully recorded
#echo "This is to test the end of recording"

if [ ! -s $2.avi ]; then
	exit 1
fi
#
MINSIZE=20000
ACTUALSIZE=$(wc -c <"$2.avi")
if [ $ACTUALSIZE -le $MINSIZE ]; then
	echo $2.avi$'\t'$ACTUALSIZE >> website_error.txt
	exit 1
fi

./neighbor-errors.sh $2
#url=$(basename $1)
./detect.py $2 $1
