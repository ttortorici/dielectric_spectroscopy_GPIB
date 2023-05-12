"""A script used to retrieve important, but user dependent things"""

import sys
import os
import getpass
import socket


def port():
    return 62538


def base_path():
    """locates where your google drive is depending on who you are currently generalized for mac users."""
    """For compatiblity, you must rename "Google Drive" folder to "Google_Drive" which will raise an error for
    google drive, which is easily fixed by relocating the folder for it"""
    user = getpass.getuser()
    if sys.platform == 'darwin':  # for mac users
        path = '/Users/%s/Google_Drive/' % (user)
    elif sys.platform == 'linux':
        if user == 'etortoric':
            path = '/home/etortoric/Documents/Google_Drive'
        else:
            path = ''
    else:
        if os.name == 'nt':
            if user == 'etcto' and socket.gethostname() != "DESKTOP-N5IGGUN":
                path = f"D:\\Google Drive\\My Drive"
            # elif user == 'Chuck':
            else:
                path = 'C:\\Users\\Chuck\\Documents\\'
        else:
            path = ''
    return path
