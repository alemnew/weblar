#!/usr/bin/python
import zmq
import json
import sys
import time


context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://172.17.0.1:5556")
#  Empty string is everything
topicfilter = 'MONROE.META.DEVICE.MODEM'
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

startSubscribe = int(time.time())
DIC = {}
PRINT = ""
while int(time.time()) - startSubscribe < 60: # listen for interface update for 1 minute
    data = socket.recv()
    try:
	ifname = ""
	iccid = ""
	ipadd = ""
        msg = json.loads(data.split(" ", 1)[1])
        if msg.get("ICCID") != None and msg.get("InternalInterface") != None:
            iccid = msg.get('ICCID')
            ifname = msg.get('InternalInterface')
            ipadd = msg.get('IPAddress')
	    tmp = {}
	    
	    ipadd = ipadd.rsplit('.',1)[0] + ".1"
	    tmp[ipadd] = iccid
            DIC[ifname] = tmp
    except Exception, ex:
        pass

#format the interface name and iccid for ease of use in bash
for ifname, ipadd_iccid in DIC.items():
	for ipadd, iccid in ipadd_iccid.items():
    		PRINT += ifname + " " + iccid + " " + ipadd + "\n" 

#write to file
f = open("interfaces", "w")
f.write(PRINT)
f.close

