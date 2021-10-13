Accessing data in the cloud
===========================
Once the master CSV file is understood, accessing data is a matter of searching for relevant datasets using the controlled vocabulary and opening them by pointing your Zarr package of choice to their corresponding ``zstore`` URLs.
While this can be done using any language whose Zarr package supports the reading of remote data stores, the following examples will be in Python, showcasing the use of `xarray <https://xarray.pydata.org/en/stable/>`_, `intake <https://intake.readthedocs.io/en/stable/>`_, and `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_ to open and explore Earth System Model (ESM) collections of the CMIP6 data.

Opening a single Zarr data store
--------------------------------
A standalone Zarr data store can be opened using xarray's ``open_zarr()`` function.
The function takes a Python-native ``MutableMapping`` as input, which can be acquired from a Zarr store URL using either `gcsfs <https://gcsfs.readthedocs.io/en/latest/>`_ or `s3fs <https://s3fs.readthedocs.io/en/latest/>`_, depending on the cloud provider:

.. code-block:: python

  import gcsfs
  import xarray as xr
  
  # Connect to Google Cloud Storage
  fs = gcsfs.GCSFileSystem(token='anon', access='read_only')
  
  # create a MutableMapping from a store URL  
  mapper = fs.get_mapper("gs://cmip6/CMIP6/CMIP/AS-RCEC/TaiESM1/1pctCO2/r1i1p1f1/Amon/hfls/gn/v20200225/")
  
  # make sure to specify that metadata is consolidated
  ds = xr.open_zarr(mapper, consolidated=True)

or, for the AWS datasets:

.. code-block:: python

  import s3fs
  import xarray as xr

  # Connect to AWS S3 storage
  fs = s3fs.S3FileSystem(anon=True)

  # create a MutableMapping from a store URL  
  mapper = fs.get_mapper("s3://cmip6-pds/CMIP6/CMIP/AS-RCEC/TaiESM1/1pctCO2/r1i1p1f1/Amon/hfls/gn/v20200225/")

  # make sure to specify that metadata is consolidated
  ds = xr.open_zarr(mapper, consolidated=True)

Notice the option ``consolidated=True``, which relies on a consolidated metadata file to open and describe the Zarr data store with minimal data egress.

Manually searching the catalog
------------------------------
By downloading the master CSV file enumerating all available data stores, we can interact with the spreadsheet through a `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ to search and explore for relevant data using the `CMIP6 controlled vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_:

.. code-block:: python

  import pandas as pd

  # for Google Cloud:
  df = pd.read_csv("https://cmip6.storage.googleapis.com/pangeo-cmip6.csv")
  # for AWS S3:
  # df = pd.read_csv("https://cmip6-pds.s3.amazonaws.com/pangeo-cmip6.csv")
  
  df_subset = df.query("activity_id=='CMIP' & table_id=='Amon' & variable_id=='tas'")

From here, we can open any of the selected data stores using xarray, providing the value of the ``zstore`` column as input:

.. code-block:: python

  # get the path to a specific zarr store
  zstore = df_subset.zstore.values[-1]
  mapper = fs.get_mapper(zstore)
  
  # open using xarray
  ds = xr.open_zarr(mapper, consolidated=True)

When working with multiple data stores at the same time, it may be necessary to combine several together to form a dataset for analysis.
In these cases, it is easier to access them using an ESM collection with intake-esm.
An ESM collection contains metadata describing how data stores can be combined to yield highly aggregated datasets, which is used by intake-esm to automatically merge/concatenate them when they are loaded into an xarray container.
This eases the burden on the user to manually combine data, while still offering the ability to search and explore all of the available data stores.

Loading an ESM collection
-------------------------
To load an ESM collection with intake-esm, the user must provide a valid ESM collection specification as input to intake's ``open_esm_datastore()`` function:

.. code-block:: python

  import intake

  # for Google Cloud:
  col = intake.open_esm_datastore("https://storage.googleapis.com/cmip6/pangeo-cmip6.json")
  # for AWS S3:
  #col = intake.open_esm_datastore("https://cmip6-pds.s3.amazonaws.com/pangeo-cmip6.json")
  
  col

This gives a summary of the ESM collection, including the total number of Zarr data stores (referred to as assets), along with the total number of datasets these Zarr data stores correspond to.
The collection can also be viewed as a DataFrame:

.. code-block:: python

  col.df.head()

Searching for datasets
----------------------
After exploring the controlled vocabulary, it’s straightforward to get the data assets you want using intake-esm's ``search()`` function.
In the example below, we will search for the following:

- variables: ``tas`` which stands for near-surface air temperature
- experiments: ``["historical", "ssp245", "ssp585"]``:

  - ``historical``: all forcing of the recent past
  - ``ssp245``: update of `RCP4.5 <https://en.wikipedia.org/wiki/Representative_Concentration_Pathway>`_ based on SSP2
  - ``ssp585``: emission-driven `RCP8.5 <https://en.wikipedia.org/wiki/Representative_Concentration_Pathway>`_ based on SSP5

- table ID: ``Amon`` which stands for monthly atmospheric data
- grid label: ``gr`` which stands for regridded data reported on the data provider's preferred target grid

.. code-block:: python

  # form query dictionary
  query = dict(experiment_id=['historical', 'ssp245', 'ssp585'],
               table_id='Amon',
               variable_id=['tas'],
               member_id = 'r1i1p1f1',
               grid_label='gr')
  # subset catalog and get some metrics grouped by 'source_id'
  col_subset = col.search(require_all_on=['source_id'], **query)
  col_subset.df.groupby('source_id')[['experiment_id', 'variable_id', 'table_id']].nunique()

Loading datasets
----------------
Once you've identified data assets of interest, you can load them into xarray dataset containers using intake-esm's ``to_dataset_dict()`` function.
Invoking this function yields a Python dictionary of high-level aggregated xarray datasets.
The logic for merging/concatenating the query results into datasets is provided in the input JSON file, under ``aggregation_control``:

.. code-block:: json

  "aggregation_control": {
    "variable_column_name": "variable_id",
    "groupby_attrs": [
      "activity_id",
      "institution_id",
      "source_id",
      "experiment_id",
      "table_id",
      "grid_label"
    ],
    "aggregations": [{
        "type": "union",
        "attribute_name": "variable_id"
      },

      {
        "type": "join_new",
        "attribute_name": "member_id",
        "options": {
          "coords": "minimal",
          "compat": "override"
        }
      },
      {
        "type": "join_new",
        "attribute_name": "dcpp_init_year",
        "options": {
          "coords": "minimal",
          "compat": "override"
        }
      }
    ]
  }

Though these aggregation specifications are sufficient to merge individual data assets into xarray datasets, sometimes additional arguments must be provided depending on the format of the data assets.
For example, Zarr-based assets can be loaded with the option ``consolidated=True``, which relies on a consolidated metadata file to describe the assets with minimal data egress:

.. code-block:: python

  dsets = col_subset.to_dataset_dict(zarr_kwargs={'consolidated': True},
                                     storage_options={'token': 'anon'})
  # list all merged datasets
  [key for key in dsets.keys()]

When the datasets have finished loading, we can extract any of them like we would a value in a Python dictionary:

.. code-block:: python

  ds = dsets['ScenarioMIP.THU.CIESM.ssp585.Amon.gr']
  ds

Preprocessing the CMIP6 datasets
--------------------------------
Once you are comfortable with the basic `intake-esm` features, you may notice that many datasets cannot be easily combined and manipulated without some time consuming debugging. Julius Busecke's very useful package, `cmip6_preprocessing <https://github.com/jbusecke/cmip6_preprocessing/>`_, can be added which does some of this cleanup for you - especially for the very tricky 'Omon' datasets. See, for example, this `tutorial <https://github.com/jbusecke/cmip6_preprocessing/blob/HEAD/docs/tutorial.ipynb>`_ .

.. code-block:: python

  from cmip6_preprocessing.preprocessing import combined_preprocessing

and then you can use this when calling ``to_dataset_dict``:

.. code-block:: python

  dsets = col_subset.to_dataset_dict(
    zarr_kwargs={'consolidated': True, 'decode_times':False}, 
    aggregate=True,
    preprocess=combined_preprocessing,
    storage_options={'token': 'anon'}
  )
  # AWS needs a slightly different syntax for the storage options
  dsets = col_subset.to_dataset_dict(
    zarr_kwargs={'consolidated': True, 'decode_times':False}, 
    aggregate=True,
    preprocess=combined_preprocessing,
    storage_options={'anon': 'True'}
  )
