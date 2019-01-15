#!/usr/bin/python
#import zmq
import json 
import sys
import util
import os

'''url = sys.argv[1]
nodeID = sys.argv[2]
ifname = sys.argv[3]
fname = sys.argv[4]
operator = sys.argv[5]
'''
# return the ip address and the path to the url 
def get_trace_route(fname):
    traceRoute = {}
    f = open(fname + '.tr', 'r')
    tr_lines = f.readlines()
    endpoint  = tr_lines[0].split('(')[1].split(')')[0]
    for line in tr_lines[1:]:
        line = line.strip()
        parts = line.split(" ")
        key = parts[0]
        val = parts[3].replace("(", "").replace(")", "") 
        rtt = []
        
        if len(parts) > 4:
            if parts[4].replace('.','',1).isdigit():
                rtt.append(float(parts[4]))
        if len(parts) > 6: 
            if parts[6].replace('.','',1).isdigit():
                rtt.append(float(parts[6]))
        if len(parts) > 8:
            if parts[8].replace('.','',1).isdigit():
                rtt.append(float(parts[8]))
        #print '%s , %s' %(key, val)
        if len(rtt) > 0:
            traceRoute[key] = val + "|" + str(sum(rtt) / float(len(rtt))) 
        else:
            traceRoute[key] = val

    traceRoute[-1] = endpoint # the destination 
    #print traceRoute
    return traceRoute

# return the visual completion time for a website 
def get_visual_completion(fname):
    visual_completion = {}
    rend_start_time = {}
    if os.path.exists(fname):
        visual_completion = json.load(open(fname, 'r'))
        try: 
            # reading the starting time of the rendering 
            if os.path.exists(fname.replace(".ren", "_ren_start.json")):
                rend_start_time = json.load(open(fname.replace(".ren",\
                    "_ren_start.json"), 'r'))
            visual_completion['rend_start_time'] = rend_start_time['rend_start'] 
        except KeyError: 
            pass
    return visual_completion

# return the web QoS performance & complexity that was captured by chromedriver using the timing api 
def get_web_qos_complexity(fname):
    performance = {}
    number_objects = {}
    qos_complexity = {}
    if os.path.exists(fname + '.perf'):
        fr = open(fname + '.perf', 'r')
        lines = fr.readlines()[0].replace('\'n', '')
        perf_metrics, num_objects = lines.split("_", 1) 
        metrics = perf_metrics.split(',') 
        for m in metrics:
            mm = m.strip().split(':')
            performance[mm[0]] = float(mm[1].strip())
        
        num_obj = num_objects.split(',') 
        for n in num_obj:
            nn = n.strip().split(':')
            number_objects[nn[0]] = int(nn[1].strip())
        qos_complexity['Performance'] = performance
        qos_complexity['NumberOfObjects'] = number_objects
    return qos_complexity 

#return the filtered meta data 
def get_metadata(fname):
    metadata = {}
    location = {} 
    network = {}
    cpu = {}
    memory = {}
    if not os.path.exists(fname + ".md"):
        return metadata
    f = open(fname + ".md", "r")
    md_lines = f.readlines()
    for line in md_lines:
        tmp_l = line.split(" ", 1)
        if len(tmp_l) < 2:
            continue
        tmp_md = tmp_l[1].replace("\n", "").strip()
        if not tmp_md.endswith("}"):
            continue
        msg= json.loads(tmp_md)
        md = {}
        timestamp = msg.get("Timestamp")
        if msg.get("DataId") == None:
            continue
        data_id = str(msg.get("DataId"))
        md["DataId"] = data_id
        # CONNECTIVITY metadata 

        if data_id.endswith((".DEVICE.MODEM", ".CONNECTIVITY")):
            if msg.get("RSSI") != None:
                md["RSSI"] = msg.get("RSSI") 
            if msg.get("RSRQ") != None:
                md["RSRQ"] = msg.get("RSRQ") 
            if msg.get("DeviceMode") != None:
                md["DeviceMode"] = msg.get("DeviceMode") 
            if msg.get("DeviceSubmode") != None:
                md["DeviceSubmode"] = msg.get("DeviceSubmode")
            if msg.get("Band") != None:
                md["Band"] = msg.get("Band")
            if msg.get("DeviceState") != None:
                md["DeviceState"] = msg.get("DeviceState")
            if msg.get("RSRP") != None:
                md["RSRP"] = msg.get("RSRP") 
            if msg.get("CID") != None:
                md["CID"] = msg.get("CID") 
            if msg.get("LAC") != None:
                md["LAC"] = msg.get("LAC") 
            if msg.get("Frequency") != None:
                md["Frequency"] = msg.get("Frequency") 
            if msg.get("ECIO") != None:
                md["ECIO"] = msg.get("ECIO")
            if msg.get("RSCP") != None:
                md["RSCP"] = msg.get("RSCP")
            if msg.get("IMSIMCCMNC") != None:
                md["IMSIMCCMNC"] = msg.get("IMSIMCCMNC")
            if msg.get("PCI") != None:
                md["PCI"] = msg.get("PCI")
            if msg.get("IPAddress") != None:
                md["IPAddress"] = msg.get("IPAddress")
            network[timestamp] = md

        elif data_id.endswith(".DEVICE.GPS"):
            if msg.get("Latitude") != None:
                md["Latitude"] = msg.get("Latitude") 
            if msg.get("Longitude") != None:
                md["Longitude"] = msg.get("Longitude") 
            if msg.get("Speed") != None:
                md["Speed"] = msge.get("Speed")
            location[timestamp] = md

        elif tmp_l[0].endswith(".cpu"):
            if msg.get("user") != None:
                md["user"] = msg.get("user")
            if msg.get("nice") != None:
                md["nice"] = msg.get("nice")
            if msg.get("system") != None:
                md["system"] = msg.get("system")
            if msg.get("idle") != None:
                md["idle"] = msg.get("idle")
            if msg.get("iowait") != None:
                md["iowait"] = msg.get("iowait")
            if msg.get("irq") != None:
                md["irq"] = msg.get("irq")
            if msg.get("softirq") != None:
                md["softirq"] = msg.get("softirq")
            if msg.get("steal") != None:
                md["steal"] = msg.get("steal")
            if msg.get("guest") != None:
                md["guest"] = msg.get("guest")
            cpu[timestamp] = md

        elif tmp_l[0].endswith(".memory"):
            if msg.get("apps") != None:
                md["apps"] = msg.get("apps")
            if msg.get("free") != None:
                md["free"] = msg.get("free")
            if msg.get("swap") != None:
                md["swap"] = msg.get("swap")
            memory[timestamp] = md
    # add to all the event to the metadata 
    metadata['Network'] = network 
    metadata['Location'] = location
    metadata['Memory'] = memory
    metadata['CPU']  = cpu

    f.close()

    return metadata

# return ATF, web QoS, complexity  form file recorded by timing API 
def read_atf_qos_complexity(filename):
    atf_qos_complexity = {}
    if os.path.exists(filename + '_atf.json'):
        f = open(filename + "_atf.json", "r")
        atf_qos_complexity = json.load(f)
        f.close()    
    return atf_qos_complexity

#if __name__ == '__main__':
def merge_metadata(url, nodeID, operator, ifname, fname):
    mergeddata = {}
    status = {}
    mergeddata['URL'] = url.replace("\n", "")
    mergeddata['NodeID'] = int(nodeID) 
    mergeddata['Operator'] = operator
    mergeddata['InterfaceName'] = ifname
    mergeddata['Metadata'] = get_metadata(fname)
    mergeddata['TraceRoute'] = get_trace_route(fname) 
    mergeddata['RenderingTime'] = get_visual_completion(fname + ".ren")
   #  mergeddata['RenderingTime_2'] = get_visual_completion(fname + "_2.ren")
    atf_qos_complexity = read_atf_qos_complexity(fname)
    if bool(atf_qos_complexity.get('web_complexity')):
        mergeddata['WebComplexity'] = atf_qos_complexity['web_complexity']
        status['webComplexity'] = 1
    else:
        status['webComplexity'] = 0
    if bool(atf_qos_complexity.get('atf')):
        mergeddata['ATF'] = atf_qos_complexity['atf'] 
        status['atf'] = 1
    else:
        status['atf'] = 0
    if bool(atf_qos_complexity.get('web_qos')):
        mergeddata['WebQoS'] = atf_qos_complexity['web_qos']
        status['webQoS'] = 1
    else: 
        status['webQoS'] = 0
    if not bool(get_metadata(fname)):
        status['metadata'] = 0
    else:
        status['metadata'] = 1
    if not bool(get_trace_route(fname)):
        status['traceroute'] = 0
    else:
        status['traceroute'] = 1
    if not bool(get_visual_completion(fname + '.ren')):
        status['rendering'] = 0
    else:
        status['rendering'] = 1
    
    mergeddata['expStatus'] = status
    
    json.dump(mergeddata, open(fname + '.json', 'w'))
