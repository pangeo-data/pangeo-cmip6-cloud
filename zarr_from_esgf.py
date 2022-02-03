import sys

from mysearch import esgf_search # We probably want to strip this out later, left as is for now.

DATASET_ID = sys.argv[1]

facet_labels = ("mip_era", "activity_id", "institute_id", "source_id", "experiment_id", "member_id", "table_id", "variable_id", "grid_label", "version")

facet_vals = DATASET_ID.split('.')
if len(facet_vals) != 10:
    raise ValueError(
        "Please specify a query of the form "
        '.'.join(facet_labels).upper()
    )

facets = dict(zip(facet_labels, facet_vals))

node_dict = {'llnl' : "https://esgf-node.llnl.gov/esg-search/search",
         'ipsl' : "https://esgf-node.ipsl.upmc.fr/esg-search/search",
         'ceda' : "https://esgf-index1.ceda.ac.uk/esg-search/search",
         'dkrz' : "https://esgf-data.dkrz.de/esg-search/search"}


search_node = 'llnl'
ESGF_site = node_dict[search_node] # TODO: We might have to be more clever here and search through different nodes. For later.


df = esgf_search(facets, server=ESGF_site) # this modifies the dict inside?

# get list of urls
urls = df['url'].tolist()
print(urls)
