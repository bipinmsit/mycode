Google Datastore Utilities
=========================

This folder contains utitlities to empty bucket and datastore entitities. 

To remove all files from a particular bucket, do 
```
gsutil -m rm gs://<bucket-name>/*

```

Buckets to clean up:- 
1. **vimana-raw-files-qa**
2. **vimana-project-files-qa**


To remove all entities of a particular kind, first edit the **KIND** in `delete_kind.py`, 
to the kind that you want to delete. 

Then, run 
```
python delete_kind.py
```

Entity Kinds to clean up:-
1. **ImageMetadata**
2. **Workflow**
3. **ProcessingSession**

