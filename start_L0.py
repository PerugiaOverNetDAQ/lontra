import sys
import datetime
import time
from L0 import (
    clear_autotrigger, clear_circ_buffer, read_trig_status, read_buff_status,
    stop_eventpoll, set_busy_off, execute_command, log_last_file
)
def send_command_and_log(timestamp, run_type, cal_num, dat_num, logfile, pathL0, start_cal_polling, start_dat_polling):
    unixTime = int(time.time())
    logfile.write(f"{unixTime}: starting run\n")
    
    execute_command(clear_autotrigger)
    execute_command(clear_circ_buffer)
    execute_command(read_trig_status)
    execute_command(read_buff_status)
    execute_command(start_cal_polling if run_type == 0 else start_dat_polling)
    # Update cal_num and dat_num
    if run_type == 0:
        cal_num += 1
        logfile.write(f"{unixTime}: starting CAL number {cal_num:02x}\n")
        logfile.write(f"{unixTime}: {start_cal_polling}\n")
    else:
        logfile.write(f"{unixTime}: starting DAT number {dat_num:02x}\n")
        logfile.write(f"{unixTime}: {start_dat_polling}\n")
        dat_num += 1

    # Update runnum.conf
    with open("runnum.conf", "w") as f:
        f.write("cal_num = " + str(cal_num) + "\n")
        f.write("dat_num = " + str(dat_num) + "\n")
    logfile.write(f"{unixTime}: {start_cal_polling if run_type == 0 else start_dat_polling}\n")
    execute_command(set_busy_off)
    execute_command(read_trig_status)
    log_last_file(logfile, unixTime, pathL0)

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

    if len(sys.argv) < 2:
        print("Usage: python start_L0.py <run_type (0 CAL; 1 DAT)>")
        sys.exit(0)
    else:
        # Define paths and start polling commands
        start_cal_polling = f"my-t W JMDC-SELF 1F0600 {cal_num:02x} 0C"
        start_dat_polling = f"my-t W JMDC-SELF 1F0600 {dat_num:02x} 0D"

        run_type = int(sys.argv[1])
        send_command_and_log(0, run_type, cal_num, dat_num, logfile, pathL0, start_cal_polling, start_dat_polling)

    logfile.close()