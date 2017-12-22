#! /usr/bin/env python3
import sys
import os
import logging
import ntpath
from pymediainfo import MediaInfo
import pandas as pd
from PIL import Image
import piexif
import subprocess
from datetime import datetime

# setup_logging('.')


def get_vid_metadata(vidfiles):
    vidmeta_list = []
    for f in vidfiles:
        media_info = MediaInfo.parse(f)
        print(media_info)
        xyz_str = media_info.to_data()['tracks'][0]['xyz']
        tagged_date = media_info.to_data()['tracks'][0]['tagged_date']
        tagged_date = datetime.strptime(tagged_date, "%Z %Y-%m-%d %H:%M:%S")
        xyz_split = xyz_str.split('+')
        print(f + ' ' + str(xyz_split))
        vidmeta_list.append([f, float(xyz_split[1]), float(xyz_split[2]), float(xyz_split[3]), -1, tagged_date])

    df = pd.DataFrame(vidmeta_list, columns=['vid', 'lat', 'long', 'z', 'num_frames', 'datetime'])
    df = df.sort_values(by='datetime')
    return df


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def interpolate(x1, y1, z1, x2, y2, z2, tp):
    if tp > 0:
        xdiff = (x2 - x1)/tp
        ydiff = (y2 - y1)/tp
        zdiff = (z2 - z1)/tp
        vals = []
        for i in range(tp):
            vals.append(((x1 + (xdiff * i)), (y1 + (ydiff * i)), (z1 + (zdiff * i))))
        return vals
    else:
        return None


def frames_from_vid(fvid, frames_dir, fps=5):
    vidname = path_leaf(fvid)
    frame_file_fmt = 'f-{}-%03d.jpg'

    first_file = os.path.join(frames_dir, 'f-{}-001.jpg'.format(vidname))
    logging.info('Look for file ' + first_file + ', and if found, do not run frame extraction')

    if os.path.isfile(first_file):
        logging.info(first_file + ' exists.')
    else:
        logging.info('generating frames for ' + fvid)
        if fvid.endswith('.mp4') or fvid.endswith('.MP4'):
            frm = os.path.join(frames_dir, frame_file_fmt.format(path_leaf(fvid)))
            ffargs = ['ffmpeg', '-i', fvid, '-r', str(fps), '-qscale:v', '2', frm]
            logging.info(ffargs)
            subprocess.call(ffargs)

    pref = 'f-{}'.format(vidname)
    num_frames = 0
    for f in os.listdir(frames_dir):
        if f.startswith(pref):
            d = int(f[len(pref)+1:len(pref)+4])
            if d > num_frames:
                num_frames = d

    logging.debug(num_frames)
    return num_frames


def generate_frames(vid_meta, frames_dir):
    nf = vid_meta.iloc[0:-1]['vid'].apply(lambda x: frames_from_vid(x, frames_dir))
    logging.info(nf)
    # using boolean array indexing to select the every row except the last
    valid_videos = [True] * len(vid_meta)
    valid_videos[-1] = False
    vid_meta.loc[valid_videos, 'num_frames'] = nf
    logging.info(vid_meta)


zeroth_ifd = {piexif.ImageIFD.Make: u"Canon",
              piexif.ImageIFD.XResolution: (96, 1),
              piexif.ImageIFD.YResolution: (96, 1),
              piexif.ImageIFD.Software: u"piexif"
              }
exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u"2099:09:29 10:10:10",
            piexif.ExifIFD.LensMake: u"LensMake",
            piexif.ExifIFD.Sharpness: 65535,
            piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
            }

# see comment at the bottom of the page at https://github.com/hMatoba/piexifjs/issues/1
# for GPS lat/long format


def degToDmsRational(degFloat):
    minFloat = degFloat % 1 * 60
    secFloat = minFloat % 1 * 60
    deg = int(degFloat)
    min = int(minFloat)
    sec = int(round(secFloat * 100))

    return (deg, 1), (min, 1), (sec, 100)


def mark_frames(vid, num_frames, frames_dir, xyzlist):
    logging.info('marking frames of ' + vid + ' at ' + frames_dir)
    frame_file_fmt = 'f-{}-{:03d}.jpg'
    DENOM = 1 * pow(10, 6)
    for i in range(1, num_frames+1):
        filename = os.path.join(frames_dir, frame_file_fmt.format(path_leaf(vid), i))
        im = Image.open(filename)
        #exif_dict = piexif.load(im.info["exif"])
        # exif_dict["GPS"][piexif.ImageIFD.XResolution] = (w, 1)
        current_xyz = xyzlist[i-1]
        gps_ifd = { piexif.GPSIFD.GPSVersionID: (3, 2, 0, 0),
                    piexif.GPSIFD.GPSAltitudeRef: 0,
                    piexif.GPSIFD.GPSLatitudeRef: 'S' if current_xyz[0] < 0 else 'N',
                    piexif.GPSIFD.GPSLatitude: degToDmsRational(current_xyz[0]),
                    piexif.GPSIFD.GPSLongitudeRef: 'W' if current_xyz[1] < 0 else 'E',
                    piexif.GPSIFD.GPSLongitude: degToDmsRational(current_xyz[1]),
                    piexif.GPSIFD.GPSAltitude: (int(current_xyz[2] * DENOM), DENOM)}
        exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd, "GPS": gps_ifd}
        # process im and exif_dict...
        exif_bytes = piexif.dump(exif_dict)
        im.save(filename, "jpeg", exif=exif_bytes)


def process_videos(vid_folder=".", output_dir=None):
    vid_files = []

    logging.info('Videos folder is - ' + vid_folder)

    output_frames_dir = os.path.join(vid_folder, 'frames')
    if output_dir is not None:
        output_frames_dir = os.path.realpath(output_dir)

    if not os.path.isdir(output_frames_dir):
        os.makedirs(output_frames_dir)
    else:
        logging.info('frames folder already exists.')

    for f in os.listdir(vid_folder):
        if f.endswith('.mp4') or f.endswith('.MP4'):
            vid_files.append(os.path.join(vid_folder, f))

    logging.debug('Video files are -' + str(vid_files))

    vid_meta = get_vid_metadata(vid_files)
    print(str(vid_meta))

    generate_frames(vid_meta, output_frames_dir)

    for i in range(len(vid_meta) - 1):
        current = vid_meta.iloc[i]
        nxt = vid_meta.iloc[i+1]

        xyzlist = interpolate(current['lat'], current['long'], current['z'], nxt['lat'],
                              nxt['long'], nxt['z'], current['num_frames'])

        logging.debug(xyzlist)

        if xyzlist is not None:
            mark_frames(current['vid'], current['num_frames'], output_frames_dir, xyzlist)


def main():
    """
    Main function to handle execution
    :return:
    """
    if len(sys.argv) > 1:
        vid_folder = sys.argv[1]
    else:
        vid_folder = "."

    output_dir = None
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    process_videos(vid_folder, output_dir)


if __name__ == "__main__":
    sys.exit(main())
