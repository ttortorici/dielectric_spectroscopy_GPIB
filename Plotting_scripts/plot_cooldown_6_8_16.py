import slowplot
import os


if __name__ == "__main__":
    import sys; sys.path.append('..')
    import GPIB.get as get

    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    filenames = [['Bake_then_Cool_1465409960_31.csv',
                  'Cooling_1465419189_83.csv',
                  'Cooling_1465423486_76.csv',
                  'Cooling_1465424730_36.csv',
                  'Cooling_1465426315_04.csv',
                  'Cooling_1465426445_64.csv',
                  'Cooling_1465426500_31.csv',
                  'Cooling_1465427051_3.csv']]
    plotters = []
    for filename in filenames:
        plotters.append(slowplot.Plotter(filepath, filename))
    for plotter in plotters:
        plotter.plot_loss_v_temp()
        plotter.plot_loss_v_time()
        plotter.plot_temp_v_time()
        plotter.plot_cap_v_temp()
        plotter.plot_cap_v_time()
        plotter.show()
