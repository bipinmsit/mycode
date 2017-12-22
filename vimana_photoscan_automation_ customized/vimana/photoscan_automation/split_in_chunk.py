import PhotoScan
import json
import re
from decimal import Decimal

QUALITY = {"1": PhotoScan.LowestQuality,
           "2": PhotoScan.LowestQuality,
           "4": PhotoScan.LowestQuality,
           "8": PhotoScan.LowestQuality,
           "16": PhotoScan.LowestQuality}

FILTERING = {"3": PhotoScan.NoFiltering,
             "0": PhotoScan.MildFiltering,
             "1": PhotoScan.ModerateFiltering,
             "2": PhotoScan.AggressiveFiltering}

class SplitDlg:
    def __init__(self, parent):
        self.splitChunks()

    def create_chunk_list(self, dictionary_of_regex=None):
        print(dictionary_of_regex)
        chunk_list = []
        for k, v in dictionary_of_regex.items():
            if isinstance(v, dict):
                return self.create_chunk_list(v)
            else:
                a_list = list([k, v])
                chunk_list.append(a_list)
        return chunk_list

    def splitChunks(self):
        print("Script started")
        buildMesh = 1
        buildDense = 1
        mergeBack = 1
        autosave = 1

        doc = PhotoScan.app.document
        chunk = doc.chunk

        if not chunk.transform.translation:
            chunk.transform.matrix = chunk.transform.matrix

        workflow_config_file = '/home/aspecscire/Desktop/workflow_config.json'
        with open(workflow_config_file, 'r') as f:
            config = json.load(f, parse_int=int, parse_float=Decimal)

        chunk_list = self.create_chunk_list(config["split_into_chunks"])
        length_of_chunk_list = len(chunk_list)
        print(chunk_list)
        c=0
        for j in range(1, length_of_chunk_list+1):  # creating new chunks and removing the camera
            new_chunk = chunk.copy(items=[PhotoScan.DataSource.DenseCloudData])
            new_chunk.label = str(chunk_list[c][0])
            new_chunk.model = None
            regex_expression =chunk_list[c][1]
            pattern = re.compile(regex_expression)
            c=c+1
            for camera in list(new_chunk.cameras):
                if not pattern.match(camera.label):
                    new_chunk.remove(camera)
                else:
                    print(camera.label)


            PhotoScan.app.update()

        if autosave:
            doc.save()

        if buildDense:
            for i in range(1, len(doc.chunks)):
                new_chunk = doc.chunks[i]
                if new_chunk.depth_maps:
                    reuse_depth = True
                    quality = QUALITY[new_chunk.depth_maps.meta['depth/depth_downscale']]
                    filtering = FILTERING[new_chunk.depth_maps.meta['depth/depth_filter_mode']]
                    try:
                        new_chunk.buildDenseCloud(quality=quality, filter=filtering, keep_depth=False,
                                                  reuse_depth=reuse_depth)
                    except RuntimeError:
                        print("Can't build dense cloud for " + chunk.label)

                else:
                    reuse_depth = False
                    try:
                        new_chunk.buildDenseCloud(quality=PhotoScan.Quality.LowestQuality,
                                                  filter=PhotoScan.FilterMode.AggressiveFiltering, keep_depth=False,
                                                  reuse_depth=reuse_depth)
                    except RuntimeError:
                        print("Can't build dense cloud for " + chunk.label)

                if autosave:
                    doc.save()

            if buildMesh:
                for i in range(1, len(doc.chunks)):
                    new_chunk = doc.chunks[i]
                    if new_chunk.dense_cloud:
                        try:
                            new_chunk.buildModel(surface=PhotoScan.SurfaceType.HeightField,
                                                 source=PhotoScan.DataSource.DenseCloudData,
                                                 interpolation=PhotoScan.Interpolation.EnabledInterpolation,
                                                 face_count=PhotoScan.FaceCount.LowFaceCount)
                        except RuntimeError:
                            print("Can't build mesh for " + chunk.label)
                    else:
                        try:
                            new_chunk.buildModel(surface=PhotoScan.SurfaceType.HeightField,
                                                 source=PhotoScan.DataSource.DenseCloudData,
                                                 interpolation=PhotoScan.Interpolation.EnabledInterpolation,
                                                 face_count=PhotoScan.FaceCount.LowFaceCount)
                        except RuntimeError:
                            new_chunk.buildModel(surface=PhotoScan.SurfaceType.HeightField,
                                                 source=PhotoScan.DataSource.DenseCloudData,
                                                 interpolation=PhotoScan.Interpolation.EnabledInterpolation,
                                                 face_count=PhotoScan.FaceCount.LowFaceCount)
                    if autosave:
                        doc.save()

                    if not buildDense:
                        new_chunk.dense_cloud = None

                    new_chunk.depth_maps = None
                    # new_chunk = None

        if mergeBack:
            for i in range(1, len(doc.chunks)):
                chunk = doc.chunks[i]
                chunk.remove(chunk.cameras)
            doc.chunks[0].model = None  # removing model from original chunk, just for case
            doc.chunks.pop(0)
            doc.mergeChunks(doc.chunks, merge_dense_clouds=True, merge_models=True,
                            merge_markers=True)  # merging all smaller chunks into single one
            # doc.remove(doc.chunks[1:-1])
            if autosave:
                doc.save()

        if autosave:
            doc.save()

        print("Script finished")
        return True


if __name__=="__main__":
    global doc
    doc = PhotoScan.app.document
    dlg = SplitDlg(doc)
