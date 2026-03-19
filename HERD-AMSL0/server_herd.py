## server_herd.py
# Author: L. Di Venere
# This script should run on the PC controlling the DAQ of each subdetector
# The script waits for the message from the client and executes the start or stop functions depending on the message content
# If the execution of these function is successful, the server sends back the message to the client.
#
# NOTE: change the IP address in the script to the current IP address of the PC running this script (server).
# NOTE: check the firewall configuration of the server pc, to be able to send/receive TCP/IP message over a specific port .

import socket
import sys
import os
import subprocess
import datetime
import time

start_autotrigger = "my-t w 40 4 0100"
stop_autotrigger = "my-t w 40 4 0000"
start_eventpoll = "my-t w 1FF 1F0205 00 10 63 69 38 1E 00 00 03 E8 00 0C 02 9F 03 83 0B 00 00 04 08 13 0B 00"
stop_eventpoll = "my-t w 1FF 1F0205 00 E0"

pathL0 = "/amssw/duranti/AMSWireDAQ/trunkBT/DecodeL0/Data/L0/BLOCKS/PG/USBL0_PG_LEFV2BEAM1/"

logfile = open('log.txt', 'a')

def log_last_file(unixTime=0, moth_path="/"):
    list_of_files = sorted(filter(lambda x: os.path.isdir(os.path.join(moth_path, x)), os.listdir(moth_path)))
    #        for file_name in list_of_files:
    #            print(file_name)
    #        print(len(list_of_files))
    #        print(list_of_files[len(list_of_files)-1])
    list_of_files_sub = sorted(filter(lambda x: os.path.isfile(os.path.join(moth_path+list_of_files[len(list_of_files)-1], x)), os.listdir(moth_path+list_of_files[len(list_of_files)-1])))
    #        for file_name in list_of_files_sub:
    #            print(file_name)
    #        print(len(list_of_files_sub))
    #        print(list_of_files_sub[len(list_of_files_sub)-1])
    logfile.write("%d: last file is %s\n" % (unixTime, moth_path+list_of_files[len(list_of_files)-1]+"/"+list_of_files_sub[len(list_of_files_sub)-1]))
    return 0

def send_command_and_log(cmd=0, run_number=0, timestamp=0, run_type=0):

    print('received run_number %i' % run_number, file=sys.stderr)
    print('received run_type %i' % run_type, file=sys.stderr)
    print('received cmd %i' % cmd, file=sys.stderr)
    print('received timestamp %i' % timestamp, file=sys.stderr)

    run_type_s = "UNDEF"
    if run_type==0:
        run_type_s = "CAL"
    elif run_type==1:
        run_type_s = "BEAM"
    
    presentDate = datetime.datetime.now()
    unixTime = time.mktime(presentDate.timetuple())
    # print regular python date&time
#    print("date_time =>", presentDate)
    # displaying unix timestamp after conversion
    print("unix_timestamp => %d" % unixTime)

    #    pippo = os.system("echo prova")
#    pippo = subprocess.run(["echo", "prova"], capture_output=True)

    if cmd==1: #START
        print("%d: starting run" % unixTime)
        print("%d: run number = %d" % (unixTime, run_number))
        print("%d: timestamp from server = %d" % (unixTime, timestamp))
        print("%d: run_type = %d (%s)" % (unixTime, run_type, run_type_s))
        logfile.write("%d: starting run\n" % unixTime)
        logfile.write("%d: run number = %d\n" % (unixTime, run_number))
        logfile.write("%d: timestamp from server = %d\n" % (unixTime, timestamp))
        logfile.write("%d: run_type = %d (%s)\n" % (unixTime, run_type, run_type_s))
        if run_type==0:
            os.system(start_autotrigger)
            logfile.write("%d: %s\n" % (unixTime, start_autotrigger))
        os.system(start_eventpoll)
        logfile.write("%d: %s\n" % (unixTime, start_eventpoll))
        log_last_file(unixTime, pathL0)
    elif cmd==0: #STOP
        print("%d: stopping run" % unixTime)
        logfile.write("%d: stopping run\n" % unixTime)
        os.system(stop_autotrigger)
        logfile.write("%d: %s\n" % (unixTime, stop_autotrigger))
        os.system(stop_eventpoll)
        logfile.write("%d: %s\n" % (unixTime, stop_eventpoll))
        log_last_file(unixTime, pathL0)
        time.sleep(60)

    return 0

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
#server_address = ('127.0.0.1', 10000) ## CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
server_address = ('', 10000) ## CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
print( 'starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection', file=sys.stderr)
    connection, client_address = sock.accept()
    try:
        print ('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            #print ('received "%s"' % data, file=sys.stderr)
            if data:
                # Decode data
                run_number = int.from_bytes(data[4:6], "big")
                run_type = int.from_bytes(data[6:8], "big")
                cmd = int.from_bytes(data[11:12], "big")
                timestamp = int.from_bytes(data[12:16], "big")
                print ( 'received run_number %i' % run_number, file=sys.stderr)
                print ( 'received run_type %i' % run_type, file=sys.stderr)
                print ( 'received cmd %i' % cmd, file=sys.stderr)
                print ( 'received timestamp %i' % timestamp, file=sys.stderr)
                send_command_and_log(cmd, run_number, timestamp, run_type)
                #print (sys.stderr, 'sending data back to the client')
                connection.sendall(data)
            else:
                print ('no more data from', client_address, file=sys.stderr)
                break
    finally:
        # Clean up the connection
        connection.close()
