#!/usr/bin/env python
import subprocess
import ntpath
import os.path
import logging
import combine_hillshaded_colorized
import sys

"""
Create a merged colorized and hillshaded version of a given DEM given a colour-relief file.

Author: Abhishek Mishra
Date: 7th Oct 2017
"""

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def createColorizedDEM(demPath, colorDemPath, colorFilePath):
    subprocess.call(['gdaldem', 'color-relief', demPath, colorFilePath, colorDemPath])


def createHillshadedDEM(demPath, hsDemPath):
    subprocess.call(['gdaldem', 'hillshade', demPath, hsDemPath])


def createColorAndHSDems(demPath, colorFilePath):
    demDir = ntpath.dirname(demPath)
    demName = ntpath.basename(demPath)
    if demName.endswith('.tif'):
        demNameWithoutExt = demName.replace('.tif', '')
        logging.info('DEM Dir is ' + demDir + ', DEM File is ' + demName + ' DEM Name without extension is ' + demNameWithoutExt)

        colorDemPath = os.path.join(demDir, demNameWithoutExt + '-cr' + '.tif')
        hsDemPath = os.path.join(demDir, demNameWithoutExt + '-hs' + '.tif')
        createColorizedDEM(demPath, colorDemPath , colorFilePath)
        createHillshadedDEM(demPath, hsDemPath)

        outputPath = os.path.join(demDir, demNameWithoutExt + '-crhs' + '.tif')
        combine_hillshaded_colorized.mergeColorReliefAndHillShade(colorDemPath, hsDemPath, outputPath)

        logging.info('Output colorized and hillshaded DEM is at - ' + outputPath)
        logging.info('Done')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Required arguments missing. Run as 'python <scriptname> <color-relief-file> <dem-file>")
    else:
        colorFilePath = sys.argv[1]
        demPath = sys.argv[2]

        createColorAndHSDems(demPath, colorFilePath)