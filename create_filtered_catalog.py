import gcsfs
from tqdm.autonotebook import tqdm
import pandas as pd
from retractions import query_retraction


# first get the total number of results
url = "https://esgf-data.dkrz.de/esg-search/search"
params = {
    "type": "Dataset",
    "mip_era": "CMIP6",
    "replica": "false",
    "distrib": "true",
    "retracted": "true",
    "format": "application/solr+json",
    "fields": "instance_id",
}

retracted_instance_ids = query_retraction(url, params)

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
