import u6

lj = u6.U6()

lj.getFeedback(u6.DAC0_8(lj.voltageToDACBits(0, dacNumber=0, is16Bits=False)))

for ii in xrange(4):
  print lj.getAIN(ii)
