Pangeo CMIP6
============
This page will serve as a central hub for information on accessing and interacting with data from the Coupled Model Intercomparison Project Phase 6 (CMIP6) stored on Amazon Web Services (AWS) cloud storage, managed by Pangeo.
This data is formatted using `Zarr <https://zarr.readthedocs.io/en/stable/>`_, a cloud-optimized storage format.
Interaction with the data is done primarily through Python, using `intake <https://intake.readthedocs.io/en/stable/>`_, `intake-esm <https://intake-esm.readthedocs.io/en/stable/>`_, and `xarray <https://xarray.pydata.org/en/stable/>`_.

Background
----------
The Coupled Model Intercomparison Project (CMIP) is an international collaborative effort to improve the knowledge about climate change and its impacts on the Earth System and on our society.
`CMIP began in 1995 <https://www.wcrp-climate.org/wgcm-cmip>`_, and today we are in its sixth phase (CMIP6).
The CMIP6 data archive consists of data models created across approximately 30 working groups and 1,000 researchers investigating the urgent environmental problem of climate change, and will provide a wealth of information for the next Assessment Report (AR6) of the `Intergovernmental Panel on Climate Change <https://www.ipcc.ch/>`_ (IPCC).
As part of the `AWS Public Dataset Program <https://aws.amazon.com/opendata/public-datasets/>`_, this data will now be made available on AWS cloud storage.

Requirements
------------
Currently, the Zarr-formatted CMIP6 data is organized and accessed through an Earth System Model (ESM) collection, which can be opened and searched using intake-esm::

    import intake
    
    col = intake.open_esm_datastore('https://storage.googleapis.com/cmip6/pangeo-cmip6.json')
    col

Using intake-esm to open these datasets requires several other Python packages:

- intake, the base catalog package which intake-esm is a driver for
- xarray, which provides a container for the opened datasets
- zarr, to handle the backend of the individual datastores

Documentation
-------------
.. toctree::
   :maxdepth: 2

   overview
