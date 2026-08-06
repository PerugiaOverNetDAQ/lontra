import socket
import datetime
import time
import sys

from L0 import (
    clear_autotrigger, clear_circ_buffer, read_trig_status, read_buff_status,
    stop_eventpoll, set_busy_on, set_busy_off, execute_command, log_last_file
)

#logfile = open('/Data/log/beamtest_202411_trigger_log', 'a')
#pathL0 = "/Data/BLOCKS/USBLF_PCGSC03/"
logfile = open('./CRSPACE_202608_L0_log', 'a')
pathL0 = "../Data/"

def print_and_log(message):
    print(message)
    logfile.write(message + "\n")
    logfile.flush()

def send_start_command_and_log(master_timestamp, run_type, logfile, pathL0):
    cal_num = 00
    dat_num = 00

    # Read the values from runnum.conf
    with open("runnum.conf", "r") as f:
        for line in f:
            if line.startswith("cal_num"):
                cal_num = int(line.split()[2])
            elif line.startswith("dat_num"):
                dat_num = int(line.split()[2])

    # Define start polling commands
    start_cal_polling = f"my-t W JMDC-SELF 1F0600 {cal_num:02x} 0C"
    start_dat_polling = f"my-t W JMDC-SELF 1F0600 {dat_num:02x} 0D"

#    print(run_type)

    unixTime = int(time.time())
    print_and_log(f"{unixTime}: starting run\n")
    
    # Update cal_num and dat_num
    if run_type == '0':
        cal_num += 1
        if (cal_num > 255): cal_num=0
        print_and_log(f"{unixTime}: received CAL START with master timestamp {master_timestamp}\n")
        print_and_log(f"{unixTime}: starting CAL number {cal_num:02x}\n")
        start_polling_command = start_cal_polling
        print_and_log(f"{unixTime}: {start_polling_command}\n")
    else:
        print_and_log(f"{unixTime}: received DAT START with master timestamp {master_timestamp}\n")
        print_and_log(f"{unixTime}: starting DAT number {dat_num:02x}\n")
        start_polling_command = start_dat_polling
        print_and_log(f"{unixTime}: {start_polling_command}\n")
        dat_num += 1
        if (dat_num > 255): dat_num=0

    # Update runnum.conf
    with open("runnum.conf", "w") as f:
        f.write("cal_num = " + str(cal_num) + "\n")
        f.write("dat_num = " + str(dat_num) + "\n")
        f.flush()
    print_and_log(f"{unixTime}: runnum file updated\n")

    execute_command(clear_autotrigger)
    execute_command(clear_circ_buffer)
    execute_command(read_trig_status)
    execute_command(read_buff_status)
    execute_command(start_polling_command)
    execute_command(set_busy_off)
    execute_command(read_trig_status)
    log_last_file(logfile, unixTime, pathL0)

#    print(run_type)
    if run_type == '0':
        ect.enable_calibration_trigger()
    else:
        edt.enable_daq_trigger()
    
def send_stop_command_and_log(master_timestamp, logfile, pathLO):
    unixTime = int(time.time())
    print_and_log(f"{unixTime}: received STOP with master timestamp {master_timestamp}\n")
    print_and_log(f"{unixTime}: stopping run\n")

    dt.disable_all_triggers()    
    
    execute_command(set_busy_on)
    execute_command(read_trig_status)
    execute_command(read_buff_status)
    execute_command(stop_eventpoll)
    print_and_log(f"{unixTime}: stopping eventpoll\n")
    print_and_log(f"{unixTime}: {stop_eventpoll}\n")
    log_last_file(logfile, unixTime, pathL0)
    time.sleep(60)

    
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

                        if cmd == '0':
                            send_start_command_and_log(master_timestamp, trigType, logfile, pathL0)
                        elif cmd == '1':
                            send_stop_command_and_log(master_timestamp, logfile, pathL0)
                        
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
