#!/usr/bin/env python 

# client_herd.py
# Author: L. Di Venere
# This script should run on the PC controlling the master DAQ
# The script sends the message to each subdetector (server) and waits for a response from the server.
# When the server has answered correctly, the client script moves to the next step (in this example, the script is terminated).
#
# NOTE: change the IP address in the script to the current IP address of the server PC..

import os
import socket
import sys
import time

def get_last_file(mother_path="/"):
    if not mother_path.endswith('/'):
        mother_path += '/'


    list_of_dirs = sorted(filter(lambda x: os.path.isdir(os.path.join(mother_path, x)), os.listdir(mother_path)))
    last_dir = list_of_dirs[-1]
    list_of_files_in_dirs = sorted(filter(lambda x: os.path.isfile(os.path.join(mother_path + last_dir, x)), os.listdir(mother_path + last_dir)))
    last_file = list_of_files_in_dirs[-1]

    return last_dir, last_file 

# def log_last_file(unixTime=0, mother_path="/"):
#     with open('log.txt', 'a') as logfile:
        #list_of_files = sorted(filter(lambda x: os.path.isdir(os.path.join(mother_path, x)), os.listdir(mother_path)))
        ##        for file_name in list_of_files:
        ##            print(file_name)
        ##        print(len(list_of_files))
        ##        print(list_of_files[len(list_of_files)-1])
        #list_of_files_sub = sorted(filter(lambda x: os.path.isfile(os.path.join(mother_path+list_of_files[len(list_of_files)-1], x)), os.listdir(mother_path+list_of_files[len(list_of_files)-1])))
        ##        for file_name in list_of_files_sub:
        ##            print(file_name)
        ##        print(len(list_of_files_sub))
        ##        print(list_of_files_sub[len(list_of_files_sub)-1])
        #logfile.write("%d: last file is %s\n" % (unixTime, mother_path+list_of_files[len(list_of_files)-1]+"/"+list_of_files_sub[len(list_of_files_sub)-1]))

    #return 0

def send_run_cmd(cmd, run_type, data_path):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('127.0.0.1', 10000) ## SET THE IP ADDRESS OF THE SERVER PC
    print ('connecting to %s port %s' % server_address, file=sys.stderr)
    sock.connect(server_address)

    try:
        # Send data
        ## data for HERD beam test

        last_dir, last_file = get_last_file(data_path)
        run_number = int(last_dir) * 1000 + int(last_file)

        CMD_UNIX_TIME = int(time.time())
        print(f"{cmd} TIME", CMD_UNIX_TIME )
        data = [0xFF, 0x80, 0x00, 0x8]
        data.append( (run_number >> 8) & 0xFF )
        data.append( (run_number >> 0) & 0xFF )
        data.append( (run_type >> 8) & 0xFF )
        data.append( (run_type >> 0) & 0xFF )
        if cmd == "START":
            data.append(0xEE)
            data.append(0x0)
            data.append(0x0)
            data.append(0x1)
        else:
            data.append(0xEE)
            data.append(0x0)
            data.append(0x0)
            data.append(0x0)

        data.append( (CMD_UNIX_TIME >> 24) & 0xFF )
        data.append( (CMD_UNIX_TIME >> 16) & 0xFF )
        data.append( (CMD_UNIX_TIME >> 8) & 0xFF )
        data.append( (CMD_UNIX_TIME >> 0) & 0xFF )

        with open("log.txt", 'a') as logfile:
            logfile.write("%d: last file is %s\n" % (CMD_UNIX_TIME, f"{data_path}/{last_dir}/{last_file}"))

        msg = bytearray(data)
        print("data to be sent")
        print (data)
        print (msg)
        sock.sendall(msg)

        # Look for the response
        amount_received = 0
        amount_expected = len(msg)
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print ( 'received "%s"' % data) #, file=sys.stderr)

            #run_number = int.from_bytes(data[4:6], "big")
            #run_type = int.from_bytes(data[6:8], "big")
            #cmd = int.from_bytes(data[11:12], "big")
            #timestamp = int.from_bytes(data[12:16], "big")
            #print ( 'received run_number "%s"' % run_number, file=sys.stderr)
            #print ( 'received run_type "%s"' % run_type, file=sys.stderr)
            #print ( 'received cmd "%s"' % cmd, file=sys.stderr)
            #print ( 'received timestamp "%s"' % timestamp, file=sys.stderr)

    finally:
        print ('closing socket', file=sys.stderr)
        sock.close()
