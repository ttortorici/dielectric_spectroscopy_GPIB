import slowplot
import os


if __name__ == "__main__":
    import sys; sys.path.append('..')
    import GPIB.get as get

    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    filenames = [['Hystersis_Check_1465318552_61.csv']]
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
