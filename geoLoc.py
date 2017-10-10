import pandas, os
os.listdir()
df1=pandas.read_csv("doc.csv")
df1
import geopy
dir(geopy)
from geopy.geocoders import Nominatim
nom = Nominatim()
n=nom.geocode("London eye")
n
print(n.longitude, n.latitude)
%history -f geoGeoLoc.py
type(n)
#add a new address column

df1["Address"]=df1["Address"]+", "+df1["City"]+", "+df1["Country"]
df1
# send this string to Geocode method
df1["Coordinates"]=df1["Address"].apply(nom.geocode)
df1
#set values to latitude and longitude
df1["Latitude"]=df1["Coordinates"].apply(lambda x: x.latitude if x!=None else None)
df1["Longitude"]=df1["Coordinates"].apply(lambda x: x.longitude if x!=None else None)

%history -f geoLoc.py
