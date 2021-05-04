"""A script used to retrieve important, but user dependent things"""

import sys
import os

def serialport():
    """Finds the serialport depending on what system you're running on"""
    if os.name == 'posix':
        if sys.platform == 'linux2' or sys.platform == 'linux': # for linux, may need to change ending number
            # platform = 'lin'
            port = '/dev/ttyUSB0'
        elif sys.platform == 'darwin': # it is possible that the serial number is different, "ls /dev" in a terminal to find out
            # platform = 'mac'
            port = '/dev/tty.usbserial-PX9HMPBU'
    elif os.name == 'nt':
            # platform = 'win'
            port = ''
    else:
        port = ''
    return port

def googledrive():
    """locates where your google drive is depending on who you are currently generalized for mac users."""
    """For compatiblity, you must rename "Google Drive" folder to "Google_Drive" which will raise an error for
    google drive, which is easily fixed by relocating the folder for it"""
    import getpass
    user = getpass.getuser()
    if sys.platform == 'darwin': # for mac users
        path = '/Users/%s/Google_Drive/' % (user)
    elif (user == 'etortorici' or user == 'root') and sys.platform == 'linux2': # legacy for linux
        #path = '/home/etortorici/Google_Drive/'
        path = '/home/etortorici/Documents/'
    else:
        #if user == 'Chuck':
        if os.name == 'nt':
            path = 'C:\Users\%s\Google Drive' % user
        else:
            path = ''
    return path
