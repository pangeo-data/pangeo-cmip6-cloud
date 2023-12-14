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
# "https://esgf-data.dkrz.de/esg-search/search",
"https://esgf-index1.ceda.ac.uk/esg-search/search",
"https://esgf-node.ipsl.upmc.fr/esg-search/search",
]

params = {
    "type": "Dataset",
    "mip_era": "CMIP6",
    "distrib": "true",
    "retracted": "true",
    "format": "application/solr+json",
    "fields": "instance_id",
}
# query every one of the nodes
retracted_ids = {
     url.split('.')[1] :query_retraction_retry(
        url, params, batchsize=5000
    ) for url in node_urls
}

# convert to pandas dataframes
retracted_ids_df = {k:pd.Series(list(v)).to_frame(name="instance_id") for k,v in retracted_ids.items()}

# iteratively merge dataframes with 'outer' to get all possible retractions
# from https://stackoverflow.com/a/44338256
retracted_df = reduce(
    lambda  left,right: pd.merge(
        left,
        right,
        on=['instance_id'],
        how='outer'
    ), 
    retracted_ids_df.values()
)

## document missing instances for each node
print('Documenting missing instance_ids per node')
def unique_instances(df, df_full):
    """Return all the items of `df_full` not found in `df`"""
    df_merged = pd.merge(df, df_full, on=['instance_id'],how='outer', indicator=True)
    df_merged = df_merged[df_merged['_merge']=='right_only']
    df_merged = df_merged.drop(columns=['_merge'])
    return df_merged

missing_ids = {k: unique_instances(v, retracted_df) for k,v in retracted_ids_df.items()}

for k,v in missing_ids.items():
    print(f"Found {len(v)} missing instances from the {k} node.")
    filename = f"missing_instance_ids_{k}.csv"
    v['instance_id'].to_csv(filename, index=False)
    print(f"Missing instance_ids written to {filename}")

## 
print('Backing up catalog')
pangeo_df = pd.read_csv(catalog_url)
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
