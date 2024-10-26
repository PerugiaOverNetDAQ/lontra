import socket
import sys
import os
import subprocess
import datetime
import time

from L0 import (
    clear_autotrigger, clear_circ_buffer, read_trig_status, read_buff_status,
    stop_eventpoll, set_busy_off, set_busy_on, execute_command, log_last_file
)
def send_command_and_log(cmd, timestamp, run_type, cal_num, dat_num, logfile, pathL0, start_cal_polling, start_dat_polling):
                         
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
        print("%d: run number = %d" % (unixTime, {cal_num if run_type==0 else dat_num}))
        print("%d: timestamp from server = %d" % (unixTime, timestamp))
        print("%d: run_type = %d (%s)" % (unixTime, run_type, run_type_s))
        logfile.write("%d: starting run\n" % unixTime)
        logfile.write("%d: run number = %d\n" % (unixTime, {cal_num if run_type==0 else dat_num}))
        logfile.write("%d: timestamp from server = %d\n" % (unixTime, timestamp))
        logfile.write("%d: run_type = %d (%s)\n" % (unixTime, run_type, run_type_s))
        logfile.write(f"{unixTime}: {start_cal_polling if run_type == 0 else start_dat_polling}\n")

        execute_command(clear_autotrigger)
        execute_command(clear_circ_buffer)
        execute_command(read_trig_status)
        execute_command(read_buff_status)
        execute_command(start_cal_polling if run_type == 0 else start_dat_polling)
        execute_command(set_busy_off)
        execute_command(read_trig_status)
        log_last_file(logfile, unixTime, pathL0)

    elif cmd==0: #STOP
        print("%d: stopping run" % unixTime)
        logfile.write("%d: stopping run\n" % unixTime)

        execute_command(set_busy_on)
        execute_command(read_trig_status)
        execute_command(read_buff_status)
        execute_command(stop_eventpoll)
        logfile.write(f"{unixTime}: stopping eventpoll\n")
        logfile.write(f"{unixTime}: {stop_eventpoll}\n")
        log_last_file(logfile, unixTime, pathL0)
        time.sleep(60)
        return 0

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
#server_address = ('127.0.0.1', 10000) ## CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
server_address = ('192.168.0.60', 10000) ## CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
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
