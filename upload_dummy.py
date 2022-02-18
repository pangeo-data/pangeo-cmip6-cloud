import gcsfs
# these env variables are set via the google auth github action?
gcs = gcsfs.GCSFileSystem(project=os.environ["PROJECT_NAME"], bucket=os.environ["STORAGE_NAME"])
gcs.put_file('dummy.csv', 'cmip6/dummy.csv')
