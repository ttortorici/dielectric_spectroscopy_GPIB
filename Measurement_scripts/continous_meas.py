import time
import AH2700A
import get

b = AH2700A.dev(28, get.serialport())

while 1:
    print(b.get_front_panel())
    time.sleep(0.5)
