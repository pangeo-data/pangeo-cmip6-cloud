# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import datetime

import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

project = "Pangeo CMIP6"
copyright = "2019-%s, Pangeo Community" % datetime.datetime.now().year
author = "Pangeo Community" 


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
  "sphinx_rtd_theme"
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

html_logo = "_static/small_e_logo.svg"
html_favicon = "_static/small_e_logo.svg"

html_theme = "sphinx_rtd_theme"
html_theme_options = {
  "collapse_navigation": False,
  "style_nav_header_background": "#00A3B0" # Pangeo teal
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
