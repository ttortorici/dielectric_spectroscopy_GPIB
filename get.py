"""A script used to retrieve important, but user dependent things"""

import sys
import os
import getpass
import socket


def port():
    return 62538


def base_path():
    user = getpass.getuser()
    if os.name == 'nt':
        if user == 'etcto' and socket.gethostname() != "DESKTOP-N5IGGUN":
            path = f"D:\\Google Drive\\My Drive"
        # elif user == 'Chuck':
        else:
            path = 'C:\\Users\\Chuck\\Documents\\'
    else:
        path = ''
    return path
