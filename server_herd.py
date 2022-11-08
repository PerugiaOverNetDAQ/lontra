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

logfile = open('log.txt', 'a')

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
        print(os.system("my-t w 40 4 0100")) #autotrigger
        logfile.write("%d: my-t w 40 4 0100\n" % unixTime)
    elif cmd==0: #STOP
        print("%d: stopping run" % unixTime)
        logfile.write("%d: stopping run\n" % unixTime)
        print(os.system("my-t w 40 4 0000")) #stop autotrigger
        logfile.write("%d: my-t w 40 4 0000\n" % unixTime)
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
