import socket
import datetime
import time
import sys

if __name__ == '__main__':

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
#    server_address = ('192.168.0.60', 8888)  # CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
    server_address = ('', 8888)  # CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
    print("starting up on %s port %s" % server_address, file=sys.stderr)
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)

    # Address to listen to
    listen_address = '192.168.0.105' # CHANGE HERE THE IP ADDRESS OF THE CLIENT PC.
    listen_address_self = '127.0.0.1'
    list_la = {listen_address, listen_address_self}

    while True:
        print("waiting for a connection", file=sys.stderr)
        connection, client_address = sock.accept()
        
        if client_address[0] not in list_la:
            print("\nconnection from", client_address, file=sys.stderr)
            print("client not allowed, closing connection", file=sys.stderr)
            connection.close()
            continue

        try:
            print("\nconnection from", client_address)

            # Buffer to accumulate data until the newline character
            data_buffer = b''

            # Loop to receive data until a newline character is detected
            while True:
                data = connection.recv(1024)
                if data:
                    data_buffer += data  # Accumulate data chunks
                    #print(data)
                    if b'\n' in data_buffer:
                        # Process the complete message
                        print(data_buffer)
                        # Estrai i dati binari senza il carattere \n finale
                        raw_msg = data_buffer.strip()
                        
                        # Parsing dei byte inviati dal client
                        run_number = int.from_bytes(raw_msg[4:6], "big")
                        bt = int.from_bytes(raw_msg[6:8], "big")
                        cmd_raw = int.from_bytes(raw_msg[8:12], "big")
                        cmd = "START" if cmd_raw == 0xEE000001 else "STOP"
                        timestamp = int.from_bytes(raw_msg[12:16], "big")
                        
                        # Stampa i valori decodificati
                        print(f'Received run_number: {run_number}')
                        print(f'Received bt: {bt} ({"BEAM" if bt == 1 else "CAL"})')
                        print(f'Received cmd: {cmd}')
                        print(f'Received timestamp: {timestamp} ({datetime.datetime.fromtimestamp(timestamp)})')

                        # Re-invia al client l'esatto pacchetto di byte ricevuto (incluso \n)
                        connection.sendall(data_buffer)
                        
                        # Clear the buffer after processing
                        data_buffer = b''
                        break  # Exit after processing a single complete message
                else:
                    print("no more data from", client_address, file=sys.stderr)
                    break
        finally:
            connection.close()
