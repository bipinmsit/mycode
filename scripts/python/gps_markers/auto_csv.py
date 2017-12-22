import marker
from PIL import Image
import glob
import csv

f = open('gps.csv','wb')
w = csv.writer(f)
w.writerow(['Latitude','Longitude'])
for filename in glob.glob("./*.JPG"):
    im=Image.open(filename)
    ex_data = marker.get_exif_data(im)
    _lat,_long = marker.get_lat_lon(ex_data)
    r = [str(_lat),str(_long)]
    w.writerow(r)
f.close()