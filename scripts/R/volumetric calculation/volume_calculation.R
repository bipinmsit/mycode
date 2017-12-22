library(data.table)
library(ggplot2)
library(raster)
library(sp)
library(rgdal)

DEM_FOLDER <- '/home/abhishek/Downloads/channasandra-dems/channasandra_volume/'

#channasandra_crop <- drawExtent()
channasandra_crop <- c(77.80555, 77.80677, 12.99272, 12.99395)

loadDEM <- function(demfilename, cropbox) {
  demfilepath <- paste(DEM_FOLDER, demfilename, sep="")
  dem <- raster(demfilepath)
  cdem <- crop(dem, channasandra_crop)
}

# see https://gis.stackexchange.com/questions/154276/how-to-reproject-a-raster-from-lat-lon-to-utm-in-r
convertProjection <- function(dem_raster) {
  # Define the Proj.4 spatial reference 
  # http://spatialreference.org/ref/epsg/26915/proj4/
  # Bangalore is http://spatialreference.org/ref/epsg/32643/proj4/
  sr <- "+proj=utm +zone=43 +ellps=WGS84 +datum=WGS84 +units=m +no_defs" 
  
  # Project Raster
  projected_dem_raster <- projectRaster(dem_raster, crs = sr)

  return(projected_dem_raster)
}

may9th <- '09may2017-DEM.tif'
dem_may9th <- loadDEM(may9th, channasandra_crop)
plot(dem_may9th)
hist(dem_may9th, breaks=100)

may15th <- '15may2017-DEM.tif'
dem_may15th <- loadDEM(may15th, channasandra_crop)
plot(dem_may15th)
hist(dem_may15th, breaks=100)

may15threv <- '15may2017-revised-DEM-.tif'
dem_may15threv <- loadDEM(may15threv, channasandra_crop)
plot(dem_may15threv)
hist(dem_may15threv, breaks=100)

hist(dem_may9th, col=rgb(1, 0, 0, 0.5), breaks=100, main="")
hist(dem_may15th, col=rgb(0, 1, 0, 0.5), breaks=100, add=T, main="")
box()
title('9th May(red) vs 15th May(green)')

hist(dem_may9th, col=rgb(1, 0, 0, 0.5), breaks=100, main="")
hist(dem_may15threv, col=rgb(0, 0, 1, 0.5), breaks=100, add=T, main="")
box()
title('9th May(red) vs 15th May revised(blue) ')

hist(dem_may15th, col=rgb(0, 1, 0, 0.5), breaks=100, main="")
hist(dem_may15threv, col=rgb(0, 0, 1, 0.5), breaks=100, add=T, main="")
box()
title('15th May(green) vs 15th May revised(blue) ')

dist_dem_may9th <- convertProjection(dem_may15th)

plot(dist_dem_may9th)

writeRaster(dist_dem_may9th, 'dist_dem_may9th.tif')

area1 <- readOGR('/home/abhishek/Downloads/channasandra-dems/channasandra_volume/', 'changed-aread-9thmayto15thmay')
