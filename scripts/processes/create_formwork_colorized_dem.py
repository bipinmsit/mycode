from create_colorized_dem import *
import sys
from io import StringIO
import ntpath
import os.path
import pandas as pd

COLOR_FILE_TEMPLATE = StringIO("""
elevation,r,g,b,colourname 
0.41,0,0,0,#Black
0.4,255,182,193,#LightPink
0.35,255,99,71,#Tomato
0.25,106,90,205,#SlateBlue
0.15,128,128,0,#Olive
0.05,250,128,114,#Salmon
0.0,147,112,219,#MediumPurple
-0.04,144,238,144,#LightGreen
-0.07,64,224,208,#Turquoise
-0.08,30,144,255,#DodgerBlue
-0.09,210,105,30,#Chocolate
-0.1,255,218,185,#PeachPuff
-0.3,255,0,0,#Red
-0.4,0,0,205,#MediumBlue
-0.45,75,0,130,#Indigo
-0.5,0,128,128,#Teal
-0.55,0,128,0,#Green
-0.7,160,82,45,#Sienna
-0.85,199,21,133,#MediumVioletRed
-0.9,0,0,0,#Black
nv,0,0,0,#Black
""")


def createColorFile(demPath, floorElevation):
    
    def addElevation(x):
        try:
            return str(round(float(x) + floorElevation, 2))
        except:
            return x

    demDir = ntpath.dirname(demPath)
    colour_file_name = os.path.join(demDir, 'colour-file-floor-' + str(floorElevation) + '.txt')
    print('writing floor colour file to ' + colour_file_name);
    df = pd.read_csv(COLOR_FILE_TEMPLATE, sep=",")
    df['elevation'] = df['elevation'].apply(addElevation)
    print(df.head())

    df.to_csv(colour_file_name, sep=' ', header=False, index=False)
    return colour_file_name

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Required arguments missing. Run as 'python <scriptname> <floor-elevation> <dem-file>")
    else:
        floorElevation = float(sys.argv[1])
        demPath = sys.argv[2]
        colorFilePath = createColorFile(demPath, floorElevation)
        createColorAndHSDems(demPath, colorFilePath)