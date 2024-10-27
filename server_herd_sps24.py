import socket
import sys
import os
import subprocess
import datetime
import time

if __name__ == '__main__':
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    #server_address = ('127.0.0.1', 10000) ## CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
    server_address = ('192.168.0.60', 8888) ## CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
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
                if data:
                    # print ('received "%s"' % data, file=sys.stderr)

                    # Decode data
                    run_type = int.from_bytes(data[1:8], "big")
                    cmd = int.from_bytes(data[11:12], "big")
                    timestamp = int.from_bytes(data[12:16], "big")
                    print ( 'received run_type %i' % run_type, file=sys.stderr)
                    print ( 'received cmd %i' % cmd, file=sys.stderr)
                    print ( 'received timestamp %i' % timestamp, file=sys.stderr)

                    if cmd==1: #START
                        print("Starting run")
                        if run_type==0:
                            print("\tStarting CAL run")
                            os.system("python3 start_L0.py 0")
                        else:
                            print("\tStarting BEAM run")
                            os.system("python3 start_L0.py 1")
                    elif cmd==0: #STOP
                        print("Stopping run")
                        os.system("python3 stop_L0.py")
                        # Wait 60 seconds with a countdown
                        print("Waiting 60 seconds for L0 to stop")
                        for i in range(60, 0, -1):
                            print(i)
                            time.sleep(1)

                    # Send back data to the client
                    connection.sendall(data)
                else:
                    print ('no more data from', client_address, file=sys.stderr)
                    break
        finally:
            # Clean up the connection
            connection.close()
