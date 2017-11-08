from osgeo import ogr

# Create a geometry collection

geomcol = ogr.Geometry(ogr.wkbGeometryCollection)

# Add a point

point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(77.783384, 12.883127)
geomcol.AddGeometry(point)

# Add a line

line = ogr.Geometry(ogr.wkbLineString)
line.AddPoint(-122.60, 47.14)
line.AddPoint(-122.48, 47.23)

geomcol.AddGeometry(line)

print(goemcol.ExportToWkt())
