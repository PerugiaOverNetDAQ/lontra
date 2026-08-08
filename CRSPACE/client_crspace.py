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

# Lista dei server con cui comunicare (IP/hostname, porta)
SERVERS = [
    ("nmori-laptop-lab2.dyndns.cern.ch", 9999), #FI
    ("128.141.41.216", 10000), #BA
    ("194.12.164.162", 10000), #PG
    #("127.0.0.1", 8888),
]

def send_command(run_type, cmd):
    run_type = run_type.upper()
    cmd = cmd.upper()

    if run_type not in ["BEAM", "CAL"]:
        raise ValueError(f"run_type non valido: {run_type}. Usa 'BEAM' o 'CAL'.")

    if cmd not in ["START", "STOP"]:
        raise ValueError(f"cmd non valido: {cmd}. Usa 'START' o 'STOP'.")

    bt = 1 if run_type == "BEAM" else 0
    
    # Lettura parametri da runnum.conf
    config = {}
    with open("runnum.conf", "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.split("=")
                config[key.strip()] = int(val.strip())
                
    key_to_use = "cal_num" if bt == 0 else "dat_num"
    run_number = config[key_to_use]
        
    #    START_UNIX_TIME = int(time.time()) #GMT
    START_UNIX_TIME = int(time.time() + time.localtime().tm_gmtoff) #local + DST
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

    # Ciclo su tutti i server configurati
    for server_address in SERVERS:
        print(f'connecting to {server_address[0]} port {server_address[1]}', file=sys.stderr)
        
        # 1. Creazione socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # 2. Connessione al server corrente
            sock.connect(server_address)
            
            # 3. Invio messaggio
            sock.sendall(msg + b'\n')

            # 4. Ricezione aknowledgment
            amount_received = 0
            amount_expected = len(msg)
            while amount_received < amount_expected:
                data = sock.recv(16)
                if not data:
                    # Connessione chiusa dal server
                    break
                amount_received += len(data)
                print ( 'received "%s"' % data) #, file=sys.stderr)
        
            run_number = int.from_bytes(data[4:6], "big")
            run_type = int.from_bytes(data[6:8], "big")
            command = int.from_bytes(data[11:12], "big")
            timestamp = int.from_bytes(data[12:16], "big")
            print ( 'received run_number "%s"' % run_number, file=sys.stderr)
            print ( 'received run_type "%s"' % run_type, file=sys.stderr)
            print ( 'received command "%s"' % command, file=sys.stderr)
            print ( 'received timestamp "%s"' % timestamp, file=sys.stderr)

        except Exception as e:
            print(f'Errore con il server {server_address}: {e}', file=sys.stderr)
            
        finally:
            # 4. Chiusura del socket per il server corrente
            print(f'closing socket for {server_address}', file=sys.stderr)
            sock.close()
        
    # Incrementa il contatore e aggiorna il file SOLO se il comando è START
    if cmd == "START":
        config[key_to_use] += 1
        with open("runnum.conf", "w") as f:
            for key, val in config.items():
                f.write(f"{key}={val}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python client_herd.py <run_type: BEAM|CAL> <cmd: START|STOP>", file=sys.stderr)
        sys.exit(1)

    send_command(sys.argv[1], sys.argv[2])
