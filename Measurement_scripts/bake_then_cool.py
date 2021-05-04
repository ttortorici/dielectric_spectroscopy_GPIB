import capacitance_measurement_tools as cap

if __name__ == "__main__":
    import sys; sys.path.append('..')
    import os
    import GPIB.get as get
    import time

    if len(sys.argv) > 1:
        comment = sys.argv[1]
    else:
        comment = ''

    low = 77
    high = 400

    data = cap.data_file(os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy'),
                     'Bake_then_Cool_%s' % (str(time.time()).replace('.', '_')), comment)
    freqs_to_sweep = [100, 1000, 10000]
    data.check_hysteresis2(low, high, freqs=freqs_to_sweep, measure_per_freq=3)
    data.ls.setpoint(400)
    while True:
        data.sweep_freq(freqs=freqs_to_sweep, measurements_at_each_freq=3)
