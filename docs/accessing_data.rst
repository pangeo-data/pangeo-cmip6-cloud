Accessing data in the cloud
===========================
Manually searching the catalog
------------------------------
Because of its Zarr format, individual CMIP6 data stores can be accessed using `xarray <https://xarray.pydata.org/en/stable/>`_:

.. code-block:: python

  import fsspec
  import xarray as xr

  # create a mutable-mapping-style interface to the store
  mapper = fsspec.get_mapper("s3://cmip6-pds/CMIP/AS-RCEC/TaiESM1/1pctCO2/r1i1p1f1/Amon/hfls/gn/")
  # make sure to specify that metadata is consolidated
  ds = xr.open_zarr(mapper, consolidated=True)

By downloading the `CSV file <https://storage.cloud.google.com/cmip6/cmip6-zarr-consolidated-stores-noQC.csv>`_ enumerating all available data stores, we can interact with the spreadsheet through a `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ to search and explore for relevant data using the `CMIP6 controlled vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_:

.. code-block:: python

  import pandas as pd

  df = pd.read_csv("https://storage.cloud.google.com/cmip6/cmip6-zarr-consolidated-stores-noQC.csv")
  df.query("activity_id=='CMIP' & table_id == 'Amon' & variable_id == 'tas' & experiment_id == 'historical'")

From here, we can open any of the selected data stores using xarray, providing the value of the ``zstore`` column as input:

.. code-block:: python

  # get the path to a specific zarr store
  zstore = df_subset.zstore.values[-1]
  mapper = fsspec.get_mapper(zstore)
  # open using xarray
  ds = xr.open_zarr(mapper, consolidated=True)

When working with multiple data stores at the same time, it may be necessary to combine several together to form a dataset for analysis.
In these cases, it is easier to access them using an Earth System Model (ESM) collection with with `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_.
An ESM collection contains metadata describing how data stores can be combined to yield highly aggregated datasets, which is used by intake-esm to automatically merge/concatenate them when they are loaded into an xarray container.
This eases the burden on the user to manually combine data, while still offering the ability to search and explore all of the available data stores.

Loading an ESM collection
-------------------------
To load an Earth System Model (ESM) collection with `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_, the user must provide a valid ESM data catalog as input:

.. code-block:: python

  import intake

  col = intake.open_esm_datastore("https://cmip6-pds.s3-us-west-2.amazonaws.com/pangeo-cmip6.json")
  col

This gives a summary of the ESM collection, including the total number of Zarr data stores (referred to as assets), along with the total number of datasets these Zarr data stores correspond to.
The collection can also be viewed as a DataFrame:

.. code-block:: python

  col.df.head()

Searching for datasets
----------------------
After exploring the controlled vocabulary, it’s straightforward to get the data assets you want using intake-esm's ``search()`` method.
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
Once you've identified data assets of interest, you can load them into xarray dataset containers using intake-esm's ``to_dataset_dict()`` method.
Invoking this method yields a Python dictionary of high-level aggregated xarray datasets.
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
