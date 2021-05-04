import slowplot
import os


if __name__ == "__main__":
    import sys; sys.path.append('..')
    import GPIB.get as get

    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    filenames = [['Hystersis_Check_1465241637_08.csv',
                  # 'Cooling_1465249385_35.csv',
                  # 'Cooling_1465249536_82.csv',
                  # 'Cooling_1465249891_34.csv',
                  'Cooling_1465249997_01.csv',
                  # 'Cooling_1465253401_92.csv',
                  'Cooling_1465253519_52.csv',
                  'Cooling_1465254760_47.csv']]
    plotters = []
    for filename in filenames:
        plotters.append(slowplot.Plotter(filepath, filename))
    for plotter in plotters:
        plotter.plot_loss_v_temp()
        plotter.plot_loss_v_time()
        plotter.plot_temp_v_time()
        plotter.show()
