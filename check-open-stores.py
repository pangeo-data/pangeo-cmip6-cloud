# make a python module out of this
from xmip.utils import google_cmip_col
import gcsfs
import xarray as xr
import dask.bag as db
from dask.diagnostics import ProgressBar

col = google_cmip_col()
stores = col.df['zstore'].tolist()

# for testing
stores = [s for s in stores if 'CanESM' in s and 'thetao' in s and 'ssp126' in s]


# Connect to Google Cloud Storage
filesystem = gcsfs.GCSFileSystem(token='anon', access='read_only')

def failcheck(store):
    mapper = filesystem.get_mapper(store)
    try:
        xr.open_dataset(mapper, engine='zarr', consolidated=True, use_cftime=True)
        return ('success', None)
    except Exception as e:
        return (store, e)
    
# b = db.from_sequence(stores, partition_size=25).map(failcheck)

# with ProgressBar():
#     b_computed = list(b)

b_computed = []
for s in stores:
    b_computed.append(failcheck(s))
    
# b = db.from_sequence(stores, partition_size=25).map(failcheck)

# with ProgressBar():
#     b_computed = list(b)
    
fails = [b for b in b_computed if b[0] != 'success']

with open('report.txt', 'a') as file:
    for fail in fails:
        file.write(f"{','.join([str(f) for f in fail])}\n")
