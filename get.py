"""A script used to retrieve important, but user dependent things"""

import sys
import os
import getpass
import socket

port = 62538


def serialport():
    """Finds the serialport depending on what system you're running on"""
    if os.name == 'posix':
        if sys.platform == 'linux2' or sys.platform == 'linux': # for linux, may need to change ending number
            # platform = 'lin'
            serial_port = '/dev/ttyUSB0'
        elif sys.platform == 'darwin':
            # platform = 'mac'
            serial_port = '/dev/tty.usbserial-PX9HMPBU'
    elif os.name == 'nt':
        # platform = 'win'
        serial_port = 'COM4'
    else:
        serial_port = ''
    return serial_port


def google_drive():
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
                path = 'C:\\Users\\Chuck\\OneDrive - UCB-O365\\'
                # path = 'C:\\Users\\%s\\My Drive' % user
        else:
            path = ''
    # print(f'\n\n\n{path}\n\n\n')
    return path
