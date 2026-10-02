"""Full Python script that will 1.) Read in FluxMap data 2.) Filter the data based on quality threshold 3.) Read in vector layers for polygon analysis if wanted 4.) Compute diurnal cycles for the whole raster, or polygons defined."""

# Disclaimer
#It is in an early (0.6.0) phase in which behavior may still change between releases. Names and arguments are subject to change until they lock at the 1.0.0 version. Name changes from 0.6.0 to 1.0.0 could cause warnings to appear when using the package.

# Function that downloads data from the google cloud bucket (Public NEON data used as placeholder example)
from pathlib import Path
import requests

#Function that will download data directly from Google Cloud Storage (Un-comment out if needed)

#def download_gcs_folder(bucket, prefix, dest):
    #"""Download every object under gs://bucket/prefix, keeping folder layout."""
    #api = f"https://storage.googleapis.com/storage/v1/b/{bucket}/o"
    #params = {"prefix": prefix, "fields": "items(name,size),nextPageToken"}
    #while True:
        #listing = requests.get(api, params=params, timeout=60)
        #listing.raise_for_status()
        #listing = listing.json()
        #for obj in listing.get("items", []):
            #out = dest / obj["name"]
            #if out.exists() and out.stat().st_size == int(obj["size"]):
                #continue  # already downloaded
            #out.parent.mkdir(parents=True, exist_ok=True)
            #with requests.get(f"https://storage.googleapis.com/{bucket}/{obj['name']}", stream=True, timeout=60) as r:
                #r.raise_for_status()
                #with open(out, "wb") as f:
                    #for chunk in r.iter_content(chunk_size=1 << 20):
                        #f.write(chunk)
            #print("downloaded", obj["name"])
        #if "nextPageToken" not in listing:
            #break
        #params["pageToken"] = listing["nextPageToken"]


# Setting the google bucket to it reads the KONA data (Un-comment out if needed)

#BUCKET = "data-neon"
#PREFIX = "KONA/fluxCo2/2024/"   # site / flux type / year (can change for different sets of public data)
#DATA_DIR = Path("KONA")          # local folder the rest of the tutorial reads from

#Actually obtaining the data (Un-comment out if needed)

#download_gcs_folder(BUCKET, PREFIX, DATA_DIR)

# If you have FluxMap tif files saved on your local computer already, you would not need this step. This step is mainly used for example purposes.

# If you downloaded data from google cloud bucket, then use this line when specifying the data you are using (Line 58)

# DATA_DIR / "KONA/fluxCo2/2024/07/01/kona_fluxCo2_20240701.tif" (Replace Kona with your local data)






# Importing necessary libraries including fluxmapPy

from fluxmappy import wrap_filt_qf, wrap_diu, wrap_stat, wrap_open_fm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Please Specify Variables 

# Folder in which your data is located (Input local directory path)
data = "" #Input local directory path

# Quality Flag Threshold in which to filter pixels in rasters.
qf_thsh = 1

# Keep data less than the filter (input 'lte') or greater than the filter (input 'gte')
qf_keep = 'lte'

#Flux type to analyze 
flux = 'fluxCo2'

#Vector file containing shape file (Replace None with vector file path if wanted)
vector = None

# Output timezone for data location
out_tz = 'America/Chicago'

#Specify which type of diunral cycle       !!!! Must change setting below !!!!
Diurnal_Cycle = 'Mean'


# FluxmapPy functions
filtered = wrap_filt_qf(data,flux = flux, qf_thsh = qf_thsh, qf_keep = qf_keep)
cycles = wrap_diu(filtered, vector = vector, in_tz = 'UTC', out_tz = out_tz)


#Plotting Diurnal Cycle
hours = np.arange(48) / 2

fig = plt.figure(figsize=(12, 8))

polygon1 = cycles[0]
polygon2 = cycles[1]
#Continue if additional polygons are within vector

# Must specify result.mean_cycle (mean diurnal) or result.cumulative_cycle (cumulative diurnal) on line 45!
plt.plot(hours,polygon1.mean_cycle, label = 'Polygon1', color = 'red',marker= 'o')
plt.plot(hours,polygon2.mean_cycle, label = 'Polygon2', color = 'blue',marker= 's')
#Continue if additional polygons are within vector

    
plt.xlabel(f"Hour of day [{out_tz}]")
plt.ylabel(f"{Diurnal_Cycle} Diurnal Cycle {flux}")
plt.title(f"{Diurnal_Cycle} Diurnal Flux{flux} [QF={qf_thsh}]")
plt.xticks(np.arange(0, 25, 2))
plt.grid(alpha=0.3)
plt.legend(title="Polygon")
plt.tight_layout()
plt.show()




