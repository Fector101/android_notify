# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'android_notify'
copyright = '2026, Fector101'
author = 'Fector101'

# The full version, including alpha/beta/rc tags
release = '0.1'

# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# The theme to use for HTML and HTML Help pages.
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the built-in static files,
# so a file named "default.css" will use a custom stylesheet.
html_static_path = ['_static']
