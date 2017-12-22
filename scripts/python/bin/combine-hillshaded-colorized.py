#!/usr/bin/env python

import sys
import gdal
import cv2
import numpy as np

# Create output file
def createImageOutput(filename, xSize, ySize):
  driver = gdal.GetDriverByName("GTiff")
  return driver.Create(filename, xSize, ySize, 3, gdal.GDT_Byte)

combineMode = 'alpha'
combineCoeff = 0.7

def combineHillshadedColorized(r, g, b, hill):  
  hsv = cv2.cvtColor(cv2.merge((r, g, b)), cv2.COLOR_RGB2HSV)
  newV = hill
  newS = hsv[:,:,1]  
  if combineMode == 'multiply':
    newV = cv2.addWeighted(
      hsv[:,:,2], combineCoeff, 
      cv2.multiply(hsv[:,:,2], hill, scale=1./255), 1 - combineCoeff, 0)
  elif combineMode == 'saturate':
    newS = cv2.multiply(hsv[:,:,1], hill, scale=1./255)
  elif combineMode == 'alpha':
    newV = cv2.addWeighted(hsv[:, :, 2], combineCoeff, hill, 1-combineCoeff, 0)
    newS = cv2.addWeighted(hsv[:, :, 1], combineCoeff, 0, 1-combineCoeff, 0)
  return cv2.cvtColor(cv2.merge((hsv[:,:,0], newS, newV)), cv2.COLOR_HSV2RGB)
  


def iterateOverBands(func, outDS, *bands,
    chunkX=8192, chunkY=8192, 
    offsetX=0, offsetY=0,
    sizeX=None, sizeY=None,
    **kwargs):
  if sizeX == None:
    sizeX = bands[0].XSize
  if sizeY == None:
    sizeY = bands[0].YSize  
  outputBands = [outDS.GetRasterBand(i) for i in range(1, outDS.RasterCount+1)]
  origOffsetY = offsetY
  while offsetX < sizeX:
    remX = min(sizeX - offsetX, chunkX)
    while offsetY < sizeY:      
      remY = min(sizeY - offsetY, chunkY)      
      chunks = [b.ReadAsArray(offsetX, offsetY, remX, remY) for b in bands]
      out = func(*chunks)
      for i in range(out.shape[2]):
        outputBands[i].WriteArray(out[:,:,i], offsetX, offsetY)
      print(offsetX, offsetY)
      offsetY += chunkY
    offsetY = origOffsetY
    offsetX += chunkX

def help():
    print("Usage:- combine-hillshaded-colorized.py <options> <Colorized-DEM> <Hillshaded-DEM> <output-DEM>\n"\
          "   <options> can include ->\n"\
          "   -h,--help                                       -> print this help message\n"\
		      "   -cm,--combine_mode <Combine-Mode>               -> Sets combine mode. Default uses alpha-blending\n"\
          "                                                      Combine mode - 'alpha'\n"\
          "                                                                     'multiply'\n"\
          "                                                                     'saturate'\n"\
          "   -cc,--combine_coefficient <Combine-Coefficient> -> Sets Combine Coefficient Value.\n"\
          "                                                      Default value is 0.7\n" )

def main(argv=None):
  argv=sys.argv
    #Add functionality to sanity check commands passed through this
  options = argv[1:-3]
  data = argv[-3:]
  if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
    help()
    return -1

  if len(argv) < 4:
        #When there are not enough arguments to use the command
    print("Use '-h' to view help",file=sys.stdout)
    print("ERROR 1. Not enough arguments",file=sys.stderr)
    return 1

  colorizedDEMFile = data[0]
  hillshadedDEMFile = data[1]
  outputFile = data[2]
  
  	#For '-cm,--combine-mode'
  if options.count('-cm') > 0:  
    cm_idx = options.index('-cm')
    if len(options[cm_idx:]) < 2:
      print('Error. Specify Combine Mode\nCheck help with "-h"',file=sys.stdout)
      print('Error. Combine Mode not specified. ',file=sys.stderr)
      sys.exit(1)
    else:
      combineMode = options[cm_idx + 1]
  elif options.count('--combine_mode') > 0:
    cm_idx = options.index('--combine_mode')
    if len(options[cm_idx:]) < 2:
      print('Error. Specify Combine Mode\nCheck help with "-h"',file=sys.stdout)
      print('Error. Combine Mode not specified.',file=sys.stderr)
      sys.exit(1)
    else:
      combineMode = options[cm_idx + 1]
      
  	#For '-cc,--combine_coefficient'
  if options.count('-cc') > 0:  
    cc_idx = options.index('-cc')
    if len(options[cc_idx:]) < 2:
      print('Error. Specify Combine Coefficient\nCheck help with "-h"',file=sys.stdout)
      print('Error. Combine Coefficient not specified. ',file=sys.stderr)
      sys.exit(1)
    else:
      combineCoeff = float(options[cc_idx + 1])
  elif options.count('--combine_coefficient') > 0:
    cc_idx = options.index('--combine_coefficient')
    if len(options[cc_idx:]) < 2:
      print('Error. Specify Combine Coefficient\nCheck help with "-h"',file=sys.stdout)
      print('Error. Combine Coefficient not specified.',file=sys.stderr)
      sys.exit(1)
    else:
      combineCoeff = float(options[cc_idx + 1])
  """
      #Old below this <-- !! -->
  if (len(sys.argv) > 4):
    combineMode = argv[4]
  if (len(sys.argv) > 5):
    combineCoeff = float(argv[5])
  """

  try:
    colorizedDEM = gdal.Open(colorizedDEMFile)
    hillshadedDEM = gdal.Open(hillshadedDEMFile)
    (redBand, greenBand, blueBand) = (colorizedDEM.GetRasterBand(i) for i in range(1,4))
    hillBand = hillshadedDEM.GetRasterBand(1)
    
  except Exception as err:
    print(err,file=sys.stderr)
    sys.exit(1)
  
  try:
    if hillBand.XSize != redBand.XSize or hillBand.YSize != redBand.YSize:
      raise ValueError("ERROR 1. Inputs do not have the same resolution")
    if hillshadedDEM.RasterCount > 1:
      raise ValueError("ERROR 1. Input Hillshaded DEM has multiple bands.")
  except Exception as err:
    print(err,file=sys.stderr)
    sys.exit(1)
  
  destDS = createImageOutput(outputFile, redBand.XSize, redBand.YSize)
  destDS.SetGeoTransform(colorizedDEM.GetGeoTransform())
  destDS.SetProjection(colorizedDEM.GetProjectionRef())

  iterateOverBands(combineHillshadedColorized, destDS,
    redBand, greenBand, blueBand, hillBand)

  destDS = None
 
if __name__ == "__main__":
  sys.exit(main())