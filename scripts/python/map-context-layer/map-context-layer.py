import sys
from geojson import FeatureCollection, Feature, Point, LineString, MultiLineString, Polygon

def create_bounding_box(topleft, bottomright):
    topright = (bottomright[0], topleft[1])
    bottomleft = (topleft[0], bottomright[1])

    return Polygon([[topleft, topright, bottomright, bottomleft]])

def create_grid_lines(topleft, bottomright, num_lines = 5):
    topright = (bottomright[0], topleft[1])
    bottomleft = (topleft[0], bottomright[1])

    long_diff = bottomright[0] - topleft[0]
    long_interval = long_diff/num_lines

    # print(topleft, bottomright)
    # print(long_diff, long_interval)

    lat_diff = topleft[1] - bottomright[1]
    lat_interval = lat_diff/num_lines

    lines = []
    grid_points = [topleft, topright, bottomleft, bottomright]

    for i in range(1, num_lines):
        low = (bottomleft[0] + (i * long_interval), bottomleft[1])
        high = (topleft[0] + (i * long_interval), topleft[1])
        hline = [low, high]

        left = (bottomleft[0], bottomleft[1] + (i * lat_interval))
        right = (bottomright[0], bottomright[1] + (i * lat_interval))
        vline = [left, right]

        lines.append(vline)
        lines.append(hline)
        grid_points.append(low)
        grid_points.append(high)
        grid_points.append(left)
        grid_points.append(right)

    return MultiLineString(lines), grid_points

if __name__ == "__main__":
    # my_feature = Feature(geometry=Point((1.6432, -19.123)))
    # my_other_feature = Feature(geometry=Point((-80.234, -22.532)))
    # fc = FeatureCollection([my_feature, my_other_feature])

    # print(fc)

    if len(sys.argv) == 5:
        topleft = (float(sys.argv[2]), float(sys.argv[1]))
        bottomright = (float(sys.argv[4]), float(sys.argv[3]))

        bounding_box = create_bounding_box(topleft, bottomright)
        grid_lines, grid_points = create_grid_lines(topleft, bottomright)

        features = []
        bbfeature = Feature(geometry=bounding_box)
        features.append(bbfeature)
        glfeature = Feature(geometry=grid_lines)
        features.append(glfeature)

        for p in grid_points:
            title = '(' + "{0:.6f}".format(p[1]) + ', ' + "{0:.6f}".format(p[0]) + ')'
            pf = Feature(geometry=Point(p), properties={"title": title})
            features.append(pf)

        fc = FeatureCollection(features)
        print (fc)

        f = open('grid.geojson', 'w')
        f.write(str(fc))
        f.close()
    else:
        print ('Not enough args. You need to provide <top left lat> <top left long> <bottom right lat> <bottom right long>')