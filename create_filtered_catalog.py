import gcsfs
import pandas as pd
import os

from functools import reduce
from tqdm.autonotebook import tqdm
from datetime import date
from retractions import query_retraction_retry

gcs = gcsfs.GCSFileSystem()
catalog_url = "https://cmip6.storage.googleapis.com/pangeo-cmip6.csv"
node_urls = [
"https://esgf-node.llnl.gov/esg-search/search",
"https://esgf-data.dkrz.de/esg-search/search",
]

params = {
    "type": "Dataset",
    "mip_era": "CMIP6",
    "replica": "false",
    "distrib": "true",
    "retracted": "true",
    "format": "application/solr+json",
    "fields": "instance_id",
}
# query every one of the nodes
retracted_ids = {
    url :query_retraction_retry(
        url, params, batchsize=10000
    ) for url in node_urls
}

# convert to pandas dataframes
retracted_ids_df = [pd.Series(list(v)).to_frame(name="instance_id") for v in retracted_ids.values()]

# iteratively merge dataframes with 'outer' to get all possible retractions
# from https://stackoverflow.com/a/44338256
retracted_df = reduce(lambda  left,right: pd.merge(left,right,on=['instance_id'],how='outer'), retracted_ids_df)

## 
pangeo_df = pd.read_csv(catalog_url)

print('Backing up catalog')
local_filename = "local_catalog.csv"
backup_filename = f"old_{date.today()}_pangeo-cmip6.csv"
# create local file
pangeo_df.to_csv(local_filename, index=False)
# upload that to the cloud
gcs.put_file(local_filename, f'cmip6/{backup_filename}')
# remove the local copy
os.remove(local_filename)
# check backup
backup_df = pd.read_csv(f"https://cmip6.storage.googleapis.com/{backup_filename}")
print(f'Backed up catalog has {len(backup_df)} items')



# FILTER THE CURRENT CATALOG
pangeo_df["instance_id"] = pangeo_df["zstore"].apply(
    lambda x: ".".join(x.replace("gs://cmip6/", "").split("/")[0:-1])
)

df_to_remove = pangeo_df.merge(retracted_df, on="instance_id")
print(f"Found {len(df_to_remove)} stores that need to be removed!")

df_to_keep = pangeo_df.merge(
    retracted_df, on=["instance_id"], how="left", indicator=True
)
df_to_keep = df_to_keep[df_to_keep["_merge"] == "left_only"]

# cleaning up
df_to_keep = df_to_keep.drop(columns=["_merge", "instance_id"])

# Make sure that this did not loose/add entries
assert len(df_to_keep) + len(df_to_remove) == len(pangeo_df)

# create local file
df_to_keep.to_csv(local_filename, index=False)
# upload that to the cloud
print("Uploading filtered catalog")
gcs.put_file(local_filename, "cmip6/pangeo-cmip6.csv")

new_df = pd.read_csv(catalog_url)
print(f'Filtered catalog has {len(new_df)} items ({len(backup_df) - len(new_df)} less than before)')
