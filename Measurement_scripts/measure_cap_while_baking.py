import capacitance_measurement_tools as cap

if __name__ == "__main__":
    import sys; sys.path.append('..')
    import os
    import GPIB.get as get
    import time

    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = ''
    if len(sys.argv) > 2:
        comment = sys.argv[2]
    else:
        comment = ''
    data = cap.data_file(os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy'),
                     '%s_%s' % (name, str(time.time()).replace('.', '_')), comment)
    freqs_to_sweep = [100, 500, 1000, 5000, 10000]
    data.bake(400, step_size=20, freqs=freqs_to_sweep, measure_per_freq=3, hold_time=5)