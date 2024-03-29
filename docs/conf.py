# -*- coding: utf-8 -*-
#
# napalm-logs documentation build configuration file, created by
# sphinx-quickstart on Wed Aug  9 16:31:45 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import json
import logging

# Import third party libs
import jinja2

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("_themes"))

import napalm_logs  # noqa
from napalm_logs.base import NapalmLogs  # noqa

log = logging.getLogger(__name__)

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "napalm-logs"
copyright = "2017-2019, Mircea Ulinic"
author = "Mircea Ulinic"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# version = napalm_logs.__version__
# The full version, including alpha/beta/rc tags.
# release = napalm_logs.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "flask_theme_support.FlaskyStyle"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "show_powered_by": False,
    "github_user": "napalm-automation",
    "github_repo": "napalm-logs",
    "github_banner": True,
    "show_related": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "links.html",
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
        "donate.html",
    ]
}

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "napalm-logsdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "napalm-logs.tex",
        "napalm-logs Documentation",
        "Mircea Ulinic",
        "manual",
    ),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "napalm-logs", "napalm-logs Documentation", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "napalm-logs",
        "napalm-logs Documentation",
        author,
        "napalm-logs",
        (
            "napalm-logs is a Python library that listens to syslog messages from network devices and returns strucuted data"
            "following the OpenConfig or IETF YANG models"
        ),
        "Miscellaneous",
    ),
]

# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


def gen_messages_rst():
    # Commenting out the next section,
    #   will revisit later if really worth testing before generating the docs.
    # ----------------
    # report_rel_path = '../report.json'
    # if not os.path.isfile(report_rel_path):
    #     raise IOError('No report.json generated.')
    # with open(report_rel_path, 'r') as report_fh:
    #     report_dict = json.loads(report_fh.read())
    # passed_tests = False
    # for data in report_dict['data']:
    #     if data['type'] == 'report':
    #         passed_tests = data['attributes']['summary'].get('failed', 0) == 0
    # if passed_tests:
    #     raise AssertionError('Didnt pass the tests, not generating doc')
    # ----------------
    # Start building the docs.
    # Firstly load the messages config, by creating an instance
    #   of the base NapalmLogs class, without starting the engine.
    nl_ = NapalmLogs(publisher=[])
    defined_errors = {}
    for os_name, os_cfg in nl_.config_dict.items():
        for message in os_cfg["messages"]:
            error_name = message["error"]
            if error_name not in defined_errors:
                defined_errors[error_name] = {"doc": "", "os": [], "model": ""}
            if not defined_errors[error_name]["doc"] or len(
                defined_errors[error_name]["doc"]
            ) < len(message["__doc__"]):
                defined_errors[error_name]["doc"] = message["__doc__"]
            if not defined_errors[error_name]["model"]:
                defined_errors[error_name]["model"] = message["model"]
            defined_errors[error_name]["os"].append(os_name)
    # The collect the mock data from the tests:
    cwd = os.path.dirname(__file__)
    test_root_path = os.path.join(cwd, "..", "tests", "config")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    for error_name, error_details in defined_errors.items():
        os_name = error_details["os"][0]  # Picking up the first OS in the list.
        error_path = os.path.join(test_root_path, os_name, error_name)
        test_cases = [
            name
            for name in os.listdir(error_path)
            if os.path.isdir(os.path.join(error_path, name))
        ]
        test_case_name = (
            "default" if "default" in test_cases else test_cases[0]
        )  # Picking up a test case.
        test_case_path = os.path.join(error_path, test_case_name)
        raw_message_filepath = os.path.join(test_case_path, "syslog.msg")
        log.debug("Looking for %s", raw_message_filepath)
        assert os.path.isfile(raw_message_filepath)
        with open(raw_message_filepath, "r") as raw_message_fh:
            raw_message = raw_message_fh.read()
        log.debug("Read raw message:")
        log.debug(raw_message)
        yang_message_filepath = os.path.join(test_case_path, "yang.json")
        log.debug("Looking for %s", yang_message_filepath)
        assert os.path.isfile(yang_message_filepath)
        with open(yang_message_filepath, "r") as yang_message_fh:
            yang_message = yang_message_fh.read()
        log.debug("Read YANG text:")
        log.debug(yang_message)
        struct_yang_message = json.loads(yang_message)
        indented_yang_message = json.dumps(
            struct_yang_message, indent=4, sort_keys=True
        )
        log.debug("Struct YANG message:")
        log.debug(struct_yang_message)
        msg_template = env.get_template("message_template.jinja")
        rendered_template = msg_template.render(
            error_name=error_name,
            error_doc=error_details["doc"],
            error_yang=error_details["model"],
            error_os_list=list(set(error_details["os"])),
            error_txt_example=raw_message.strip(),
            error_json_example=indented_yang_message.replace("\n}", "\n  }"),
        )
        message_rst_path = "messages/{error_name}.rst".format(error_name=error_name)
        with open(message_rst_path, "w") as rst_fh:
            rst_fh.write(rendered_template)
    index_tpl_file = env.get_template("messages_index_template.jinja")
    messages_list = list(defined_errors.keys())
    messages_list.extend(["RAW", "UNKNOWN"])
    messages_list.sort()
    rendered_template = index_tpl_file.render(error_list=messages_list)
    with open("messages/index.rst", "w") as index_fh:
        index_fh.write(rendered_template)


gen_messages_rst()
