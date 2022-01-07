Zarr Data Overview
==================

Requirements
------------
First and foremost, a Zarr package is required to interact with the data stores.
Listed below are languages with actively developed Zarr packages; bolded languages do not yet have Zarr packages that support the reading of remote data stores:

- Python: `zarr-developers/zarr-python <https://github.com/zarr-developers/zarr-python>`_
- TypeScript: `gzuidhof/zarr.js <https://github.com/gzuidhof/zarr.js/>`_
- **C++**: `constantinpape/z5 <https://github.com/constantinpape/z5>`_
- Julia: `meggart/zarr.jl <https://github.com/meggart/Zarr.jl>`_
- **Java**: `saalfeldlab/n5-zarr <https://github.com/saalfeldlab/n5-zarr>`_
- Scala: `lasersonlab/ndarray.scala <https://github.com/lasersonlab/ndarray.scala>`_
- C: `Unidata/netcdf-c/libnczarr <https://github.com/Unidata/netcdf-c/tree/master/libnczarr>`_

Additionally, a filesystem package for Google Cloud and/or S3 storage is required for some languages to access the files containing the data stores:

- Python: `gcsfs <https://gcsfs.readthedocs.io/en/latest/>`_ or `s3fs <https://s3fs.readthedocs.io/en/latest/>`_
- Julia: `AWSCore <https://github.com/JuliaCloud/AWSCore.jl>`_

Though optional, a CSV-loading package allows for searching and filtering of the Zarr data stores, which are enumerated in CSV files located at the root of each cloud storage bucket.
Python users are encouraged to use `xarray <https://xarray.pydata.org/en/stable/>`_, `intake <https://intake.readthedocs.io/en/stable/>`_, and `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_, which facilitate exploration and interaction with the data through the use of Earth System Model (ESM) collection specifications which are also provided at the root of each bucket.

Data Locations
--------------

CMIP6 data in the cloud can be found in both Google Cloud and AWS S3 storage buckets:

- ``gs://cmip6`` (part of `Google Cloud Public Datasets <https://cloud.google.com/public-datasets>`_)
- ``s3://cmip6-pds`` (part of the `AWS Open Data Sponsorship Program <https://aws.amazon.com/opendata/public-datasets/>`_)

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
**UPDATE: Feb. 1, 2021:** Please note that our zarr store names, and therefore the URLs for our zarr stores,  has recently changed. For example, the prefix is now ``gs://cmip6/CMIP6/`` on GC and ``s3://cmip6-pds/CMIP6/`` on AWS S3. In addition, conforming to the ESGF syntax, we have appended the ``version_id`` (e.g., /v20200101) to the names.

To organize the data there is a list of keywords, each with a `controlled vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_ which has been developed over the many CMIP iterations.
The keywords categorize the model data in the many ways we might want to search the data.
For example, to find all available 3-hourly precipitation data from the pre-industrial control runs, we only need to specify the variable, frequency and experiment name.
In this case, the keywords ``['variable_id', 'table_id', 'experiment_id']`` will have the values ``['pr', '3hr', 'piControl']``.
The data are now structured in this cloud repository using 9 of these keywords in this order::

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
We maintain CSV files listing the most recent versions of the Zarr data stores, providing the keyword values in columns as well as the dataset URLs and some additional information.  These files allow for rapid searching by keyword using your favorite spreadsheet software.  For example, in python, we generally use the `pandas` package.

There are two different master CSV files located at the root of the buckets; one contains only datasets with no serious issues listed in the official `ESGF Errata Service <https://errata.es-doc.org/static/index.html>`_:

- https://storage.googleapis.com/cmip6/pangeo-cmip6.csv
- https://cmip6-pds.s3-us-west-2.amazonaws.com/pangeo-cmip6.csv

And the other contains all available Zarr data stores, including those with serious issues (represented with a ``-noQC`` label):

- https://storage.googleapis.com/cmip6/pangeo-cmip6-noQC.csv
- https://cmip6-pds.s3-us-west-2.amazonaws.com/pangeo-cmip6-noQC.csv

For backward compatibility on GCS, we also maintain redundant copies called "cmip6-zarr-consolidated-stores.csv" and "cmip6-zarr-consolidated-stores-noQC.csv".

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

There are currently over 400,000 entries - which is too large for Google Spreadsheets, but can be viewed in most standard spreadsheet applications and the entries can be sorted, selected and discovered quickly and efficiently.  We find that importing them as a python ``pandas`` dataframe is very useful.

NetCDF Data Overview
==================

Data locations
-------------------------------

CMIP6 netcdf data in the cloud can be found in AWS S3 storage. 

- ``s3://esgf-world`` (part of the `AWS Open Data Sponsorship Program <https://aws.amazon.com/opendata/`_public-datasets/>`_). 

The data is in NetCDF format, with a predetermined and well-defined directory structure to ensure that it is properly organized and classified. This directory structure is reflected in the CSV files located `here <https://cmip6-nc.s3.amazonaws.com/esgf-world.csv.gz>`_, which enumerates all available netcdf datasets using their containing directory names as columns to allow for sorting and filtering.The names of the columns adhere to the CMIP6 controlled vocabulary whenever  available. One can use the ` AWS S3 explorer <https://esgf-world.s3.amazonaws.com/index.html>`_ to quickly explore these data holdings. 

These datasets are also linked from the `AWS registry of open data on AWS <https://registry.opendata.aws/cmip6/>`_.

Directory structure 
-------------------

The directory structure (or the prefixes) adhere to the CMIP6 Data Reference Syntax and CMIP6 Controlled Vocabulary to facilitate building of automated tools to build data catalogs and other utilities to aid in data analysis. 

Here is an example: ``s3://esgf-world/CMIP6/AerChemMIP/NOAA-GFDL/GFDL-ESM4/hist-piNTCF/r1i1p1f1/Amon/tas/gr1/v20180701/tas_Amon_GFDL-ESM4_hist-piNTCF_r1i1p1f1_gr1_185001-194912.nc`` (appears as the column path in the CSV file located `here <https://cmip6-nc.s3.amazonaws.com/esgf-world.csv.gz>`_)

where: 

- ``esgf-world`` is the name of the S3 bucket with CMIP6 NetCDF holdings (subset) 
- ``CMIP6`` is the project_id
- ``AerChemMIP`` is the name of the MIP (Model Intercomparison Project) 
- ``NOAA-GFDL`` is the institution_id 
- ``GFDL-ESM4`` is the source_id (i.e., the model)
- ``hist-piNTCF`` is the experiment_id
- ``r1i1p1f1`` is the member_id (i.e ensemble member. r,i,p stand for realization, initiatialization, physics, forcing respectively)
- ``Amon`` is the table_id (i.e. the MIP table. Amon stands for atmos monthly)
- ``tas`` is the variable_id 
- ``gr1`` is the grid_label (in this example, r in "gr1" stands for regridded)
- ``v20180701`` is the version_id
- ``tas_Amon_GFDL-ESM4_hist-piNTCF_r1i1p1f1_gr1_185001-194912.nc`` is the file_name

More CMIP6 netcdf data is being added incrementally to the S3 storage bucket, through a cloud based experimental Earth System Grid Federation (ESGF) node. 

CSV File Structure 
-------------------

The `CSV file <https://cmip6-nc.s3.amazonaws.com/esgf-world.csv.gz>`_), also known as the intake-esm catalog is a  CSV file listing the netcdf objects in the esgf-world bucket, providing the keyword values in columns as well as the dataset URLs and some additional information. The column names use CMIP6 controlled vocabulary as indicated in the section above. These files allow for rapid searching by keyword using your favorite spreadsheet software. For example, in python, we generally use the pandas package. If you'd like to use them in your data analysis directly, you can also leverage xarray and dask. An example can be found `here <https://github.com/aradhakrishnanGFDL/gfdl-aws-analysis/blob/community/examples/intake-esm-s3-nc-simple-access.ipynb>`_. 






