import marker
from PIL import Image
import glob
import csv
import os
import os.path
import ntpath

if __name__ == '__main__':
    f = open('image_altitude.csv','w')
    w = csv.writer(f)
    w.writerow(['File', 'Altitude'])
    for filename in glob.glob("./*.JPG"):
        im=Image.open(filename)
        ex_data = marker.get_exif_data(im)
        altitude = marker.get_altitude(ex_data)
        r = [ntpath.basename(filename), str(altitude)]
        w.writerow(r)
    f.close()