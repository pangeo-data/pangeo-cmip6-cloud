import gcsfs
import pandas as pd

df_needed = pd.DataFrame()
df_GCS = pd.DataFrame()
fs = gcsfs.GCSFileSystem(token='anon',access='read_only',cache_timeout=-1)

#local_target_prefix = 'zarrs/'
local_target_prefix = '/h112/naomi/zarr-minimal/'
local_source_prefix = 'netcdfs/'

target_keys = ['activity_id','institution_id','source_id','experiment_id','member_id','table_id','variable_id','grid_label']
target_keys2 = ['activity_id','institution_id','source_id','experiment_id','member_id','table_id','variable_id','grid_label','version']

target_format = '%(' + ')s/%('.join(target_keys) + ')s'
target_format2 = '%(' + ')s/%('.join(target_keys2) + ')s'

#target_prefix1 = 'gs://cmip6/'
target_prefix2 = 'gs://cmip6/CMIP6/'

node_pref = {'esgf-data1.llnl.gov':0,'esgf-data2.llnl.gov':0,'aims3.llnl.gov':0,'esgdata.gfdl.noaa.gov':10,'esgf-data.ucar.edu':10,
 'dpesgf03.nccs.nasa.gov':5,'crd-esgf-drc.ec.gc.ca':6, 'cmip.bcc.cma.cn':10, 'cmip.dess.tsinghua.edu.cn':10,
 'cmip.fio.org.cn':10, 'dist.nmlab.snu.ac.kr':10, 'esg-cccr.tropmet.res.in':10, 'esg-dn1.nsc.liu.se':10,
 'esg-dn2.nsc.liu.se':10, 'esg.camscma.cn':10, 'esg.lasg.ac.cn':10, 'esg1.umr-cnrm.fr':10, 'esgf-cnr.hpc.cineca.it':10,
 'esgf-data2.diasjp.net':10, 'esgf-data3.ceda.ac.uk':10, 'esgf-data3.diasjp.net':10, 'esgf-nimscmip6.apcc21.org':10, 'esgf-node2.cmcc.it':10, 'esgf.bsc.es':10, 'esgf.dwd.de':10, 'esgf.ichec.ie':10, 'esgf.nci.org.au':10, 'esgf.rcec.sinica.edu.tw':10, 'esgf3.dkrz.de':10, 'noresg.nird.sigma2.no':10, 'polaris.pknu.ac.kr':10, 'vesg.ipsl.upmc.fr':10}


dtype = {'llnl' : "https://esgf-node.llnl.gov/esg-search/search",
         'ipsl' : "https://esgf-node.ipsl.upmc.fr/esg-search/search",
         'ceda' : "https://esgf-index1.ceda.ac.uk/esg-search/search",
         'dkrz' : "https://esgf-data.dkrz.de/esg-search/search"}

