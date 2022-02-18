import gcsfs
gcs = gcsfs.GCSFileSystem()
gcs.put_file('dummy.csv', 'cmip6/dummy.csv')