This folder contains scripts to create upload to Google Cloud Storage, where the release versions
of the photogrammetry pipeline will be stored. 

This is done by automatically pulling files from their respective bitbucket repos, and creating a tar ball of each. 
These tar balls, are added to a folder `release-v0.1.0` (for version 0.1.0). The name will change
according to version number. 

This folder with the tar balls are then uploaded Google Cloud Storage.

