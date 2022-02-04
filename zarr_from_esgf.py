import sys
import logging
import tempfile

from fsspec.implementations.local import LocalFileSystem
from pangeo_forge_recipes.storage import FSSpecTarget, CacheFSSpecTarget, MetadataTarget
from pangeo_forge_recipes.patterns import pattern_from_file_sequence
from pangeo_forge_recipes.recipes import XarrayZarrRecipe

from mysearch import (
    esgf_search,
)  # We probably want to strip this out later, left as is for now.

DATASET_ID = sys.argv[1]

# CMIP6.CMIP.CCCma.CanESM5.historical.r1i1p1f1.Omon.so.gn.v20190429
facet_labels = (
    "mip_era",
    "activity_id",
    "institution_id",
    "source_id",
    "experiment_id",
    "member_id",
    "table_id",
    "variable_id",
    "grid_label",
    "version",
)


facet_vals = DATASET_ID.split(".")
if len(facet_vals) != 10:
    raise ValueError(
        "Please specify a query of the form {"
        + ("}.{".join(facet_labels).upper())
        + "}"
    )

facets = dict(zip(facet_labels, facet_vals))

if facets["mip_era"] != "CMIP6":
    raise ValueError("Only CMIP6 mip_era supported")


# version is still not working
# if facets["version"].startswith("v"):
#    facets["version"] = facets["version"][1:]


node_dict = {
    "llnl": "https://esgf-node.llnl.gov/esg-search/search",
    "ipsl": "https://esgf-node.ipsl.upmc.fr/esg-search/search",
    "ceda": "https://esgf-index1.ceda.ac.uk/esg-search/search",
    "dkrz": "https://esgf-data.dkrz.de/esg-search/search",
}


# version doesn't work here
keep_facets = (
    "activity_id",
    "institution_id",
    "source_id",
    "experiment_id",
    "member_id",
    "table_id",
    "variable_id",
    "grid_label",
)
search_facets = {f: facets[f] for f in keep_facets}

search_node = "llnl"
ESGF_site = node_dict[
    search_node
]  # TODO: We might have to be more clever here and search through different nodes. For later.


df = esgf_search(search_facets, server=ESGF_site)  # this modifies the dict inside?

# get list of urls
urls = df["url"].tolist()

# sort urls in decending time order (to be able to pass them directly to the pangeo-forge recipe)
end_dates = [url.split("-")[-1].replace(".nc", "") for url in urls]
urls = [url for _, url in sorted(zip(end_dates, urls))]

# TODO Check that there are no gaps or duplicates.

pattern = pattern_from_file_sequence(urls, "time")

recipe = XarrayZarrRecipe(
    pattern,
    target_chunks={"time": 3},
    xarray_concat_kwargs={"join": "exact"},
)

fs_local = LocalFileSystem()

target_dir = tempfile.TemporaryDirectory().name + ".zarr"
target = FSSpecTarget(fs_local, target_dir)

cache_dir = tempfile.TemporaryDirectory()
cache_target = CacheFSSpecTarget(fs_local, cache_dir.name)

meta_dir = tempfile.TemporaryDirectory()
meta_store = MetadataTarget(fs_local, meta_dir.name)

recipe.target = target
recipe.input_cache = cache_target
recipe.metadata_cache = meta_store

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("pangeo_forge_recipes")
logger.setLevel(logging.INFO)

recipe.to_function()()

print(target_dir)
