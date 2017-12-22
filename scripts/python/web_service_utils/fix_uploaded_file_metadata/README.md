This folder contains the python file to fix files with wrong meta data.

Procedure
---------
1. Take all images which need to be fixed, and keep it in a certain
folder at path `IMAGES_TO_FIX_FOLDER`.
2. Set up your local machine to run the Assistant APIs Web Service
at **port 8000**. Ensure that the Cloud function that the local
Assistant APIs point to, is the one that will fix the metadata for the
file (`updateMetaDataLatLongFix`).
3. Run the python script, with the first commandline argument as the path
to the folder containing the images `IMAGES_TO_FIX_FOLDER`:
```
python create_list_wrong_meta.py IMAGES_TO_FIX_FOLDER
```
4. This will create a CSV in the current working directory with the list of
images and details, that need to be fixed. Let the path to the CSV be
`PATH_TO_ENTITY_LIST_CSV`.
5. Then, run the following to implement the fix:
```
python fix_wrong_meta.py PATH_TO_ENTITY_LIST_CSV
```





