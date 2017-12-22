library(data.table)
library(ggplot2)
library(raster)
library(sp)
library(rgdal)

df <- fread('/home/abhishek/programs/channasandra/volumetric calculation/Channasandra Excavation_Truck Load.csv')
setnames(df, c('date', 'trucks'))
head(df)
df$date <- as.POSIXct(df$date)
qplot(df$date, df$trucks) + geom_line()

hist(df$trucks)

# let's load the DEM deltas

demfolder <- '/home/abhishek/Downloads/channasandra-dems/channasandra_volume/'

may15dem <- raster('/home/abhishek/Downloads/channasandra-dems/channasandra_volume/09may2017_T_15may2017_T_delta_M.tif')
head(may15dem)

hist(may15dem, main="Distribution of elevation delat values", 
     col= "purple", 
     maxpixels=22000000)

plot(may15dem)
cropbox1 <- drawExtent()
may15dem_crop <- crop(may15dem, cropbox1)
plot(may15dem_crop)

hist(may15dem_crop, breaks=1000, main="Distribution of elevation delta values", 
     col= "purple", 
     maxpixels=22000000)


xmax = may15dem@extent@xmax * 100000
xmin = may15dem@extent@xmin * 100000
xinc = (xmax - xmin)/10

ymax = may15dem@extent@ymax * 100000
ymin = may15dem@extent@ymin * 100000
yinc = (ymax - ymin)/10

xbars = seq(xmin, xmax, xinc)/100000
ybars = seq(ymin, ymax, yinc)/100000

extents = c()
mc = c()
for(i in seq(1: 9)) {
  ex <- extent(xbars[i], xbars[i+1], ybars[i], ybars[i+1])
  extents <- c(extents, ex)
  cr <- crop(may15dem, ex)
  mc <- c(mc, cr)
}

