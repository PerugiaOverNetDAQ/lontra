import os

# Define the commands as variables
clear_autotrigger = "my-t W 3C 4 02 01"
clear_circ_buffer = "my-t W 3C 14"
read_trig_status = "my-t R 3C 4"
read_buff_status = "my-t R 3C 14"
stop_eventpoll = "my-t W JMDC-SELF 1F0601"
set_busy_off = "my-t W 3C 4 00 01"
set_busy_on = "my-t W 3C 4 02 01"

# Define reusable functions for command execution and logging
def execute_command(command):
    os.system(command)

def log_last_file(logfile, unixTime=0, moth_path="/"):
    list_of_files = sorted(filter(lambda x: os.path.isdir(os.path.join(moth_path, x)), os.listdir(moth_path)))
    list_of_files_sub = sorted(filter(lambda x: os.path.isfile(os.path.join(moth_path + list_of_files[-1], x)), os.listdir(moth_path + list_of_files[-1])))
    logfile.write(f"{unixTime}: last file is {moth_path + list_of_files[-1]}/{list_of_files_sub[-1]}\n")
