import os
import gcsfs
# these env variables are set via the google auth github action?
gcs = gcsfs.GCSFileSystem()
gcs.put_file('dummy.csv', 'cmip6/dummy.csv')
