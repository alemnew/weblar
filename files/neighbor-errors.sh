#!/bin/bash
#Convert video into images

BASEDIR=/experiments/user
WORKINGDIR=/opt/weblar
OUTDIR=/monroe/results

videoname=$1.avi
# check if the video is created <-- the experiment was successful 
if ! [ -e "$videoname" ]; then 
    exit 
fi

mkdir $1
ffmpeg -loglevel panic -i $1.avi -r 10 $1/image-%d.bmp
begin=0
#pixels=$((1920*1200))
echo "prev i errors delta" > diffs.txt
frames=$(ls -1 $1/*.bmp|wc -l)

# pixel changes among consecutive frames 
for i in $(seq 2 $frames); do
#	echo "test debug 1"
	prev=$((i-1))
	errors=$(compare -metric AE -fuzz 5% $1/image-$prev.bmp $1/image-$i.bmp /dev/null 2>&1)
	echo "$prev $i $errors" >> $1.txt
done 

#pixel change between the first frame and the others 
for i in $(seq 3 $frames); do
	prev=2
    errors=$(compare -metric AE -fuzz 5% $1/image-$prev.bmp $1/image-$i.bmp /dev/null 2>&1)
	echo "$prev $i $errors" >> $1_2.txt
#	echo "debug 2"
done

#DS=$HOME"/data-store/"$1"/"
rm  -rf $1
#rm $1.avi # remove the video after recording in performance 
