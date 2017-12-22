import csv
import PhotoScan
import logging


def read_marker(path_to_marker_file, chunk=None):
    marker_list = list(csv.DictReader(open(path_to_marker_file)))
    number_of_cameras = len(marker_list)
    j = 0
    while j < number_of_cameras:
        title = list(marker_list[j].keys())
        camera_name = marker_list[j]["camera_label"]
        marker_name = marker_list[j]["marker_label"]
        x = float(marker_list[j]["px_x"])
        y = float(marker_list[j]["px_y"])
        cx = float(marker_list[j]["world_x"])
        cy = float(marker_list[j]["world_y"])
        cz = float(marker_list[j]["altitude"])
        photos_total = len(chunk.cameras)  # number of photos in chunk

        logging.info(str(j) + " " + camera_name + " " + marker_name)
        for i in range(0, photos_total):
            if chunk.cameras[i].label == camera_name:
                marker_found = False
                marker_to_use = None
                logging.info("found a camera " + camera_name)
                logging.info("no of markers in projects " + str(len(chunk.markers)))
                for marker in chunk.markers:  # searching for the marker (comparing with all the marker labels in chunk)
                    logging.info("found marker name " + marker.label)
                    if marker.label == marker_name:
                        marker_found = True
                        marker_to_use = marker
                        break

                if not marker_found:
                    logging.info("creating marker "+marker_name+" because it doesnt exist")
                    marker_to_use = chunk.addMarker()
                    marker_to_use.label = marker_name
                    marker_to_use.reference.location = PhotoScan.Vector([cx, cy, cz])

                logging.info(marker_to_use.label + "adding marker to" + camera_name)
                marker_to_use.projections[chunk.cameras[i]] = (x, y)  # setting up marker projection of the correct photo

        chunk.updateTransform()
        j = j + 1
