Cloud data overview
===================
CMIP6 data in the cloud can be found in both Google Cloud and S3 storage buckets:

- ``gs://cmip6``
- ``s3://cmip6-pds``

The data is primarily `Zarr <https://zarr.readthedocs.io/en/stable/>`_-formatted, with a predetermined and well-defined directory structure to ensure that it is properly organized and classified.
This directory structure is reflected in the master CSV files located at the root of each bucket, which enumerates all available Zarr stores using their containing directory names as columns to allow for sorting and filtering.

Zarr storage format
-------------------
Each data store in the CMIP6 collection consists of all of the data, including the grids and metadata, stored in Zarr format.
This format stores the data as a collection of files consisting of regular text files containing metadata and data files consisting of the data divided into compressed chunks which can be read individually or in parallel, allowing very large datasets to scale more efficiently in the cloud.

The original datasets, stored in the WCRP/CMIP6 ESGF repositories, consist of `netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_ files.
Each of these datasets typically corresponds to a single variable saved at specified time intervals for the length of a single model run.
For convenience, these datasets were often divided into multiple netCDF files.
Our Zarr data stores correspond to the result of concatenating these netCDF files and then storing them as a single Zarr object.
All of the metadata in the original netCDF files has been preserved, including the licensing information and the CMIP6 persistent identifiers (``tracking_ids``) which are unique for each of the original netCDF files. 

A Zarr data store ``tracking_id`` consists of a concatenated list of the netCDF ``tracking_ids`` from which it was created. An individual ``tracking_id`` can be looked up at `Handle.net <http://hdl.handle.net/>`_  (e.g., enter "hdl:21.14100/33cbdc29-fbc9-44ab-9e09-5dc7824441cf", which then redirects `here <https://handle-esgf.dkrz.de/lp/21.14100/33cbdc29-fbc9-44ab-9e09-5dc7824441cf/>`_).

Directory structure
-------------------
To organize the data there is a list of keywords, each with a `controlled vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_ which has been developed over the many CMIP iterations.
The keywords categorize the model data in the many ways we might want to search the data.
For example, to find all available 3-hourly precipitation data from the pre-industrial control runs, we only need to specify the variable, frequency and experiment name.
In this case, the keywords ``['variable_id', 'table_id', 'experiment_id']`` will have the values ``['pr', '3hr', 'piControl']``.
The data are structured in this cloud repository using 9 of these keywords in this order::

  cmip6[-pds]/CMIP6/
  └──<activity_id>/
      └──<institution_id>/
          └──<source_id>/
              └──<experiment_id>/
                  └──<member_id>/
                      └──<table_id>/
                          └──<variable_id>/
                              └──<grid_label>/
                                  └──<version_id>/

Each object specified in this way refers to a single Zarr data store.

CSV file structure
------------------
There are two different master CSV files enumerating available Zarr data stores located at the root of each bucket; one contains only datasets with no serious issues listed in the official `ESGF Errata Service <https://errata.es-doc.org/static/index.html>`_:

- https://storage.googleapis.com/cmip6/pangeo-cmip6.csv
- https://cmip6-pds.s3-us-west-2.amazonaws.com/pangeo-cmip6.csv

The other contains all available Zarr data stores, including those with serious issues (represented with a ``-noQC`` label):

- https://storage.googleapis.com/cmip6/pangeo-cmip6-noQC.csv
- https://cmip6-pds.s3-us-west-2.amazonaws.com/pangeo-cmip6-noQC.csv

The first 8 column names correspond to the standard CMIP keywords; the next three additional columns are:

- ``zstore``: URL of the corresponding Zarr data store
- ``dcpp_init_year``: optional metadata for convenience when accessing `DCPP <https://www.wcrp-climate.org/dcp-overview>`_-type experiments
- ``version``: approximate data of model output file as listed on ESGF in YYYYMMDD format

Finally, the ``-noQC`` variants exclusively include three additional columns:

- ``status``: status of the dataset's issue, if any, using a controlled vocabulary:

  - ``new``: issue has been recently raised with no other updates to status
  - ``onhold``: issue is in the process of being examined or resolved
  - ``resolved``: issue has been resolved AND the corrected files have been published on ESGF with a new dataset version
  - ``wontfix``: issue cannot/won’t be fixed by the data provider; may result in a persistent low severity issue with no consequences to analysis

- ``severity``: severity of the dataset's issue, if any, using a controlled vocabulary:

  - ``low``: issue concerns file management (e.g., addition, removal, period extension, etc.)
  - ``medium``: issue concerns metadata (netCDF attributes) without undermining the values of the involved variable
  - ``high``: issue concerns single point variable or axis values
  - ``critical``: issue concerns the variable or axis values undermining the analysis; use of this data is strongly discouraged

- ``issue_url``: link to view the issue on ESGF Errata Service

Although there are currently over 400,000 entries, these files can be viewed in any spreadsheet application and the entries can be sorted, selected and discovered quickly and efficiently.
