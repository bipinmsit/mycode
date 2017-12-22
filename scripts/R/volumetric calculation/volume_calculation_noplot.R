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

calcVolume <- function(dist_dem, baseline) {
  area_dist_dem <- xres(dist_dem) * yres(dist_dem)
  
  df <- as.data.frame(dist_dem)
  df <- as.data.table(df)
  df <- df[complete.cases(df), ]
  setnames(df, c('z'))
  head(df)
  
  df$elev <- df$z - baseline
  df$vol <- df$elev * area_dist_dem
  
  head(df)
  volume <- sum(df$vol)
  print(volume)
  return(volume)
}

cropToShape <- function(dist_dem, shpaoi) {
  dist_shpaoi <- spTransform(shpaoi, crs(dist_dem))
  #plot(dist_shpaoi)
  c_dist_dem <- mask(dist_dem, dist_shpaoi)
  #plot(c_dist_dem)
  return(c_dist_dem)
}

may9th <- '09may2017-DEM.tif'
dem_may9th <- loadDEM(may9th, channasandra_crop)

may15th <- '15may2017-DEM.tif'
dem_may15th <- loadDEM(may15th, channasandra_crop)

may15threv <- '15may2017-revised-DEM-.tif'
dem_may15threv <- loadDEM(may15threv, channasandra_crop)

dist_dem_may9th <- convertProjection(dem_may9th)
#writeRaster(dist_dem_may9th, 'dist_dem_may9th.tif')
vol9th <- calcVolume(dist_dem_may9th, 800)

dist_dem_may15th <- convertProjection(dem_may15th)
vol15th <- calcVolume(dist_dem_may15th, 800)

dist_dem_may15threv <- convertProjection(dem_may15threv)
vol15threv <- calcVolume(dist_dem_may15threv, 800)

shpaoi <- readOGR('/home/abhishek/Downloads/channasandra-dems/channasandra_volume/', 'Excavation aoi')
excav_dist_dem_may9th <- cropToShape(dist_dem_may9th, shpaoi)

excav_dist_dem_may9th <- cropToShape(dist_dem_may9th, shpaoi)
excav_dist_dem_may15threv <- cropToShape(dist_dem_may15threv, shpaoi)
volexcav9th <- calcVolume(excav_dist_dem_may9th, 800)
volexcav15threv <- calcVolume(excav_dist_dem_may15threv, 800)

vol9thto15thdelta <- volexcav9th - volexcav15threv
# area_dem_may9th <- xres(dist_dem_may9th) * yres(dist_dem_may9th)
# 
# df <- as.data.frame(dist_dem_may9th)
# df <- as.data.table(df)
# df <- df[complete.cases(df), ]
# head(df)
# 
# baseline <- 850
# df$elev <- df$X09may2017.DEM - baseline
# df$vol <- df$elev * area_dem_may9th
# 
# head(df)
# print(sum(df$vol))
# 
# dist_dem_may15threv <- convertProjection(dem_may15threv)
# #writeRaster(dist_dem_may9th, 'dist_dem_may9th.tif')
# 
# area_dem_may15threv <- xres(dist_dem_may15threv) * yres(dist_dem_may15threv)
# 
# df2 <- as.data.frame(dist_dem_may15threv)
# df2 <- as.data.table(df2)
# df2 <- df2[complete.cases(df2), ]
# head(df2)
# 
# df2$elev <- df2$X15may2017.revised.DEM. - baseline
# df2$vol <- df2$elev * area_dem_may15threv
# 
# head(df2)
# print(sum(df2$vol))
