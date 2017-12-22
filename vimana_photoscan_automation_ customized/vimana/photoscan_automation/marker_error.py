import PhotoScan

# doc = PhotoScan.app.document
# chunk = doc.chunk
# photos_total = len(chunk.cameras)

def check_marker_error(doc=None,chunk=None,err=None):
    for camera in chunk.cameras:
        for marker in chunk.markers:
            if not marker.projections[camera]:
                continue
            else:
                projections = marker.projections[camera].coord
                reprojection = camera.project(marker.position)
                error = (projections - reprojection)

                if error.norm()>0.5:
                    print(marker.label,camera.label)
                    marker.projections[camera] = None
                    PhotoScan.app.update()
                    doc.save()
                    check_marker_error(None)

# if __name__=="__main__":
#     check_marker_error(None)
