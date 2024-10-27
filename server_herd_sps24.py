import socket
import sys
import datetime

from L0 import (
    clear_autotrigger, clear_circ_buffer, read_trig_status, read_buff_status,
    stop_eventpoll, set_busy_on, set_busy_off, execute_command, log_last_file
)

def send_start_command_and_log(master_timestamp, run_type, cal_num, dat_num, logfile, pathL0, start_polling_command):
    unixTime = int(time.time())
    logfile.write(f"{unixTime}: starting run\n")

    # Update cal_num and dat_num
    if run_type == 0:
        cal_num += 1
        logfile.write(f"{unixTime}: received CAL START with master timestamp {master_timestamp}\n")
        logfile.write(f"{unixTime}: starting CAL number {cal_num:02x}\n")
        logfile.write(f"{unixTime}: {start_polling_command}\n")
    else:
        logfile.write(f"{unixTime}: received DAT START with master timestamp {master_timestamp}\n")
        logfile.write(f"{unixTime}: starting DAT number {dat_num:02x}\n")
        logfile.write(f"{unixTime}: {start_polling_command}\n")
        dat_num += 1

    # Update runnum.conf
    with open("runnum.conf", "w") as f:
        f.write("cal_num = " + str(cal_num) + "\n")
        f.write("dat_num = " + str(dat_num) + "\n")
    logfile.write(f"{unixTime}: {start_polling_command}\n")

    execute_command(clear_autotrigger)
    execute_command(clear_circ_buffer)
    execute_command(read_trig_status)
    execute_command(read_buff_status)
    execute_command(start_polling_command)
    execute_command(set_busy_off)
    execute_command(read_trig_status)
    log_last_file(logfile, unixTime, pathL0)

def send_stop_command_and_log(master_timestamp):
    unixTime = int(time.time())
    logfile.write(f"{unixTime}: received STOP with master timestamp {master_timestamp}\n")
    logfile.write(f"{unixTime}: stopping run\n")

    execute_command(set_busy_on)
    execute_command(read_trig_status)
    execute_command(read_buff_status)
    execute_command(stop_eventpoll)
    logfile.write(f"{unixTime}: stopping eventpoll\n")
    logfile.write(f"{unixTime}: {stop_eventpoll}\n")
    log_last_file(logfile, unixTime, pathL0)
    time.sleep(60)


if __name__ == '__main__':

    cal_num = 00
    dat_num = 00

    # Read the values from runnum.conf
    with open("runnum.conf", "r") as f:
        for line in f:
            if line.startswith("cal_num"):
                cal_num = int(line.split()[2])
            elif line.startswith("dat_num"):
                dat_num = int(line.split()[2])

    logfile = open('log.txt', 'a')
    pathL0 = "/Data/BLOCKS/USBLF_PCGSC03/"

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    server_address = ('192.168.0.60', 8888)  # CHANGE HERE THE IP ADDRESS OF THE SERVER PC.
    print("starting up on %s port %s" % server_address, file=sys.stderr)
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)

    # Address to listen to
    listen_address = '192.168.0.105' # CHANGE HERE THE IP ADDRESS OF THE CLIENT PC.

    while True:
        print("waiting for a connection", file=sys.stderr)
        connection, client_address = sock.accept()
        
        if client_address[0] != listen_address:
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
                    if b'\n' in data_buffer:
                        # Process the complete message
                        complete_message = data_buffer.strip().decode()  # Remove newline and decode
                        print(f'received complete message: "{complete_message}"', file=sys.stderr)
                        
                        # Process the message in the form YYYYMMDD_HHMM_trigType_cmd (e.g.20231027_1740_0_0)
                        # trigType: 0 = CAL, 1 = BEAM
                        # cmd: 0 = start, 1 = stop

                        date = complete_message[0:8]
                        time = complete_message[8:12]
                        trigType = complete_message[13]
                        cmd = complete_message[15]

                        # Convert date and time to unix timestamp
                        date_obj = datetime.datetime.strptime(date, '%Y%m%d')
                        time_obj = datetime.datetime.strptime(time, '%H%M')
                        master_timestamp = int(datetime.datetime.timestamp(date_obj) + datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute).total_seconds())
                        print(f'master_timestamp: {master_timestamp}', file=sys.stderr)
                        print(f'trigType: {trigType}', file=sys.stderr)
                        print(f'cmd: {cmd}', file=sys.stderr)

                        # Define start polling commands
                        start_cal_polling = f"my-t W JMDC-SELF 1F0600 {cal_num:02x} 0C"
                        start_dat_polling = f"my-t W JMDC-SELF 1F0600 {dat_num:02x} 0D"

                        if cmd == '0':
                            send_start_command_and_log(master_timestamp, trigType, cal_num, dat_num, logfile, pathL0, start_cal_polling if trigType == 0 else start_dat_polling)
                        elif cmd == '1':
                            send_stop_command_and_log(master_timestamp)

                        # Clear the buffer after processing
                        data_buffer = b''
                        break  # Exit after processing a single complete message
                else:
                    print("no more data from", client_address, file=sys.stderr)
                    break
        finally:
            connection.close()
