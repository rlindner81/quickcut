# Quickcut

This is a python 3 script for cutting mkv files using a "controlling" csv file `quickcut.csv`.

The heavy lifting is done by MKVMerge, which is a hard dependency. It should be installed and on the path for this script to work. See
- https://mkvtoolnix.download
- https://www.fosshub.com/MKVToolNix.html (Win binaries)
- https://formulae.brew.sh/formula/mkvtoolnix (Mac OS homebrew)

An example control file looks like:
```
source     ,target  ,cut_from  ,cut_to
input.mkv  ,a.mkv   ,3034      ,4678
input.mkv  ,a.mkv   ,8082      ,27719
a.mkv      ,b.mkv   ,5612      ,10939
input.mkv  ,b.mkv   ,14668     ,22703
```

Note: The cuts don't occur exactly at the frame you point to here, but at the nearest keyframe to avoid re-encoding.

# Usage

- Install MKVMerge and Python3

```
cd <path with quickcut.csv and video files>
python <path with quickcut>/src/quickcut.py
```
