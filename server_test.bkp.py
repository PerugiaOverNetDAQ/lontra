import socket
import sys
import datetime

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket to the port
server_address = ('192.168.0.60', 8888)  # CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
print("starting up on %s port %s" % server_address, file=sys.stderr)
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)

listen_address = '192.168.0.105'

while True:
    print("waiting for a connection", file=sys.stderr)
    connection, client_address = sock.accept()
    
    if client_address[0] != listen_address:
        print("connection from", client_address, file=sys.stderr)
        print("client not allowed, closing connection", file=sys.stderr)
        connection.close()
        continue

    try:
        print("connection from", client_address)

        # Buffer to accumulate data until the newline character
        data_buffer = b''

        # Loop to receive data until a newline character is detected
        while True:
            data = connection.recv(1024)
            if data:
                data_buffer += data  # Accumulate data chunks
                if b'\n' in data_buffer:
                    # Process the complete message
                    complete_message = data_buffer.strip().decode()  # Remove newline and decode
                    print(f'received complete message: "{complete_message}"', file=sys.stderr)
                    
                    # Process the message in the form YYYYMMDD_HHMM_trigType_cmd
                    # Example: 20231027_1740_0_0
                    # trigType: 0 = CAL, 1 = BEAM
                    # cmd: 0 = start, 1 = stop

                    date = complete_message[0:8]
                    time = complete_message[8:12]
                    trigType = complete_message[13]
                    cmd = complete_message[15]

                    # Convert date and time to unix timestamp
                    date_obj = datetime.datetime.strptime(date, '%Y%m%d')
                    time_obj = datetime.datetime.strptime(time, '%H%M')
                    unix_timestamp = int(datetime.datetime.timestamp(date_obj) + datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute).total_seconds())
                    print(f'unix timestamp: {unix_timestamp}', file=sys.stderr)

                    print(f'trigType: {trigType}', file=sys.stderr)
                    print(f'cmd: {cmd}', file=sys.stderr)

                    # Clear the buffer after processing
                    data_buffer = b''
                    break  # Exit after processing a single complete message
            else:
                print("no more data from", client_address, file=sys.stderr)
                break
    finally:
        connection.close()
