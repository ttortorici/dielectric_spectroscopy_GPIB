import slowplot
import os


if __name__ == "__main__":
    import sys; sys.path.append('..')
    import GPIB.get as get

    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    #filenames = [['Bake_1465495585_84.csv',
    #              'Bake_then_Cool_1465495585_84.csv']]
    filenames = [['Bake_then_Cool_1465581362_09.csv',
                  'Bake_then_Cool_1465586145_01.csv']]
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
