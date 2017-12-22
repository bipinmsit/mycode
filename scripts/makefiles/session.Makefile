PROCESSES := $(SITE_PROCESSES)
DEM_COLORS_FILE := $(SITE_DEM_COLORS_FILE)


-include session-settings.Makefile

%.tif: %-initial.tif
	gdalwarp -t_srs $(SITE_SRS) $< $@

all: $(PROCESSES)	

dem-colorized.tif: dem.tif $(DEM_COLORS_FILE)
	gdaldem color-relief $^ $@ 

dem-hillshaded.tif: dem.tif
	gdaldem hillshade $< $@ $(DEM_HILLSHADE_OPTIONS)

dem-colorshaded.tif: dem-colorized.tif dem-hillshaded.tif 
	$(VM_SCRIPTS)/processes/combine-hillshaded-colorized.py $^ $@

dem-overview.tif: dem-colorshaded.tif
	gdal_translate -outsize 8000 0 $^ $@