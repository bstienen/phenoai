""" Functions to check for updates of PhenoAI and AInalyses

This module implements functions to check for updates of the PhenoAI package
and individual AInalyses (if downloaded from the official PhenoAI website).
This is done by sending an HTTP request to the PhenoAI server API. Returned
information is automatically formatted in such a way that it is usable in
Python.

All functions in this module are already implemented in various parts of the
PhenoAI package. In normal circumstances the user should not need to call any
of the functions in this module him- or herself.

.. attention:: None of the functions in this module install anything
    automatically. This module is merely an update checker. Any updating has
    to be initiated manually by the user.
"""

import sys
import importlib
from math import floor
import requests
import json

from phenoai.__version__ import __apiurl__, __version__
from phenoai import logger


def check_ainalysis_update(uniquedbid, version):
    """ Check if there is a new version available for an AInalysis

    Checks if a new version is available on the PhenoAI server for the
    AInalysis with provided unique database ID. Versions are automatically
    checked for compatibility with versions of currently installed libraries
    (including PhenoAI) and the running python version. Querying of server is
    done by query_server function in this module.

    .. attention:: This function does not automatically install the AInalysis.

    Parameters
    ----------
    uniquedbid: :obj:`str`
        Unique ID of the AInalysis. Is stored in the configuration file of the
        AInalysis.
    version: :obj:`int`
        Integer indicating the version number of the AInalysis.

    Returns
    -------
    error: :obj:`bool`
        Boolean indicating if an error occurred on the server during processing
        of request. If True, return variable `text` will be the unformatted
        error message.
    update: :obj:`bool`
        Boolean indicating if an update is available. If return variable
        `error` is True, this variable will be `None`.
    text: :obj:`str`
        Return message. If return variable `update` is True, this message will
        be formatted.
    disclaimer: :obj:`str`
        Disclaimer message on usage of premade AInalyses. """

    logger.debug(("Querying server for ainalysis update information (dbid: {},"
                  " version: {})").format(uniquedbid, version))
    logger.set_indent("+")
    answer = query_server("ainalysis", {
        "ainalysis": uniquedbid,
        "current": version
    })
    logger.set_indent("-")
    return (answer["error"], answer["update"],
            format_server_message(answer["text"]))


def check_phenoai_update():
    """ Check if there is a new version available for the PhenoAI package

    Checks if a new version is available for the PhenoAI package. Versions are
    automatically checked for compatibility with versions of currently
    installed libraries and the running python version. Querying of server is
    done by query_server function in this module.

    .. attention:: This function does not automatically install the new PhenoAI
        version.

    Returns
    -------
    error: :obj:`bool`
        Boolean indicating if an error occurred on the server during processing
        of request. If True, return variable `text` will be the unformatted
        error message.
    update: :obj:`bool`
        Boolean indicating if an update is available. If return variable
        `error` is True, this variable will be `None`.
    text: :obj:`str`
        Return message. If return variable `update` is True, this message will
        be formatted.
    """
    answer = query_server("phenoai")
    logger.set_indent("+")
    logger.debug(("Querying server for phenoai update information"
                  "(version: {})").format(__version__))
    logger.set_indent("-")
    return (answer["error"], answer["update"],
            format_server_message(answer["text"]))


def query_server(target, extra_post_data=None):
    """ Query server for information

    This function is called by the `check_*_update` functions in this module
    and should not be called directly by the user.

    Parameters
    ----------
    target: :obj:`str`
        Select which update script to call on the server. Can be 'ainalysis'
        or 'phenoai'.
    extra_post_data: :obj:`dict`
        Add extra information to the dictionary that is sent to the server via
        POST request.

    Returns
    -------
    json_decoded: :obj:`dict`
        Dictionary of json decoded returned information.
    """
    postdata = {
        "phenoai":
        __version__,
        "python":
        "{}.{}.{}".format(sys.version_info[0], sys.version_info[1],
                          sys.version_info[2])
    }
    for lib in ["sklearn", "tensorflow", "keras"]:
        try:
            package = importlib.import_module(lib)
            postdata[lib] = package.__version__
        except Exception:
            pass

    if extra_post_data is not None:
        postdata.update(extra_post_data)
    
    # Check if request can be made
    if __apiurl__ is None:
        logger.warning(("Could make no request to the server, as no API URL "
                        "was specified for this PhenoAI version."))
        return (False, None, "Unknown API URL")
    try:
        data = requests.post(__apiurl__.format(target),
                            data=postdata,
                            timeout=5)
        logger.debug("Data returned from server: {}".format(data.text))
        j = data.json()
        return j
    except requests.exceptions.ConnectionError:
        logger.debug("Could not connect with PhenoAI update server")
        return (False, None, "Could not connect with PhenoAI server.")
    except json.decoder.JSONDecodeError:
        logger.debug("Server response was incorrectly formatted")
        return (False, None, "Got invalid formatted response from the server.")


def format_server_message(text, border=True, line_length=75):
    """ Format server message to be centered with a certain line length

    Formats the provided text to be centered in lines of provided length. If
    the text is longer than the provided length, the text will continue on new
    lines until the text stops.

    Parameters
    ----------
    text: :obj:`str`
        Text that will be centered and put over multiple lines.
    border: :obj:`bool`. Optional
        If set to `True`, the first and last line of the new text will consist
        out of line_length * "=". Default is `True`
    line_length: :obj:`int`. Optional
        Number of characters per line. Default is 25.

    Returns
    -------
    formatted_text: :obj:`str`
        Formatted text. Line breaks are denoted by \n """
    lines = []
    text = text.strip()
    words = text.split()
    if border:
        lines.append("=" * line_length)
    line = ""
    i = 0
    for word in words:
        if len(line) + len(word) + 1 <= line_length:
            line += " {}".format(word)
        if len(line) + len(word) + 1 > line_length or i == len(words) - 1:
            spaces = floor((line_length - len(line)) / 2)
            line = (" " * spaces) + line
            lines.append(line)
            line = ""
        i += 1
    if border:
        lines.append("=" * line_length)
    return "\n".join(lines)
