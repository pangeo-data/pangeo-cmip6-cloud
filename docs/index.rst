Pangeo CMIP6
============
This page will serve as a central hub for information on accessing and interacting with data from the Coupled Model Intercomparison Project Phase 6 (CMIP6) in cloud storage, managed by `Pangeo <https://pangeo.io/>`_.
This data is formatted using `Zarr <https://zarr.readthedocs.io/en/stable/>`_, a cloud-optimized storage format.

Background
----------
The Coupled Model Intercomparison Project (CMIP) is an international collaborative effort to improve the knowledge about climate change and its impacts on the Earth System and on our society.
`CMIP began in 1995 <https://www.wcrp-climate.org/wgcm-cmip>`_, and is currently in its sixth phase (CMIP6).
The CMIP6 data archive consists of data models created across approximately 30 working groups and 1,000 researchers investigating the urgent environmental problem of climate change, and will provide a wealth of information for the next Assessment Report (AR6) of the `Intergovernmental Panel on Climate Change <https://www.ipcc.ch/>`_ (IPCC).
As part of `Google Cloud Public Datasets <https://cloud.google.com/public-datasets>`_ and the `AWS Open Data Sponsorship Program <https://aws.amazon.com/opendata/public-datasets/>`_, this data is now available on Google Cloud and Amazon S3 storage.

Requirements
------------
First and foremost, a Zarr package is required to interact with the data stores.
Listed below are languages with actively developed Zarr packages; italicized languages do not yet have Zarr packages that support the reading of remote data stores:

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

Documentation
-------------
.. toctree::
   :maxdepth: 2

   overview
   accessing_data
   pangeo_catalog
