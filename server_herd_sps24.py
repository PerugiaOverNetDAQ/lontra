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

cal_num = 0x00
dat_num = 0x00

# Read the values from runnum.conf
with open("runnum.conf", "r") as f:
    for line in f:
        if line.startswith("cal_num"):
            cal_num = line.split()[2]
        elif line.startswith("dat_num"):
            dat_num = line.split()[2]

# Set Trigger number to 1 and clear Auto-trigger with local busy set
clear_autotrigger = "my-t W 3C 4 02 01"

# Clear circular buffer
clear_circ_buffer = "my-t W 3C 14"

# Read back trigger status
read_trig_status = "my-t R 3C 4"

# Read back buffer status
read_buff_status = "my-t R 3C 14"

# Start server DAQ
# first  data: 00-FF
# second data: CAL=0C, DAQ=0D
start_cal_polling = "my-t W JMDC:SELF 1F0600 " + f"{cal_num:0{2}x}" + " 0C"
start_dat_polling = "my-t W JMDC:SELF 1F0600 " + f"{dat_num:0{2}x}" + " 0D"

# Set local busy to 0 to enable trigger coming
set_busy_off = "my-t W 3C 4 00 01"

# Stop trigger by set local busy to 1
set_busy_on = "my-t W 3C 4 02 01"

# Stop server DAQ
stop_eventpoll = "my-t W JMDC:SELF 1F0601"

pathL0 = "/Data/BLOCKS/USBLF_PCGSC03/"

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
        cal_num += 1
    elif run_type==1:
        run_type_s = "BEAM"
        dat_num += 1

    # Update runnum.conf
    with open("runnum.conf", "w") as f:
        f.write("cal_num = " + str(cal_num) + "\n")
        f.write("dat_num = " + str(dat_num) + "\n")

    presentDate = datetime.datetime.now()
    unixTime = time.mktime(presentDate.timetuple())
    print("unix_timestamp => %d" % unixTime)

    if cmd==1: #START
        print("%d: starting run" % unixTime)
        print("%d: run number = %d" % (unixTime, run_number))
        print("%d: timestamp from server = %d" % (unixTime, timestamp))
        print("%d: run_type = %d (%s)" % (unixTime, run_type, run_type_s))
        logfile.write("%d: starting run\n" % unixTime)
        logfile.write("%d: run number = %d\n" % (unixTime, run_number))
        logfile.write("%d: timestamp from server = %d\n" % (unixTime, timestamp))
        logfile.write("%d: run_type = %d (%s)\n" % (unixTime, run_type, run_type_s))
        os.system(clear_autotrigger)
        os.system(clear_circ_buffer)
        os.system(read_trig_status)
        os.system(read_buff_status)
        if run_type==0:	
            os.system(start_cal_polling)
            logfile.write("%d: %s\n" % (unixTime, start_cal_polling))
        else:
            os.system(start_dat_polling)
            logfile.write("%d: %s\n" % (unixTime, start_dat_polling))
        os.system(set_busy_off)
        os.system(read_trig_status)
        log_last_file(unixTime, pathL0)
    elif cmd==0: #STOP
        print("%d: stopping run" % unixTime)
        logfile.write("%d: stopping run\n" % unixTime)
        os.system(set_busy_on)
        os.system(read_trig_status)
        os.system(read_buff_status)
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
