#!/usr/bin/python

import os
import sys
import csv
import json
import time
import subprocess

PIXELS = 1920 *1080 
FRAMERATE = 10
THRESHOLD = 0.5
stopingTime_14 = 140 # number of consecutive screenshots that has pixel change 
stopingTime_3 = 30 # number of consecutive screenshots that has pixel change 
stopingTime_10 = 100 # number of consecutive screenshots that has pixel change 
renderingTime_14 = {}
renderingTime_10 = {}
renderingTime_3 ={}
renderingTime_2 = {}
changing_img = []
def setPixels():
    try:
        line = open("resolution", "r").readline()
        parts = line.split("x")
        width = int(parts[0])
        height = int(parts[1])
        PIXELS = width * height
    except Exception as e:
        print("Error in reading resolution")
        
# compute the rendering time from the changing images only 
def calc_rend_time_changing_img(changing_img, fname):
    deltas = {}
    for i in range(len(changing_img) - 1):
        nxt = changing_img[i + 1]
        cmd = ["compare",  "-metric",  "AE",  "-fuzz", "5%", fname + "/image-"+ 
                nxt +".bmp",  fname + "/image-" + changing_img[i] + ".bmp",
                "/dev/null", "2>&1"] 
        err = subprocess.check_output(cmd)
        
        key = i + "_" + nxt
        deltas[key] = err * 100.0 / PIXELS


# calculate the rendering time by comparing consecutive frames
def calcRenderingTime(difftxt):

    begin = -1
    end = -1
    last_change = -1
    try:
        diff = open(difftxt, 'r')
        lines = diff.readlines()
        interval = 0 #the time stamp of every 100 ms
        key = 0
        #dlog.write(str(len(lines)) + "\n")
        diff.close()

        # for the 14 sec threshold
        for line in lines[1:]:
            line = line.strip().replace("\n", "")
            if line == "": 
                continue 
            parts = line.split(" ")
            prev = int(parts[0])
            i = int(parts[1])
            errors = float(parts[2])
            delta = 100.0 * errors / PIXELS
            #print delta
            if begin < 0:
                begin = prev
                last_change = 0
                # continue
            if delta >= THRESHOLD:
                end = i
                rt = ((end - begin) / float(FRAMERATE)) * 1000
                key += 1
                print(str(rt) + "\n")
                #dlog.write(str(rt) + " \n")
                if not renderingTime_14.has_key(key):
                    renderingTime_14[key] = rt
                    #dlog.write(str(key) + " ... rt added \n")
                last_change = 0

            if last_change != -1 and delta < THRESHOLD:
                #what if delta < threshold  instead of errors = 0 ???
                last_change += 1
                
            if last_change >= stopingTime_14: # The page hasn't changed for 14s  
                begin = -1
                end = -1
                last_change = -1
                key = 0
                break
        
        # for the 10 sec threshold
        for line in lines[1:]:
            line = line.strip().replace("\n", "")
            if line == "": 
                continue 
            parts = line.split(" ")
            prev = int(parts[0])
            i = int(parts[1])
            errors = float(parts[2])
            delta = 100.0 * errors / PIXELS
            if begin < 0:
                begin = prev
                last_change = 0
            if delta >= THRESHOLD:
                end = i
                rt = ((end - begin) / float(FRAMERATE)) * 1000
                key += 1
                if not renderingTime_10.has_key(key):
                    renderingTime_10[key] = rt
                last_change = 0

            if last_change != -1 and delta < THRESHOLD:
                last_change += 1
                
            if last_change >= stopingTime_10: # The page hasn't changed for 14s  
                begin = -1
                end = -1
                last_change = -1
                key = 0
                break

        # for the 3 sec threshold
        for line in lines[1:]:
            line = line.strip().replace("\n", "")
            if line == "": 
                continue 
            parts = line.split(" ")
            prev = int(parts[0])
            i = int(parts[1])
            errors = float(parts[2])
            delta = 100.0 * errors / PIXELS
            if begin < 0:
                begin = prev
                last_change = 0
            if delta >= THRESHOLD:
                end = i
                rt = ((end - begin) / float(FRAMERATE)) * 1000
                key += 1
                if not renderingTime_3.has_key(key):
                    renderingTime_3[key] = rt
                last_change = 0

            if last_change != -1 and delta < THRESHOLD:
                last_change += 1
                
            if last_change >= stopingTime_3: # The page hasn't changed for 14s  
                begin = -1
                end = -1
                last_change = -1
                key = 0
                break

        '''rendTime = ((end - begin) / float(FRAMERATE)) * 1000
        if len(renderingTime) > 0 and len(renderingTime) < 10: 
            # means that there is very small pixel difference and the web site doesn't reach stable state 
            maxIndex = max(renderingTime.keys())
            while maxIndex < 100:
                maxIndex +=10
                renderingTime[maxIndex] = rendTime 
                '''
        renderingTime = {}
        renderingTime['3Sec'] = renderingTime_3
        renderingTime['10Sec'] = renderingTime_10
        renderingTime['14Sec'] = renderingTime_14
        json.dump(renderingTime, open(fname + ".ren",'w'))
        #os.remove(difftxt)
        #dlog.write("Done") 
    except IOError as e:
        print "IO Error occurred " + str(e) 
    #dlog.close()

# calculate the rendering time by comparing the pixels in the first with each frame 
def calcRenderingTime_2(difftxt):
    last_change_2 = 0
    begin = 2
    try:
        diff = open(difftxt, 'r')
        lines = diff.readlines()
        interval = 0 #the time stamp of every 100 ms
        key = 0
        diff.close()
        for line in lines:
            line = line.strip().replace("\n", "")
            if line == "": 
                continue 
            parts = line.split(" ")
            prev = int(parts[0])
            i = int(parts[1])
            errors = float(parts[2])
            delta = 100.0 * errors / PIXELS
            interval += 100
            
            if delta >= THRESHOLD:
                end = i
                rt = ((end - begin) / float(FRAMERATE)) * 1000
                key += 1
                if not renderingTime_2.has_key(key):
                    renderingTime[key] = rt
                last_change_2 = 0

            if delta < THRESHOLD:
                last_change_2 += 1
                
            if last_change_2 >= stopingTime: # The page has not changed for 3 seconds 
                break
        json.dump(renderingTime_2, open(fname + "_2.ren",'w'))
    except IOError as e:
        print "IO Error occurred " + str(e) 

# main function 
if __name__ == '__main__':
    setPixels()
    fname = sys.argv[1]
    websiteName = sys.argv[2]
    difftxt = fname + ".txt"
    difftxt_2 = fname + "_2.txt"
    if os.path.exists(difftxt):
        calcRenderingTime(difftxt)
    #if os.path.exists(difftxt_2):
    #    calcRenderingTime_2(difftxt_2)

