library(data.table)
library(ggplot2)
library(raster)
library(sp)
library(rgdal)
library(zoo)

DEM_FOLDER <- '/home/abhishek/Downloads/channasandra-dems/channasandra_volume/'

#channasandra_crop <- drawExtent()
channasandra_crop <- c(77.80555, 77.80677, 12.99272, 12.99395)

loadDEM <- function(demfilename, cropbox) {
  demfilepath <- paste(DEM_FOLDER, demfilename, sep="")
  print(demfilepath)
  dem <- raster(demfilepath)
  cdem <- crop(dem, cropbox)
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
  sa_ext <- extent(dist_shpaoi)
  c_dist_dem <- crop(dist_dem, sa_ext)
  #plot(dist_shpaoi)
  c_dist_dem <- mask(c_dist_dem, dist_shpaoi)
  #plot(c_dist_dem)
  return(c_dist_dem)
}

computeVolumes <- function(date, demfile) {
  print(date)
  print(demfile)

  # vol_dt = 10
  # vol_excav_dt = 100
  
  dt <- demfile
  dem_dt <- loadDEM(dt, channasandra_crop)
  dist_dem_dt <- convertProjection(dem_dt)
  vol_dt <- calcVolume(dist_dem_dt, 800)
  excav_dist_dem_dt <- cropToShape(dist_dem_dt, shpaoi)
  vol_excav_dt <- calcVolume(excav_dist_dem_dt, 800)
  
  return (list("total" = vol_dt, "excavation" = vol_excav_dt))
}


shpaoi <- readOGR('/home/abhishek/Downloads/channasandra-dems/channasandra_volume/Excavation area bounday/', 'Excavation aoi')
input_dems <- fread('dem_input.csv')
#id <- head(input_dems, 1)
#dem_vols <- id[, .(vols = computeVolumes(date, demfile)), by=date]

dem_vols <- input_dems[, c("total_volume", "excavation_volume") := computeVolumes(date, demfile), by=date]


dem_vols <- input_dems

dem_vols$dt <- as.Date(as.POSIXct(dem_vols$date, format="%d/%m/%Y"))
dates_dt <- as.data.table(seq(min(dem_vols$dt), max(dem_vols$dt), by='1 day'))
setnames(dates_dt, c('dt'))

#dem_vols <- fread('dem_vols_14072017.csv')
dem_vols <- merge(dates_dt, dem_vols, all=TRUE)
#dem_vols$excavation_volume <- na.locf(dem_vols$excavation_volume)
#dem_vols$total_volume <- na.locf(dem_vols$total_volume)
dem_vols$excavation_volume <- na.approx(dem_vols$excavation_volume)
dem_vols$total_volume <- na.approx(dem_vols$total_volume)
dem_vols[,excavation_volume_diff := c(0, diff(excavation_volume))]
dem_vols[,excavation_volume_change := cumsum(excavation_volume_diff)]

ggplot(dem_vols, aes(x=dt, y=excavation_volume)) + geom_point() + geom_line()
head(dem_vols)

#trucks <- fread('/home/abhishek/programs/channasandra/volumetric calculation/Channasandra Excavation_Truck Load.csv')
trucks <- fread('/home/abhishek/programs/channasandra/volumetric calculation/trucks-17Jul2017.csv')
setnames(trucks, c('date', 'trucks'))
head(trucks)
trucks$dt <- as.Date(as.POSIXct(trucks$date, format="%d/%m/%Y"))
avg_trucks <- mean(trucks$trucks)
trucks <- merge(dates_dt, trucks, all=TRUE)
trucks[is.na(trucks), trucks:=0]
qplot(trucks$dt, trucks$trucks) + geom_line()

trucks$vol10 <- trucks$trucks * 10
trucks$vol11 <- trucks$trucks * 11
trucks$vol12 <- trucks$trucks * 12
trucks$vol15 <- trucks$trucks * 15

trucks$cs_trucks <- cumsum(trucks$trucks)
trucks$cs_vol10 <- cumsum(trucks$vol10)
trucks$cs_vol11 <- cumsum(trucks$vol11)
trucks$cs_vol12 <- cumsum(trucks$vol12)
trucks$cs_vol15 <- cumsum(trucks$vol15)

qplot(trucks$dt, trucks$cs_trucks) + geom_line()

dem_vols_and_trucks <- merge(dem_vols, trucks)
dem_vols_and_trucks$excavation_volume_change <- -(dem_vols_and_trucks$excavation_volume_change)

xdt <- dem_vols_and_trucks[,c('dt', 'excavation_volume_change', 'cs_vol10', 'cs_vol11', 'cs_vol12')]
setnames(xdt, c('Date', 'ExcavationVolumeChange', 'TrucksVolAt10cubicmetre', 'TrucksVolAt11cubicmetre', 'TrucksVolAt12cubicmetre'))

mdt <- melt(xdt, id.vars = "Date")

ggplot(mdt, aes(Date,value, col=variable)) + 
  geom_line()
#write.csv(dem_vols, 'dem_vols_17072017.csv')
write.csv(dem_vols, 'dem_vols_17072017.csv')
