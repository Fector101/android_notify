"""Configuration file for the Sphinx documentation builder."""

import os
import sys

sys.path.insert(0, os.path.abspath('../'))   # noqa: E402
sys.path.insert(0, os.path.abspath('_ext'))  # noqa: E402

import android_notify.config  # noqa: E402

# -- Project information -----------------------------------------------------

project = "Android-Notify"
author = "Fabian (Fector101)"
copyright = "2026, Fabian (Fector101)"
release = android_notify.config.__version__
version = android_notify.config.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
    "pydroid_tabs",
    "seo_meta",
]

# Modules that require Android/pyjnius are mocked so docs build on Linux.
autodoc_mock_imports = ["jnius"]

# MyST (Markdown) parser options
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
]
myst_heading_anchors = 3

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "imgs", "old-README.md"]

# The master toctree document.
master_doc = "index"

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = f"{project} {release}"

# Canonical URL: each version's page points at the same page on the default
# version, so Google does not treat latest/stable/vX.Y.Z as duplicates.
html_baseurl = os.environ.get(
    "READTHEDOCS_CANONICAL_URL",
    "https://android-notify.readthedocs.io/en/latest/",
)