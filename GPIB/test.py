import tester
import time
import sys


ls = tester.GPIB(12, '/dev/tty.usbserial-PX9HMPBU')
b = tester.GPIB(28, '/dev/tty.usbserial-PX9HMPBU')

b.open()
b.ser.write('UN DS\n')
time.sleep(0.1)
b.ser.write('FR 100\n')
time.sleep(0.1)
print('-----')
print(b.read())
print('-----')
b.ser.write('Q\n')
t0 = time.time()
x = ''
while x == '':
    time.sleep(0.5)
    x = b.read()
    print(repr(x))
print(time.time() - t0)





#print '-----'
#print repr(bridge.write('*IDN?'))
#print '-----'
#print repr(bridge.write('Q'))
#print '-----'
#print repr(bridge.write('SH UN'))
#print '-----'
#print repr(ls.write('*IDN?'))
#print '-----'
#print repr(ls.write('KRDG? A'))
#print '-----'
#print repr(ls.write('KRDG? B'))
#print '-----'
#print repr(bridge.write('Q'))
#print '-----'



#ls.open()
#repr(print ls.read())
#ls.close()
#print '...ls...'
#print repr(ls.write('*IDN?'))
#print '...ls...'
#ls.open()
#while 1:
#    blah = ls.read()
#    print repr(blah)
#    if len(blah) > 1:
#        continue
#    else:
#        break
#ls.close()
#ls.open()
#while 1:
#    blah = ls.read()
#    print repr(blah)
#    if len(blah) > 1:
#        continue
#    else:
#        break
#ls.close()
#print '-----bridge-----'
#print repr(bridge.write('*IDN?'))
#print '-----bridge-----'
#print ls.write('KDRG A')
#print '...'
#ls.open()
#print ls.read()
#ls.close()
#print '-----'
#print ls.write('KDRG B')
#print '...'
#ls.open()
#print ls.read()
#ls.close()
#print '-----'
#print bridge.write('Q')
#print '-----'
#print bridge.write('SH UN')
#print '-----'