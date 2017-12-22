import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import os
import os.path
import ntpath
import sys
## Based on docs example here https://docs.opencv.org/3.1.0/d3/db4/tutorial_py_watershed.html

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    #obstacle_select = np.zeros_like(img[:,:,0])
    #gold_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    
    bgr_img = img[...,::-1]
    # Convert BGR to HSV
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    
    # define range of gold color in HSV
    lower_gold = np.array([10,100,100])
    upper_gold = np.array([30,255,255])

    # Threshold the HSV image to get only gold colors
    mask = cv2.inRange(hsv, lower_gold, upper_gold)
    
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(img, img, mask= mask)
    gold_thresh = (res[:,:,0] > 0) \
                & (res[:,:,1] > 0) 
            
    # Index the array of zeros with the boolean array and set to 1
    color_select[:] = 0
    color_select[above_thresh] = 1
    color_select[gold_thresh] = 0
    
    # Return the binary image
    return color_select
    #return (color_select, obstacle_select, gold_select)


def apply_color_thresholding(image):
    # Define color selection criteria
    ###### TODO: MODIFY THESE VARIABLES TO MAKE YOUR COLOR SELECTION
    red_threshold = 250
    green_threshold = 250
    blue_threshold = 250
    ######
    rgb_threshold = (red_threshold, green_threshold, blue_threshold)

    # pixels below the thresholds
    colorsel = color_thresh(image, rgb_thresh=rgb_threshold)

    fwblur = cv2.blur(colorsel, (7, 7))
    fw_canny_edge = cv2.Canny(fwblur, 100, 120)

    # Display the original image and binary
    # f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 30), sharey=True)
    # f.tight_layout()
    # ax1.imshow(image)
    # ax1.set_title('Original Image', fontsize=40)
    #
    # ax2.imshow(colorsel, cmap='hot')
    # ax2.set_title('Marker Isolated', fontsize=40)
    #
    # ax3.imshow(fw_canny_edge, cmap='Reds')
    # ax3.set_title('Marker Edges Detected', fontsize=40)
    #
    # plt.subplots_adjust(left=0., right=1, top=0.9, bottom=0.)
    return colorsel, fwblur


def get_background_and_foreground(colorsel):
    # noise removal
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(colorsel, cv2.MORPH_OPEN, kernel, iterations=2)

    # sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # plt.imshow(sure_bg)

    return sure_bg, sure_fg, unknown


def get_connected_component_markers(sure_bg, unknown):
    ret, markers = cv2.connectedComponents(sure_bg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1

    # Now, mark the region of unknown with zero
    markers[unknown == 255] = 0
    # print(ret, markers)

    # plt.imshow(markers, cmap='jet')

    len(markers[markers != 0])
    return ret, markers


def apply_marker_location(image, num_markers, markers, imagename):
    markers = cv2.watershed(image, markers)
    b_channel, g_channel, r_channel = cv2.split(image)
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 50

    # image[markers == 1] = [0,255,0]
    for mx in range(2, num_markers + 1):
        locs = np.where(markers == mx)
        print('number of pixels in connected component is ', len(locs[0]))

        if len(locs[0]) > 1000:
            print((min(locs[0]), min(locs[1])), (max(locs[0]), max(locs[1])))

            if abs(min(locs[0]) - max(locs[0])) < 25 or abs(min(locs[1]) - max(locs[1])) < 25:
                print('Marker dimension discovered is too small, most probably a false positive')
            else:
                alpha_channel[markers == 1] = 150
                # alpha_channel[markers==2]=255
                img_BGRA = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
                margin = 50
                img_BGRA = cv2.rectangle(img_BGRA, (min(locs[1]) - margin, min(locs[0]) - margin),
                                         (max(locs[1]) + margin, max(locs[0]) + margin), (255, 0, 0, 255), 5)
                img_BGRA[min(locs[0]) - margin: max(locs[0]) + margin, min(locs[1]) - margin:max(locs[1]) + margin, 3] = 255

                # plt.imshow(img_BGRA)
                # plt.imshow(img_BGRA, cmap='jet')

                cv2.imwrite(imagename + '-' + str(mx) + '.png', img_BGRA)


def circle_based_marker_detector(input_image, output_image_name):
    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 220
    params.maxThreshold = 255

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 80

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.85

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(input_image)
    for kp in keypoints:
        print(kp.pt)

    if len(keypoints) > 0:
        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
        # the size of the circle corresponds to the size of blob

        im_with_keypoints = cv2.drawKeypoints(input_image, keypoints, np.array([]), (0, 255, 0),
                                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        for kp in keypoints:
            cv2.circle(im_with_keypoints, (round(kp.pt[0]), round(kp.pt[1])), 100, (255, 0, 0), 5)
            cv2.circle(im_with_keypoints, (round(kp.pt[0]), round(kp.pt[1])), 2, (255, 255, 0), 1)

        # Show blobs
        #plotImageLarge(im_with_keypoints)
        cv2.imwrite(output_image_name + '.png', im_with_keypoints)
    return keypoints

if __name__ == "__main__":
    #images_folder = '/media/abhishek/6A140D7E140D4F0F/linux-data/test-datasets/sowparnika_thecolumn_2017_08_11/Images'
    #images_folder = '/media/abhishek/6A140D7E140D4F0F/linux-data/test-datasets/2017_09_04/Images'
    if len(sys.argv) > 1:
        images_folder = sys.argv[1]
        marker_folder = os.path.join(images_folder, 'Markers')
        if not os.path.exists(marker_folder):
            os.makedirs(marker_folder, False)
        image_files = []
        for f in os.listdir(images_folder):
            if f.endswith('.jpg') or f.endswith('.JPG'):
                image_files.append(os.path.join(images_folder, f))

        for image_name in image_files:
            #image_name = 'f-tharangini_2017_07_14_02_DJI_0003.MP4-076.jpg'
            if image_name.endswith('.jpg'):
                img_prefix = image_name.split('.jpg')[0]
            else:
                img_prefix = image_name.split('.JPG')[0]
            image = mpimg.imread(image_name)
            marker_file = os.path.join(marker_folder, ntpath.basename(img_prefix) + '-marker')
            kps = circle_based_marker_detector(image, marker_file)
            print(str(len(kps)) + ' MARKERS detected in ' + image_name)
            # colorsel, fwblur = apply_color_thresholding(image)
            # sure_bg, sure_fg, unknown = get_background_and_foreground(colorsel)
            # num_markers, markers = get_connected_component_markers(sure_bg, unknown)
            # if num_markers > 1:
            #     marker_file = os.path.join(marker_folder, ntpath.basename(img_prefix) + '-marker')
            #     print('Marker FOUND in image - ', image_name, ' writing to - ' + marker_file)
            #     apply_marker_location(image, num_markers, markers, marker_file)
            # else:
            #     print('No markers found in image - ', image_name)
    else:
        print('Usage: python marker_detection.py <FullPathToImagesFolder>')