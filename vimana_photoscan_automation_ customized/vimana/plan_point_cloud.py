import laspy

header = laspy.header.Header()
outfile = laspy.file.File("output.las", mode="w", header=header)
outfile.X = [1, 2, 3]
outfile.Y = [0, 0, 0]
outfile.Z = [10, 10, 11]
outfile.close()