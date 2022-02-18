import os
import gcsfs
# these env variables are set via the google auth github action?
gcs = gcsfs.GCSFileSystem(project='gcp-public-data-noaa-cmip6', bucket='cmip6')
gcs.put_file('dummy.csv', 'cmip6/dummy.csv')
