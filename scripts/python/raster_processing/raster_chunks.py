"""
Module to read and write rasters in chunks, and to simplify interface by
abstracting away gdal components.
"""

import gdal
import numpy as np

DEFAULT_CHUNK_SIZE = 128

class Chunk:
    """
    Class that defines the chunking methodology used.
    It is a placeholder class, that simply defines the attributes of a chunk.
    Attributes:
        x_offset: X Pixel Coordinate of the Raster, that corresponds to [0, 0] element of the
                  array
        y_offset: Y Pixek Coordinate of the Raster, that corresponds to [0, 0] element of the
                  array
        x_chunk_size: Chunk Size along the X coordinate
        y_chunk_size: Chunk Size along the Y coordinate
        padding_x: Padding Size along the X coordinate sour
        padding_y: -> Padding Size along the Y coordinate
        
    """
    def __init__(self, x_off=0, y_off=0, x_cs=0, y_cs=0, pad_x=0, pad_y=0):
        self.x_offset = int(x_off)
        self.y_offset = int(y_off)
        self.x_chunk_size = int(x_cs)
        self.y_chunk_size = int(y_cs)
        self.padding_x = int(pad_x)
        self.padding_y = int(pad_y)


    def __str__(self):
        return "X_offset=%i\nY_offset=%i\nX_ChunkSize=%i\nY_ChunkSize=%i\nPadding_X=%i\n" \
               "Padding_Y=%i" % (self.x_offset, self.y_offset,\
                                                       self.x_chunk_size, self.y_chunk_size,\
                                                       self.padding_x, self.padding_x,)


class GeoChunks:
    """
    Class that abstracts the interface to GeoTiff files

    Important - The constructor has a boolean variable 'update' that is used to decide
                whether the raster is to opened in read-only mode (default, update=False)
                or in read-write mode (update=True)
    Attributes:
        data_gtif: Variable to store reference to Raster as gdal.Dataset
        data_bands: Array to store reference to the bands of the Raster
                    as an array of gdal.Band objects
        geo_trans: Store the GeoTrasnform info of the Raster as flaot array
                   Geotransform is formatted as
                   [UpperLeft_X, PixelSize_X, Skew_X,UpperLeft_Y,
                   Skew_Y, PixelSize_Y]
        n_bands: Stores the number of Raster Bands present in the Raster, as int
        proj: Stores the Co-ordinate Reference System (CRS) or the "Projection"
              of the Raster, as a string array in WkT format
        geo_extent_x: Array that stores [min_X,max_X] using the CRS of the Raster
        geo_extent_y: Array that stores [min_Y,max_Y] using the CRS  of the Raster
        no_data_value: Stores the NoDataValue of the Raster
                     NOTE - no_data_value can sometimes take value as float('nan')
                     This is something that must be dealt with independently.
    
    """

    data_gtif = None
    data_bands = []
    geo_trans = None
    n_bands = None
    proj = None
    geo_extent_x = None
    geo_extent_y = None
    no_data_value = None

    def __init__(self, filename="", update=False):
        """
        Function to initilize an instance of the class.
        Args:
            self: Reference to object of GeoChunks which calls the function
            filename: Filepath to the GeoTiff to be opened
            update: Flag boolean that controls whether file is to be opened in 
                    read-only mode, or update mode. Update mode is *unsafe*, and must
                    be used carefully to avoid accidental modificationo of original data
        """

        if filename == "":
            self.data_gtif = None
            self.data_bands = []
            self.geo_trans = None
            self.n_bands = None
            self.proj = None
        else:
            self.open(filename, update)

    def open(self, filename, update=False):
        """
        Function to Open GeoTiff Image using GDAL and save attributes in class GeoChunks
        Args:
            self: Reference to object of GeoChunks which calls the function
            filename: Filepath to the GeoTiff to be opened
            update: Flag boolean that controls whether file is to be opened in 
                    read-only mode, or update mode. Update mode is *unsafe*, and must
                    be used carefully to avoid accidental modificationo of original data

        """

        if update is True:
            self.data_gtif = gdal.Open(filename, gdal.GA_Update)
        else:
            self.data_gtif = gdal.Open(filename)
        self.geo_trans = self.data_gtif.GetGeoTransform()
        # Getting and assigning GeoTransform and the extent of the raster in Geographic
        # Coorindindates defined the the projection system
        self.geo_extent_x = [self.geo_trans[0],
                             self.geo_trans[0] + self.data_gtif.RasterXSize * self.geo_trans[1]]
        self.geo_extent_y = [self.geo_trans[3],
                             self.geo_trans[3] + self.data_gtif.RasterYSize * self.geo_trans[5]]
        self.geo_extent_x = sorted(self.geo_extent_x)
        self.geo_extent_y = sorted(self.geo_extent_y)

        self.proj = self.data_gtif.GetProjectionRef()
        self.n_bands = self.data_gtif.RasterCount
        self.data_bands = []
        for band in range(self.n_bands):
            self.data_bands += [self.data_gtif.GetRasterBand(band + 1)]
        self.no_data_value = self.data_bands[0].GetNoDataValue()
        if self.no_data_value is None:
            pass
        else:
            if np.isnan(self.no_data_value):
                print("Warning: No data value is NaN.\n\tCould cause error in "
                      "later functionality..\n\tTry Fixing with"
                      "'gdalwarp -dstnodata 0 <in_file> <out_file>' to set NDV to 0.")

    def create_from(other, filename):
        """
        Function to create a GeoTiff file at specified location with the same properties as
        another object of the GeoChunks class.
        Note that the GeoTiff created through this method, will be opened in update mode,
        and thus, can be modified. 
        Args:
            other: Object of GeoChunks based on which to create new GeoTiff
            filename: Filepath of new GeoTiff file to be created
        Returns:
            new_data: Instance of GeoChunks containing reference to the newly created
                      GeoTiff file
        """
        driver = gdal.GetDriverByName("GTiff")
        new_data = GeoChunks()
        # Creating New file with specified filename, and same parameters as existing filename
        new_data.data_gtif = driver.Create(filename, other.data_bands[0].XSize,
                                           other.data_bands[0].YSize,
                                           other.n_bands, other.data_bands[0].DataType)

        # Copying band Number Data
        new_data.n_bands = other.n_bands
        # Copying Projection Reference Data
        new_data.proj = other.proj
        new_data.data_gtif.SetProjection(new_data.proj)
        # Copying Geo Transform Data
        new_data.geo_trans = other.geo_trans
        new_data.geo_extent_x = other.geo_extent_x
        new_data.geo_extent_y = other.geo_extent_y
        new_data.data_gtif.SetGeoTransform(new_data.geo_trans)
        # Storing corresponding band data in data_bands variable
        for band in range(new_data.n_bands):
            new_data.data_bands += [new_data.data_gtif.GetRasterBand(band + 1)]
            new_data.data_bands[band].SetNoDataValue(other.no_data_value)
        # Returning output
        new_data.no_data_value = other.no_data_value
        return new_data


class ChunkUtils:
    """
    Class for operations on rasters with and without chunks
    Attributes:
        chunk_2d: Array to store the definition of how the Raster should be chunked,
               with 2D referencing.
        raster: Object of Class GeoChunks that stores reference to the GeoTiff file that
              will be operated on, whether it is read or write operation

    """
    def __init__(self, raster=None):
        if raster is None:
            self.raster = GeoChunks()
        else:
            self.raster = raster

        self.chunk_2d = []

    def break_chunks(self, b_idx=0, chunk_x=DEFAULT_CHUNK_SIZE, chunk_y=DEFAULT_CHUNK_SIZE,
                     padding_x=0, padding_y=0):
        """
        Function to split image into different chunks and
        specify offset, size, and padding of chunks
        b_idx -> Index of band to be read from raster
        chunk_x -> Chunk Size along X direction, to be used while chunking
        chunk_y -> Chunk Size along Y direction, to be used while chunking
        padding_x -> Padding to be used along X direction, when reading the Chunk
        padding_y -> Padding to be used along Y direction, when reading the Chunk
        """
        dband = self.raster.data_bands[b_idx]


        # Add assertation that padding is less than chunk size for both X and Y directions
        if padding_x > chunk_x or padding_y > chunk_y:
            raise ValueError("Padding Values should be less than corresponding Chunk Size")
        # Adding One to account for last column  and last row
        x_blocks = dband.XSize // chunk_x + 1
        y_blocks = dband.YSize // chunk_y + 1

        # Finding Pixels in last row and last column
        x_rem = dband.XSize % chunk_x
        y_rem = dband.YSize % chunk_y
        # Removing Extra Column or Row Added when Size is a multiple of the Blocksize
        if x_rem == 0:
            x_blocks -= 1
        if y_rem == 0:
            y_blocks -= 1

        chunk = []
        for y_it in range(y_blocks):
            row_chunk = []
            y_off = y_it *chunk_y
            y_cs = chunk_y
            if y_it == y_blocks - 1 and y_rem > 0:
                y_cs = y_rem
            for x_it in range(x_blocks):
                x_off = x_it * chunk_x
                x_cs = chunk_x
                if x_it == x_blocks - 1 and x_rem > 0:
                    x_cs = x_rem
                chunk_temp = Chunk(x_off, y_off, x_cs, y_cs, padding_x, padding_y)
                row_chunk.append(chunk_temp)


            chunk.append(row_chunk)
        self.chunk_2d = np.array(chunk)

        # Return 1D chunk referencing Array

        return self.chunk_2d.reshape([self.chunk_2d.shape[0] * self.chunk_2d.shape[1]])

    def read_raster(self, b_idx=0, chunk=None, filt_flag=False):
        """
        Function to read a raster as a numpy array, according to a chunk if specified.
        self -> Object of  Class Chunkutils that calls the function
        b_idx -> Index of raster band to be read. This is 0-indexed.
        chunk -> Chunk of the raster to be read. It will specify where and how much
                 of the raster will be written to.
                 This is an object of Class Chunk
        filt_flag -> Decides if invalid pixels read as part of reading the chunk is set to
                     0 (True) or self.no_data_value (False)
        Returns ->
                 numpy.ndarray containing pixel values from the raster
        """
        if chunk is None:
            return self.raster.data_bands[b_idx].ReadAsArray()
        else:
            # Deciding whether invalid pixels read are 0 or self.no_data_value according to
            # filt_flag
            if filt_flag:
                temp_arr = np.zeros([chunk.y_chunk_size + 2 * chunk.padding_y,
                                     chunk.x_chunk_size + 2 * chunk.padding_x])
            else:
                temp_arr = np.ones([chunk.y_chunk_size + 2 * chunk.padding_y,
                                    chunk.x_chunk_size + 2 * chunk.padding_x])\
                           * self.raster.no_data_value

            # Final Output
            temp_arr = self.raster.data_bands[b_idx].ReadAsArray(chunk.x_offset, chunk.y_offset,\
                                                         chunk.x_chunk_size, chunk.y_chunk_size)
            return temp_arr

    def write_raster(self, arr, b_idx=0, chunk=None):
        """
        Function to write a numpy array to aa raster, according to a chunk if specified.
        if chunk is not specified, it will write from top-left corner to the max extent
        that the size of the numpy array covers.
        self -> Object of  Class ChunkUtils that calls the function
        b_idx -> Index of raster band to be written. This is 0-indexed.
        chunk -> Chunk of the raster to be written. It will specify where and how much
                 of the raster will be written to.
                 This is an object of Class Chunk
        Returns ->
                 0 -> If Operation is completed successfully
        """
        if chunk is None:
            self.raster.data_bands[b_idx] = None
            self.raster.data_gtif.GetRasterBand(b_idx + 1).WriteArray(arr)
            self.raster.data_gtif.FlushCache()
            self.raster.data_bands[b_idx] = self.raster.data_gtif.GetRasterBand(b_idx + 1)
            return 0
        else:
            if not isinstance(chunk, Chunk):
                raise ValueError("chunk passed is not a member of class Chunks")
            # Final Output
            if arr.shape[1] != chunk.x_chunk_size and arr.shape[0] != chunk.y_chunk_size:
                raise ValueError("Size of array does not match expected chunk size")
            self.raster.data_gtif.GetRasterBand(b_idx + 1)\
                .WriteArray(arr, chunk.x_offset, chunk.y_offset)
            self.raster.data_gtif.FlushCache()
            self.raster.data_bands[b_idx] = self.raster.data_gtif.GetRasterBand(b_idx + 1)
            return 0
