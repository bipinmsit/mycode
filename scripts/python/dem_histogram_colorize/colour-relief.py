"""
Color relief interpolation file

Author: Abhishek Mishra
Date: 15th Jun 2017
"""
import os.path
import cv2
import numpy as np

def rgb_to_hsv(rgb):
    bgr_arr = np.uint8([[[rgb[2],rgb[1],rgb[0]]]])
    hsv = cv2.cvtColor(bgr_arr,cv2.COLOR_BGR2HSV)
    return (int(hsv[0, 0, 0]), int(hsv[0, 0, 1]), int(hsv[0, 0, 2]))

def hsv_to_rgb(hsv):
    hsv = np.uint8([[[hsv[0],hsv[1],hsv[2]]]])
    bgr_arr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    return (int(bgr_arr[0, 0, 2]), int(bgr_arr[0, 0, 1]), int(bgr_arr[0, 0, 0]))

def read_colour_relief(crfname):
    '''
    Reads a colour relief file, and returns the contents as a dict
    with elevation as key and rgb color as value.
    '''
    colour_relief = {}
    if os.path.isfile(crfname):
        crfile = open(crfname)
        for line in crfile:
            words = line.split()
            if len(words) == 4:
                elevation = words[0]
                if elevation != 'nv':
                    elevation = float(elevation)
                    red = int(words[1])
                    green = int(words[2])
                    blue = int(words[2])
                    rgb = (red, green, blue)
                    hsv = rgb_to_hsv(rgb)
                    colour_relief[elevation] = (rgb, hsv)
    else:
        print('File not found:', crfname)

    return colour_relief

def create_image(colours, width = 40, height = 20):
    """ 
    Create a rectangular image with stacked colour bars for each colour in
    the colours array
    """
    blank_image = np.zeros((height * len(colours),width,3), np.uint8)
    for i in range(len(colours)):
        c = colours[i]
        bgr = (c[2], c[1], c[0])
        blank_image[height * i: height * (i + 1), 0: width] = bgr
    cv2.imwrite('color-relief.png',blank_image)
    print('interpolated color relief is written to color-relief.png')

def interpolate_colour(start_elevation, start_colour, end_elevation, end_colour, elevation_increment=1.0):
    """
    interpolates hsv colours from start colour to end colour
    while also incrementing elevation.

    So we have a continuous list of elevations and corresponding colours
    from start to end of elevation and colours
    """
    eldiff = end_elevation - start_elevation
    num_increments = int(eldiff/elevation_increment)
    hincr = (end_colour[0] - start_colour[0])/num_increments
    sincr = (end_colour[1] - start_colour[1])/num_increments
    vincr = (end_colour[2] - start_colour[2])/num_increments

    colours = [start_colour]
    elevations = [start_elevation]
    for i in range(num_increments):
        hsv = (start_colour[0] + (i * hincr), start_colour[1] + (i * sincr), start_colour[2] + (i * vincr))
        colours.append(hsv)
        elevations.append(start_elevation + (i * elevation_increment))
    
    colours.append(end_colour)
    elevations.append(end_elevation)
    #print(elevations, colours)
    return elevations, colours

def interpolate_colour_relief(colour_relief, elevation_increment=1.0):
    """
    for each contiguous pair of elevations in the colour relief file
    create an interpolated elevation + colour sequence
    then merge them all and return the interpolated colour
    relief as a dictionary.

    returned dict has elevation as key and colour (rgb) as value.
    """

    elevations = sorted(colour_relief.keys())
    new_colour_relief = {}
    if len(elevations) > 1:
        start = elevations[0]
        for i in range(1, len(elevations)):
            end = elevations[i]
            new_elevations, hsv_colours = interpolate_colour(start, colour_relief[start][1],
                                                             end, colour_relief[end][1], elevation_increment)
            colours = []
            for hsv in hsv_colours:
                colours.append(hsv_to_rgb(hsv))

            for j in range(len(new_elevations)):
                new_colour_relief[new_elevations[j]] = colours[j]
            start = end
    return new_colour_relief

if __name__ == "__main__":
    colour_relief = read_colour_relief('colour-relief-sowparnika-v2.txt')
    new_colour_relief = interpolate_colour_relief(colour_relief, elevation_increment=0.5)
    elevations = sorted(new_colour_relief.keys())
    print(elevations)
    colours = []
    for e in elevations:
        colours.append(new_colour_relief[e])
    #print(colours)
    create_image(colours)
    # for e in elevations:
    #     color = new_colour_relief[e]
    #     print (e, color[0], color[1], color[2])
    # print('nv', 0, 0, 0)
