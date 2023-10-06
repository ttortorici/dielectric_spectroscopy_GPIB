from communication.devices.lakeshore import Client as Lakeshore
import numpy as np
import time
import os


def run_command_line():
    ls = Lakeshore(331)

    setpoint = None

    with open(os.path.join("text", "temperature control startup.txt"), "r") as startup_file:
        print(startup_file.read())

    run = True
    while run:
        command = input("LS>").upper().split(" ")
        if command[0] == "QUIT" or command == "EXIT":
            run = False
            print("Exiting", end="")
            for _ in range(5):
                time.sleep(1)
                print(" .", end="")
        elif command[0] == "HELP":
            with open(os.path.join("text", "temperature control help.txt"), "r") as help_file:
                print(help_file.read())

        elif command[0] == "PID?":
            print("P={}; I={}; D={}".format(*ls.read_pid()))
        elif command[0] == "PID":
            if len(command) < 4:
                print('No PID values given; please type "PID X, Y, Z" to set P=X, I=Y, D=Z.')
            else:
                p = float(command[1].strip(","))
                i = float(command[2].strip(","))
                d = float(command[3].strip(","))
                ls.set_pid(p, i, d)
                print("Set P=X, I=Y, D=Z.")

        elif command[0] == "RAMP?":
            print("{} K/min".format(ls.read_ramp_speed()))
        elif command[0] == "RAMP":
            if len(command) == 1:
                print('No ramp-rate given; please type "RAMP X" to set the ramp-rate to X K/min.')
            else:
                ls.set_ramp_speed(float(command[1]))

        elif command[0] == "SP?":
            if setpoint is not None:
                print("{} K".format(setpoint))
            else:
                print("{} K".format(ls.read_setpoint()))
        elif command[0] == "SP":
            if len(command) == 1:
                print('No temperature given; please type "SP X" to set the set-point to X Kelvin.')
            else:
                setpoint = float(command[1])
                ls.set_setpoint(setpoint)
                print("Set-point ramping to {} K".format(setpoint))

        elif command[0] == "RAW":
            if len(command) == 1:
                print('No message given; please type "RAW [message]" to send [message] to the Lakeshore.')
            else:
                message_back = ls.write(command[1].upper())
                print('Sent "{}" to the LakeShore.'.format(command[1].upper()))
                print('Response: {}'.format(message_back))


if __name__ == "__main__":
    run_command_line()
