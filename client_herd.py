# client_herd.py
# Author: L. Di Venere
# This script should run on the PC controlling the master DAQ
# The script sends the message to each subdetector (server) and waits for a response from the server.
# When the server has answered correctly, the client script moves to the next step (in this example, the script is terminated).
#
# NOTE: change the IP address in the script to the current IP address of the server PC..

import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('127.0.0.1', 8888) ## SET THE IP ADDRESS OF THE SERVER PC
print ('connecting to %s port %s' % server_address, file=sys.stderr)
sock.connect(server_address)

try:
    # Send data
    ## data for HERD beam test
    run_number=1
    bt=0  # CAL
    #bt=1  # BEAM
    cmd="START"
    #cmd="STOP"
    START_UNIX_TIME = int(time.time())
    print("START TIME", START_UNIX_TIME )
    data = [0xFF, 0x80, 0x00, 0x8]
    data.append( (run_number >> 8) & 0xFF )
    data.append( (run_number >> 0) & 0xFF )
    data.append( (bt >> 8) & 0xFF )
    data.append( (bt >> 0) & 0xFF )
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

    data.append( (START_UNIX_TIME >> 24) & 0xFF )
    data.append( (START_UNIX_TIME >> 16) & 0xFF )
    data.append( (START_UNIX_TIME >> 8) & 0xFF )
    data.append( (START_UNIX_TIME >> 0) & 0xFF )
    
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
