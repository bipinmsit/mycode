import cv2
import numpy as np
import gdal
import gdal
import os.path
import matplotlib.pyplot as plt


def create_and_show_histogram(tif_file, hist_nbins=255):
    tif = gdal.Open(tif_file)
    min, max, mean, sd = tif.GetRasterBand(1).GetStatistics(True, True)
    binwidth = (max - min) / hist_nbins
    y_hist = tif.GetRasterBand(1).GetHistogram(buckets=hist_nbins, min=min, max=max)
    dy_hist = np.gradient(y_hist)
    x_hist = np.linspace(min, max, hist_nbins)
    asign = np.sign(dy_hist)
    signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
    print(signchange)

    print(y_hist)
    print(x_hist)
    f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    ax1.plot(x_hist, dy_hist)
    ax2.plot(x_hist, signchange)
    ax3.plot(x_hist, y_hist)
    plt.show()
    pass


if __name__ == "__main__":
    folder = '/home/abhishek/programs/channasandra'
    test_tif = os.path.join(folder, '16June-DEM.tif')

    create_and_show_histogram(test_tif)
