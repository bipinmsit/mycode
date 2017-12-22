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
    newS = hsv[:, :, 1]
    if combineMode == 'multiply':
        newV = cv2.addWeighted(
            hsv[:, :, 2], combineCoeff,
            cv2.multiply(hsv[:, :, 2], hill, scale=1. / 255), 1 - combineCoeff, 0)
    elif combineMode == 'saturate':
        newS = cv2.multiply(hsv[:, :, 1], hill, scale=1. / 255)
    elif combineMode == 'alpha':
        newV = cv2.addWeighted(
            hsv[:, :, 2], combineCoeff, hill, 1 - combineCoeff, 0)
        newS = cv2.addWeighted(
            hsv[:, :, 1], combineCoeff, 0, 1 - combineCoeff, 0)
    return cv2.cvtColor(cv2.merge((hsv[:, :, 0], newS, newV)), cv2.COLOR_HSV2RGB)


def iterateOverBands(func, outDS, *bands,
                     chunkX=8192, chunkY=8192,
                     offsetX=0, offsetY=0,
                     sizeX=None, sizeY=None,
                     **kwargs):
    if sizeX == None:
        sizeX = bands[0].XSize
    if sizeY == None:
        sizeY = bands[0].YSize
    outputBands = [outDS.GetRasterBand(i)
                   for i in range(1, outDS.RasterCount + 1)]
    origOffsetY = offsetY
    while offsetX < sizeX:
        remX = min(sizeX - offsetX, chunkX)
        while offsetY < sizeY:
            remY = min(sizeY - offsetY, chunkY)
            chunks = [b.ReadAsArray(offsetX, offsetY, remX, remY)
                      for b in bands]
            out = func(*chunks)
            for i in range(out.shape[2]):
                outputBands[i].WriteArray(out[:, :, i], offsetX, offsetY)
            print(offsetX, offsetY)
            offsetY += chunkY
        offsetY = origOffsetY
        offsetX += chunkX


def mergeColorReliefAndHillShade(pathToCR, pathToHS, pathToMerged, combCoeff=None, combMode=None):
    '''
    Creates a merged colorized, hillshaded version of the same DEM from two files:
    1. A colorized DEM tiff
    2. A hillshaded DEM tiff
    '''
    colorizedDEM = gdal.Open(pathToCR)
    hillshadedDEM = gdal.Open(pathToHS)

    if combCoeff != None:
        combineCoeff = combCoeff
    if combMode != None:
        combineMode = combMode
    
    (redBand, greenBand, blueBand) = (colorizedDEM.GetRasterBand(i)
                                      for i in range(1, 4))
    hillBand = hillshadedDEM.GetRasterBand(1)

    destDS = createImageOutput(pathToMerged, redBand.XSize, redBand.YSize)
    destDS.SetGeoTransform(colorizedDEM.GetGeoTransform())
    destDS.SetProjection(colorizedDEM.GetProjectionRef())

    iterateOverBands(combineHillshadedColorized, destDS,
                     redBand, greenBand, blueBand, hillBand)
    destDS = None


if __name__ == "__main__":
    colorizedDEMFile = sys.argv[1]
    hillshadedDEMFile = sys.argv[2]
    outputFile = sys.argv[3]
    if (len(sys.argv) > 4):
        combineMode = sys.argv[4]
    if (len(sys.argv) > 5):
        combineCoeff = float(sys.argv[5])

    mergeColorReliefAndHillShade(colorizedDEMFile, hillshadedDEMFile, outputFile, combineCoeff, combineMode)

# colorizedDEM = gdal.Open(colorizedDEMFile)
# hillshadedDEM = gdal.Open(hillshadedDEMFile)

# (redBand, greenBand, blueBand) = (colorizedDEM.GetRasterBand(i)
#                                   for i in range(1, 4))
# hillBand = hillshadedDEM.GetRasterBand(1)


# destDS = createImageOutput(outputFile, redBand.XSize, redBand.YSize)
# destDS.SetGeoTransform(colorizedDEM.GetGeoTransform())
# destDS.SetProjection(colorizedDEM.GetProjectionRef())

# iterateOverBands(combineHillshadedColorized, destDS,
#                  redBand, greenBand, blueBand, hillBand)

# destDS = None
