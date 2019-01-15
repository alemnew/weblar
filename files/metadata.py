#!/usr/bin/python
import zmq
import json 
import sys

IFNAME = sys.argv[2]
ICCID = sys.argv[1]
fname = sys.argv[3]

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://172.17.0.1:5556")
topicfilter = ""
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
f = open(fname + ".md", "a")
while True:
    data = socket.recv()
    try:
        msg = json.loads(data.split(" ", 1)[1])
        if msg.get("InternalInterface") == IFNAME or msg.get("DataId") == \
                "MONROE.META.NODE.SENSOR" or msg.get("DataId") == \
                "MONROE.META.DEVICE.GPS" or msg.get("DataId") ==  "MONROE.EXP.PING":
            f.write(data + "\n")
    except Exception as e:
        print "Exception occurred: " + str(e)
        pass

f.close()

