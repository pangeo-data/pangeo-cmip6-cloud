# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import datetime

# -- Project information -----------------------------------------------------

project = "Pangeo / ESGF Cloud Data Working Group"
copyright = "2019-%s, Pangeo Community" % datetime.datetime.now().year
author = "Pangeo Community"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinxext.opengraph",
    #"myst_nb",
    #"sphinx.ext.autodoc",
    #"sphinx.ext.extlinks",
    # "numpydoc",
    #"sphinx_autodoc_typehints",
    #"sphinx_copybutton",
]



# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
pygments_style = "sphinx"

html_logo = "_static/small_e_logo_cropped.png"
html_favicon = "_static/favicon.png"

html_theme = "pangeo_sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/pangeo-data/pangeo-cmip6-cloud",
    "repository_branch": "master",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
