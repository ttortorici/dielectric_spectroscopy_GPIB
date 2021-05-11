import capacitance_measurement_tools as cap
from builtins import input

if __name__ == "__main__":
    import os
    import time
    import sys; sys.path.append('../GPIB')
    import get

    if len(sys.argv) > 1:
        comment = sys.argv[1]
    else:
        comment = ''
    path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    data = cap.data_file(path, 'Cooling_%s' % (str(time.time()).replace('.', '_')), comment)
    #freqs_to_sweep = [100, 400, 1000, 1400, 10000, 14000]
    freqs_to_sweep = [100, 1000, 10000]
    while True:
        for ii in range(10):
            data.sweep_freq(freqs_to_sweep, 1)
        data.speak('Adjust probes')
        print('Adjust Probes')
        input("Press Enter to continue...")
    # data.cont_meas(1000)
    # data.sweep_heat(low=320, high=400, step_size=5, freqs=freqs_to_sweep, measure_per_freq=3, hold_time=60)