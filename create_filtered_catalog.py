import requests
import json
import gcsfs
from tqdm.autonotebook import tqdm
import pandas as pd


# first get the total number of results
# url = "https://esgf-data.dkrz.de/esg-search/search"
# suggestion from @durack1 for more reliable search (https://github.com/pangeo-data/pangeo-cmip6-cloud/issues/30#issuecomment-1045620838)
url = "https://esgf-node.llnl.gov/esg-search/search"
params = {
    "type": "Dataset",
    "mip_era": "CMIP6",
    "replica": "false",
    "distrib": "true",
    "retracted": "true",
    "format": "application/solr+json",
    "fields": "instance_id",
}

resp = requests.get(url=url, params=params)
header = resp.json()  # Check the JSON Response Content documentation below
n_items = header["response"]["numFound"]

batchsize = 5000

batches = range(0, n_items+1, batchsize)  # if I offset these, can
params["limit"] = batchsize

batch_jsons = []

print("Downloading Retraction Data...")
for batch in tqdm(batches):
    params["offset"] = batch
    resp = requests.get(url=url, params=params)
    if resp.status_code != 200:
        print(batch)
        print(resp.status_code)
    data = resp.json()
    batch_jsons.append(data)

# Convert to list of instance ids
print("Extracting instance_ids...")
all_retracted_instance_ids = []
for data in tqdm(batch_jsons):
    extracted = [i["instance_id"] for i in data["response"]["docs"]]
    all_retracted_instance_ids.extend(extracted)

# Fail out here if the total number of items is not what was promised in the header
# I had a few instances today, where that was the case, I think a simple retry is
# a good enough solution for now.
n_retracted = len(all_retracted_instance_ids)
if n_retracted == n_items:
    print('Successfully downloaded all retraction info')
else:
    raise RuntimeError(f'Downloaded retraction info is incomplete. Found {n_retracted} items, expected {n_items}')

# There is the possibility that we are getting duplicate instance_ids here because we query replicas
# Make sure dubplicates are not carried forward
retracted_instance_ids = set(all_retracted_instance_ids)
print(f"{len(all_retracted_instance_ids)-len(retracted_instance_ids)} replicas found")


# Now check which of the retracted datasets are in the pangeo catalog
df_retracted_instance_ids = pd.Series(list(retracted_instance_ids)).to_frame(
    name="instance_id"
)

pangeo_df = pd.read_csv("https://cmip6.storage.googleapis.com/pangeo-cmip6.csv")

pangeo_df["instance_id"] = pangeo_df["zstore"].apply(
    lambda x: ".".join(x.replace("gs://cmip6/", "").split("/")[0:-1])
)

df_to_remove = pangeo_df.merge(df_retracted_instance_ids, on="instance_id")
print(f"Found {len(df_to_remove)} stores that need to be removed!")

df_to_keep = pangeo_df.merge(
    df_retracted_instance_ids, on=["instance_id"], how="left", indicator=True
)
df_to_keep = df_to_keep[df_to_keep["_merge"] == "left_only"]

# cleaning up
df_to_keep = df_to_keep.drop(columns=["_merge", "instance_id"])

# Make sure that this did not loose/add entries
assert len(df_to_keep) + len(df_to_remove) == len(pangeo_df)

# Now write out the new catalog that does not contain the retraced dataset
# for local testing
# with open("/home/jovyan/keys/google_cmip6_service.json") as token_file:
#     token = json.load(token_file)
# gcs = gcsfs.GCSFileSystem(token=token)
gcs = gcsfs.GCSFileSystem()

# create local file
df_to_keep.to_csv("local_test_retracted.csv", index=False)
# upload that to the cloud
print("Uploading filtered catalog")
gcs.put_file("local_test_retracted.csv", "cmip6/test_retracted.csv")
# done
