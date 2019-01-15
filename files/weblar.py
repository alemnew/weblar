#!/usr/bin/python
import sys
import subprocess
from datetime import datetime
import zmq
import json
import time
import os
import mergedata
import shutil 
import re

# date 25.07.2017 

VERSION = 0.8
OUTDIR = '/monroe/results/'
CURRENT_DIR = os.getcwd() + "/"

# return the base from a url 
def url_basename(url):
    basename = ''
    pieces = url.split("/")
    if len(pieces) > 2:
        basename = pieces[2]
    elif len(pieces) == 2:
        basename = pieces[1]

    return basename

# return the ip address for an interface 
# assume the route info is found tmp_route_info
def get_ip_addr(inf):
    t = 'tmp_route_info'
    os.system('routel | grep default > ' + t)
    f = open(t, 'r') 
    routes = f.readlines()
    ip_addr = ""
    for route in routes:
        #remove too many white spaces and make them list  
        pieces = ' '.join(route.split()).split(' ') 
        if inf in pieces:
            ip_addr = pieces[1]
            break
    f.close()

    return ip_addr

# get the default gateways for a set of interfaces
# from Foivos 
def get_default_gateways(interfaces):
    default_gateway_line = re.compile(r'default via (\S+) dev (\S+)')
    default_gateways = {}
    cmd = ["ip", "rule", "list"]
    output = subprocess.check_output(cmd)
    ip_tables = set()
    for line in output.split("\n"):
        ip_tables.add(line.strip().split(" ")[-1])
    ip_tables.remove("")
    for ip_table in ip_tables:
        cmd = ["ip", "route", "show", "table", ip_table]
        output = subprocess.check_output(cmd)
        for line in output.split("\n"):
            if default_gateway_line.search(line):
                (gateway, interface) = default_gateway_line.search(line).groups()
                if interface in interfaces:
                    default_gateways[interface] = gateway
    return default_gateways

def change_default_gateway(default_gateways, interface):
    """
    first we delete the default routes but only if they exist
    and then we add once the route we want

    This function returns True is the change is sucessful and
    False if it fails
    """
    output_interface = None
    cmd0 = ["ip", "route", "show",  "default"]
    routing_table = subprocess.check_output(cmd0)
    while routing_table.find("default") >= 0:
        cmd1 = ["route", "del", "default"]
        try:
            subprocess.check_output(cmd1)
        except subprocess.CalledProcessError as e:
            if e.returncode == 28:
                print "Time limit exceeded"
        routing_table = subprocess.check_output(cmd0)
    gw_ip = default_gateways[interface]
    cmd2 = ["route", "add", "default", "gw", gw_ip, interface]
    try:
        subprocess.check_output(cmd2)
        cmd3 = ["ip", "route", "get", "8.8.8.8"]
        output = subprocess.check_output(cmd3)
        output = output.strip(' \t\r\n\0')
        output_interface = output.split(" ")[4]
        if output_interface == interface:
            print "Source interface is set to " + interface
        else:
            return False
    except subprocess.CalledProcessError as e:
        if e.returncode == 28:
            print "Time limit exceeded"
        return False
    return True

# reset the default gateway 
def reset_default_gateway(default_gateways):
    cmd1 = ["route", "del", "default"]
    cmd0 = ["ip", "route", "show",  "default"]
    routing_table = subprocess.check_output(cmd0)
    while routing_table.find("default") >= 0:
        cmd1 = ["route", "del", "default"]
        try: 
            subprocess.check_output(cmd1)
        except subprocess.CalledProcessError as e:
            if e.returncode == 28:
                print "ime limit exceeded"
        routing_table = subprocess.check_output(cmd0)
    eth_gw_ip = default_gateways["eth0"]
    cmd2 = ["route", "add", "default", "gw", eth_gw_ip, "eth0"]
    try:
        subprocess.check_output(cmd2)
    except subprocess.CalledProcessError as e:
        if e.returncode == 28:
            print "Time limit exceeded"
            return False

    return True


# return  the available interface 
def get_interfaces():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect ("tcp://172.17.0.1:5556")
    #  Empty string is everything
    topicfilter = 'MONROE.META.DEVICE.MODEM'
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
    
    startSubscribe = int(time.time())
    DIC = {}
    
    while int(time.time()) - startSubscribe < 120:
        data = socket.recv()
        try: 
            ifname = ""
            iccid  = ""
            ipadd  = ""
            msg = json.loads(data.split(" ", 1)[1])
            if msg.get("ICCID") != None and msg.get("InternalInterface") != None:
                iccid = msg.get('ICCID')
                ifname = str(msg.get('InternalInterface'))
                op = msg.get('Operator') 
                tmp = str(iccid) + "_" + str(op)
                DIC[ifname] = tmp
        except Exception, ex:
            print str(ex)
            pass 
    return DIC

# record metadata for iccid 
def write_init_metadata(ICCID, fname):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect ("tcp://172.17.0.1:5556")
    topicfilter = "MONROE.META.DEVICE.MODEM." + ICCID + ".UPDATE"
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
    data = socket.recv()

    f = open(fname + ".md", 'w') 
    f.write(data + "\n")
    f.close()

# run the web rendering experiment 
def run_web_rend_exp(NODEID, websites, IINF, default_gateways):
    for ifname, iccid_op in IINF.items():
        ic_op = iccid_op.split("_")
        iccid = ic_op[0]
        operator = ic_op[1]
        if not change_default_gateway(default_gateways, ifname):
            print "default gateway don't changed to " + ifname 
            continue
        for w in websites:
            w = w.replace("\n", "")
            if w == "": 
                continue 
            print w + " is downloading..."
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            fname = str(NODEID) + "_" + str(ifname) + "_" + str(now)
            
            # record  the path to the website in the interface 
            os.system('traceroute -i ' + ifname + ' ' +  url_basename(w) + ' > '
                  +  fname + '.tr')
            # wait until metadata update for that specific iccid is received
            if iccid != '0': # record only in cellular interfaces
                write_init_metadata(iccid, fname)
            metaProc = subprocess.Popen(['./metadata.py', iccid, ifname, fname], 
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=4096)
            renderProcess = subprocess.Popen(['./rendering-time.sh', w, fname], 
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=4096)
            renderProcess.wait()
            metaProc.kill()
            
            # if the rendering file doesn't exists then there was something wrong in the experiment 
            if not os.path.exists(fname + '_atf.json') and not os.path.exists(fname + '.ren'):
                #print "there was error in calculating ATF @ " + fname
                continue

            #if not os.path.exists(fname + '.ren'):
            #    print "there was error in calculating rendering time  @ " + fname
            #    continue
            # merge data (meta, performance, rendering data) 
            mergedata.merge_metadata(w, NODEID, operator, ifname, fname)
            #  move file to /monroe/results directory for rsync 
            shutil.move(fname + '.json', OUTDIR + fname + '.json') 
            # shutil.move(fname + '.avi', OUTDIR + fname + '.avi') 
            #shutil.move(fname + '.md', OUTDIR + fname + '.md') 
            #shutil.move(fname + '.ren', OUTDIR + fname + '.ren') 
            #shutil.move(fname + '.txt', OUTDIR + fname + '.txt') 
            
            print "moving finished"

    #f = open("/monroe/results/webrendering.log", "a") 
    #f.write("FINISHED") 
    #f.close()

# main
if __name__ == '__main__':
    print('Rendering server version %.1f started. ' %VERSION )
    
    run_on_eth = sys.argv[1]
    # read Node ID
    f = open("/nodeid", "r") 
    NODEID = f.readlines()[0].strip()
    f.close()
    
    # read target url 
    target_url = open(CURRENT_DIR + "target-url", "r")
    websites = target_url.readlines()
    target_url.close()
    
    # read the available interface 
    interfaces_info = {}
    if run_on_eth == '-e':
        interfaces_info.update({'eth0':'0_FIXED'}) # to add fixed line 
    interfaces_info.update(get_interfaces())

    default_gateways = get_default_gateways(interfaces_info.keys())
    run_web_rend_exp(NODEID, websites, interfaces_info, default_gateways)
    time.sleep(500)
