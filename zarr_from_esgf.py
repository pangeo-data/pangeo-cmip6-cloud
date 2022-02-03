from mysearch import esgf_search # We probably want to strip this out later, left as is for now.

node_dict = {'llnl' : "https://esgf-node.llnl.gov/esg-search/search",
         'ipsl' : "https://esgf-node.ipsl.upmc.fr/esg-search/search",
         'ceda' : "https://esgf-index1.ceda.ac.uk/esg-search/search",
         'dkrz' : "https://esgf-data.dkrz.de/esg-search/search"}


facet_dict = {
                'table_id'      : 'Omon',
                'activity_id'   : 'CMIP',
                'experiment_id' : 'historical',
                'variable_id'   : "so", 
                'member_id'     : 'r1i1p1f1',
                'source_id'     : 'CanESM5',
                'grid_label'    : 'gn',
            }

search_node = 'llnl'
ESGF_site = node_dict[search_node] # TODO: We might have to be more clever here and search through different nodes. For later.


query_dict = {k:v for k,v in facet_dict.items()}
df = esgf_search(facet_dict, server=ESGF_site) # this modifies the dict inside?

# get list of urls
urls = df['url'].tolist()
print(urls)