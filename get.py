"""A script used to retrieve important, but user dependent things"""

import subprocess
import os
import socket


def port():
    return 62538


def base_path():
    user = os.getlogin()
    if os.name == 'nt':
        if user == 'etcto' and socket.gethostname() != "DESKTOP-N5IGGUN":
            path = f"D:\\Google Drive\\My Drive"
        # elif user == 'Chuck':
        else:
            path = f'C:\\Users\\{user}\\Documents\\'
    else:
        path = ''
    return path


def uuid():
    cmd = 'wmic csproduct get uuid'
    uuid_ = str(subprocess.check_output(cmd))
    pos1 = uuid_.find("\\n") + 2
    uuid_ = uuid_[pos1:-15]
    return uuid_


def onedrive():
    if uuid() == "1F0050C0-00C6-0C00-E9B7-BCAEC5601728":
        path = "F:\\OneDrive - UCB-O365\\Rogerslab3"
    else:
        path = ""
    return path
