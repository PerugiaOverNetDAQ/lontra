import datetime
import time
from L0 import (
    set_busy_on, read_trig_status, read_buff_status, stop_eventpoll, 
    execute_command, log_last_file
)

pathL0 = "/Data/BLOCKS/USBLF_PCGSC03/"
logfile = open('log.txt', 'a')

def send_stop_command_and_log(timestamp=0):
    unixTime = int(time.time())
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
    send_stop_command_and_log(0)
