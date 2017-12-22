from subprocess import call
import glob


def assignCRS(file_in, CRS_string):
    call(["gdalinfo", str(file_in)])
    call(["gdalwarp", "-t_srs", str(CRS_string), str(file_in), str(file_in)])


def auto_assignCRS(CRS_string, ext="./*.tif"):
    # Assigns the mentioned CRS to all files with extension .tif
    for filename in glob.glob(ext):
        print("Processing for " + str(filename))
        assignCRS(filename, CRS_string)


def auto_slopeDEM(ext="./", fname="*dem.tif"):
    for filename in glob.glob(ext + fname):
        call(["gdaldem", "slope", str(filename),
              str(filename.replace("dem", "slope"))])

def slopeDEM(file_in, file_out):
    call(["gdaldem","slope",file_in,file_out])

