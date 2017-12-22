from raster_processing.raster_chunks import GeoChunks as gc
from dem_processing.dem_perf_check import create_delta_DEM
import os.path
import gdal


def terrain_accuracy(demfile, dtmfile, epsilon=0.2, max_tree_height=30):
    '''
    Calculates the accuracy of the terrain model.
    accuracy = (# of points with error)/(total # of points)

    A point has error if its delta is less than epsilon or greater than
    max_tree_height. where delta = dtm - dem.

    :param demfile: path to dem
    :param dtmfile: path to dtm
    :param epsilon: value of epsilon(error allowed for ground points)
    :param max_tree_height: max assumed height of trees(non terrain features) in the area.
    :return: accuracy score
    '''

    dem = gc(demfile)
    dtm = gc(dtmfile)

    deltafile = './data/delta.tif'
    create_delta_DEM(demfile, dtmfile, deltafile)
    delta = gc(deltafile)

    dem_chunks = dem.break_chunks()
    dtm_chunks = dtm.break_chunks()
    delta_chunks = delta.break_chunks()

    total_count = 0
    error = 0

    for i in range(len(dem_chunks)):
        dem_chunk = dem_chunks[i]
        dtm_chunk = dtm_chunks[i]
        delta_chunk = delta_chunks[i]
        dem_data = dem.read(0, dem_chunk)
        dtm_data = dtm.read(0, dtm_chunk)
        delta_data = delta.read(0, delta_chunk)

        #print(dem_data.shape)

        for i in range(dem_data.shape[0]):
            for j in range(dem_data.shape[1]):
                if delta_data[i, j] == 0.0:
                    pass
                else:
                    if delta_data[i, j] < -epsilon or delta_data[i, j] > max_tree_height:
                        #print(delta_data[i, j])
                        error += 1
                    total_count += 1

    accuracy = None
    if total_count > 0:
        accuracy = 100 - (error/total_count * 100)
    #print('# of points with error=', error, ' | total # of points=', total_count, ' | accuracy=', accuracy, '%')

    return error, total_count, accuracy

if __name__ == "__main__":
    data_folder = 'C:/code/aspecscire/scripts/python/dem_processing/data/'
    demfile = os.path.join(data_folder, 'M_DS_s5_dem.tif')
    print('DEM file - ', demfile)
    for i in range(1, 6):
        dtmfile = os.path.join(data_folder, 'M_DS_s5_dtm_{}.tif'.format(i))
        if os.path.isfile(demfile) and os.path.isfile(dtmfile):
            error, total_count, accuracy = terrain_accuracy(demfile, dtmfile)
            print('Accuracy for DTM file - ', dtmfile, ' is ', '{:.2f}%'.format(accuracy))
