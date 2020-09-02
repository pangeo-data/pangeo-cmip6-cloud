Cloud Data Overview
===================
Zarr Storage Format
-------------------
We have chosen the `Zarr object model and storage format <https://zarr.readthedocs.io/en/stable/>`_ for our cloud-based data repositories.
Each Zarr data store in the CMIP6 collection consists of all of the data, including the grids and metadata, stored in Zarr format.
This format stores the data as a collection of files consisting of regular text files containing metadata and data files consisting of the data divided into compressed chunks which can be read individually or in parallel, allowing very large datasets to scale more efficiently in the cloud.

The original datasets, stored in the WCRP/CMIP6 ESGF repositories, consists of `netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_ files.
Each of these datasets typically corresponds to a single variable saved at specified time intervals for the length of a single model run.
For convenience, these datasets were often divided into multiple netCDF files.
Our Zarr data stores correspond to the result of concatenating these netCDF files and then storing them as a single Zarr object.
All of the metadata in the original netCDF files has been preserved, including the licensing information and the CMIP6 persistent identifiers (``tracking_ids``) which are unique for each of the original netCDF files.

Directory Layout
----------------
To organize the data there is a list of keywords, each with a `controlled vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_ which has been developed over the many CMIP iterations.
The keywords categorize the model data in the many ways we might want to search the data.
For example, to find all available 3 hourly precipitation data from the pre-industrial control runs, we only need to specify the variable, frequency and experiment name.
The modeling centers all agreed to use the same keywords, each with its own controlled vocabulary.
In this case, the keywords ``['variable_id', 'table_id', 'experiment_id']`` will have the values ``['pr', '3hr', 'piControl']``.
The data are structured in this cloud repository using 8 of these keywords in this order:

.. code-block:: python

  cmip6/<activity_id>/<institution_id>/<source_id>/<experiment_id>/<member_id>/<table_id>/<variable_id>/<grid_label>/

Each object specified in this way refers to a single Zarr data store.

Structure of the CSV File
-----------------------------
A master spreadsheet of all available data is stored in a `simple CSV file <https://storage.googleapis.com/cmip6/pangeo-cmip6.csv>`_ in which the first line consists of the column names and each subsequent line specifies a Zarr data store.
The first 9 column names correspond to these 8 keywords, with an additional column for the URL of the Zarr data store.
The last column is included in the master spreadsheet for convenience when using the DCPP-type of experiments.
Here are the 10 columns:

.. code-block:: python

  activity_id  institution_id  source_id  experiment_id  member_id  table_id  variable_id  grid_label  zstore  dcpp_init_year

Although there are currently over 250,000 entries, this simple text file can be viewed in any spreadsheet application and the entries can be sorted, selected and discovered quickly and efficiently.
