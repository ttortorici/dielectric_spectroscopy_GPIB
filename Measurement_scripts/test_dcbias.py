import capacitance_measurement_tools as cap
import time


def takeInput():
    """This function will be executed via thread"""
    value = raw_input("Press Enter to Pause")
    return value


if __name__ == "__main__":
    import os
    import time
    import sys; sys.path.append('../GPIB')
    import get
    import datetime

    date = str(datetime.date.today()).split('-')
    year = date[0]
    month = date[1]
    day = date[2]

    if len(sys.argv) > 1:
        comment = sys.argv[1]
    else:
        comment = ''
    path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', year, month, day)
    if not os.path.exists(path):
        os.makedirs(path)
    data = cap.data_file(path, 'TestDCBIAS_%s' % (str(time.time()).replace('.', '_')), comment)
    #freqs_to_sweep = [100, 400, 1000, 1400, 10000, 14000]
    freqs_to_sweep = [10000, 1000, 100]
    data.write_row2('# DC bias set to LOW')
    data.bridge.dcbias('HI')
    start_time = time.time()
    while (time.time()-start_time)/60 < 20:
        data.sweep_freq(freqs_to_sweep, 1)
    data.write_row2('# DC bias set to LOW')
    data.bridge.dcbias('LO')
    while (time.time()-start_time)/60 < 40:
        data.sweep_freq(freqs_to_sweep, 1)
    data.write_row2('# DC bias turned off')
    data.bridge.dcbias('OFF')
    while (time.time()-start_time)/60 < 60:
        data.sweep_freq(freqs_to_sweep, 1)
