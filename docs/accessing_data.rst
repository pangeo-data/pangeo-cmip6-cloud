Accessing Data in The Cloud
===========================
Because of its Zarr format, individual CMIP6 data stores can be accessed using `xarray <https://xarray.pydata.org/en/stable/>`_::

  import fsspec
  import xarray as xr

  path = fsspec.get_mapper("s3://cmip6-pds/CMIP/AS-RCEC/TaiESM1/1pctCO2/r1i1p1f1/Amon/hfls/gn/") # gs://cmip6 for data on GCS
  ds = xr.open_zarr(path, consolidated=True) # make sure to specify that metadata is consolidated

However, when working with multiple data stores at the same time, it is easier to access them using an Earth System Model (ESM) collection with with `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_.
This allows the thousands of data stores to be searched and explored using the `CMIP6 controlled vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_.
When all relevant data stores have been discovered, they can then be merged and opening into an xarray container automatically, using information specified by the ESM collection.

Loading An ESM Collection
-------------------------
To load an Earth System Model (ESM) collection with `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_, the user must provide a valid ESM data catalog as input::

  import intake

  col = intake.open_esm_datastore("https://cmip6-pds.s3-us-west-2.amazonaws.com/pangeo-cmip6.json")
  col

This gives a summary of the ESM collection, including the total number of Zarr data stores (referred to as assets), along with the total number of datasets these Zarr data stores correspond to.
The collection can also be viewed as a `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_::

  col.df.head()

Searching For Datasets
----------------------
After exploring the controlled vocabulary, it’s straightforward to get the data assets you want using intake-esm's ``search()`` method.
In the example below, we will search for the following:

- variables: ``tas`` which stands for near-surface air temperature
- experiments: ``["historical", "ssp245", "ssp585"]``:

  - ``historical``: all forcing of the recent past
  - ``ssp245``: update of `RCP4.5 <https://en.wikipedia.org/wiki/Representative_Concentration_Pathway>`_ based on SSP2
  - ``ssp585``: emission-driven `RCP8.5 <https://en.wikipedia.org/wiki/Representative_Concentration_Pathway>`_ based on SSP5

- table ID: ``Amon`` which stands for monthly atmospheric data
- grid label: ``gr`` which stands for regridded data reported on the data provider's preferred target grid::
  
  # form query dictionary
  query = dict(experiment_id=['historical', 'ssp245', 'ssp585'],
               table_id='Amon',
               variable_id=['tas'],
               member_id = 'r1i1p1f1',
               grid_label='gr')

  # subset catalog and get some metrics grouped by 'source_id'
  col_subset = col.search(require_all_on=['source_id'], **query)
  col_subset.df.groupby('source_id')[['experiment_id', 'variable_id', 'table_id']].nunique()

Loading Datasets
----------------
Once you've identified data assets of interest, you can load them into xarray dataset containers using intake-esm's ``to_dataset_dict()`` method.
Invoking this method yields a Python dictionary of high-level aggregated xarray datasets.
The logic for merging/concatenating the query results into datasets is provided in the input JSON file, under ``aggregation_control``::

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
For example, Zarr-based assets can be loaded with the option ``consolidated=True``, which relies on a consolidated metadata file to describe the assets with minimal data egress::

  dsets = col_subset.to_dataset_dict(zarr_kwargs={'consolidated': True}, storage_options={'token': 'anon'})

  # list all merged datasets
  [key for key in dsets.keys()]

When the datasets have finished loading, we can extract any of them like we would a value in a Python dictionary::

  ds = dsets['ScenarioMIP.THU.CIESM.ssp585.Amon.gr']
  ds
