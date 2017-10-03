import os
import glob
SITE = "tharangini"
DATE = "2017-08-30"
SESSION_NO = "03"
files = glob.glob("*.jpg")
for file in files:
    out_name = SITE + "_" + DATE + "_" + SESSION_NO + "_" + file
    os.rename(file, out_name)

