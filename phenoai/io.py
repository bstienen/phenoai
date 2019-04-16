""" The io module contains functions to read and create files. Files that have
a reader interface in this module are .slha, .hdf5, .csv, .sfv and .yaml. Files
with a writer interface are .hdf5, .csv and .yaml. A more global function to
find all files with a specific extension is implemented via the
:func:`phenoai.io.get_file_paths` function. """
from os import listdir
import os.path
import codecs
try:
    import cPickle as pkl
except Exception:
    import pickle as pkl

import numpy as np
import pyslha
import h5py
from yaml import load as yamlload
from yaml import dump as yamldump
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from phenoai import exceptions


def get_file_paths(locations, extensions=None, recursive=False):
    """ Return all paths from all files in a folder fulfilling requirements

    This function walks over all files in a folder. If its extension matches
    the extension requirement (if any) the path to the file is stored in a list
    which is returned by this function. By using the `recursive` argument to
    this function all encountered folders will be walked through as well.

    Parameters
    ----------
    locations: :obj:`str`, :obj:`list(str)`
        Paths to folders which have to be walked through looking for files
    extensions: :obj:`str`, :obj:`list(str)`, :obj:`None`, optional
        Extensions of files of which the path has to be returned. If `None` all
        encountered files will have their path stored.
    recursive: :obj:`bool`, optional.
        Determines if encountered folders have to be walked through as well.
        Default is `False`.

    Returns
    -------
    locations: :obj:`list(str)`
        List of all paths to files fulfilling the extensions requirement."""

    # Locations of the found files
    locs = []
    # If provided locations argument is a list call this function for each of
    # the entries. Add result of each call to list of found file paths
    if isinstance(locations, list):
        for l in locations:
            locs.extend(get_file_paths(l, extensions))
    # Check if provided locations argument is a string
    elif isinstance(locations, str):
        # Check if locations is a valid location
        if not os.path.exists(locations):
            raise exceptions.FileIOException(("Location '{}' does not "
                                              "exist.").format(locations))
        # Check if it is a directory
        if os.path.isdir(locations):
            # If search is resursive get files in subdir and call this function
            # recursively. Add result for each call to list of found file paths
            content = [
                os.path.join(locations, f) for f in listdir(locations)
                if os.path.isfile(os.path.join(locations, f))
            ]
            for c in content:
                if os.path.isdir(c) and recursive:
                    paths = get_file_paths(c, extensions, True)
                    if paths is not None:
                        locs.extend(paths)
                elif os.path.isfile(c):
                    path = get_file_paths(c, extensions, recursive)
                    if path is not None:
                        locs.extend(path)
        elif os.path.isfile(locations):
            if extensions is None:
                # No requirement, add location to list of file paths
                locs = [locations]
            elif isinstance(extensions, str):
                # Requirement is a string, check if file name ends with
                # extension. If it does, add file path to list of found file
                # paths
                if locations.endswith(extensions):
                    locs.append(locations)
            elif isinstance(extensions, list):
                # Requirement is a list, check for each of the entries in the
                # list if it contains the extension of the file.
                # If it does, add file path to list of found file paths
                for ext in extensions:
                    if locations.endswith(ext):
                        locs.append(locations)
                        break
            else:
                # No valid extension requirement provided
                raise exceptions.FileIOException(
                    ("Extension of files has to be a (list of) string(s), not "
                     "a '{}'.").format(type(extensions)))
        else:
            raise exceptions.FileIOException(
                ("Provided locations '{}' is not "
                 "a directory or a file").format(locations))
    else:
        # No valid locations argument input
        raise exceptions.FileIOException(
            ("Location of files has to be a (list of) path(s) [string] to "
             "files or folders containing them. Provided was '{}'.").format(
                 type(locations)))
    # Return list of file locations
    locs = sorted(locs)
    return locs


def read_slha(path, reader_list=None):
    """ Reads a .slha file to :obj:`pyslha.Doc` object or :obj:`numpy.ndarray`.

    Reads the content of a .slha file into a :obj:`pyslha.Doc`. If a reader
    list was provided these requested entries are extracted fromt the
    :obj:`pyslha.Doc` object and returned as a :obj:`numpy.ndarray`. If no
    readerlist was provided the :obj:`pyslha.Doc` object is returned.

    Parameters
    ----------
    path: :obj:`str`
        Path of the .slha file to be read
    reader_list: :obj:`list(list)` of slha [BLOCK, SWITCH] entries. Optional
        List of entries in the .slha file, denoted by [BLOCK, SWITCH] entries.
        A reader list is therefore 2-dimensional object (a list of lists). If
        `None` was provided, no specific elements will be read from the file.
        Default is `None`.

    Returns
    -------
    content: :obj:`pyslha.Doc`, :obj:`numpy.ndarray`
        If a valid reader list was provided a numpy.ndarray with the requested
        content is returned. Else the pylsha.Doc object is returned. """

    # Read .slha file into pyslha.Doc object
    docobj = None
    if (isinstance(path, pyslha.Doc)):
        return path
    if isinstance(path, str):
        if os.path.isfile(path):
            try:
                docobj = pyslha.read(path)
            except Exception as e:
                raise exceptions.FileIOException(
                    ("Unexpected pyslha error while reading '{}': {}.").format(
                        path, str(e)))
        else:
            raise exceptions.FileIOException(
                "File not found '{}'.".format(path))
    else:
        raise exceptions.FileIOException(
            ("Filepath to the .slha to read has to be a string (supplied: "
             "'{}').").format(type(path)))

    # Check if reader list is provided
    if reader_list is None:
        return docobj
    if isinstance(reader_list, list):
        data = np.zeros(len(reader_list))
        for i, reader_entry in enumerate(reader_list):
            if len(reader_entry[i]) != 2:
                raise exceptions.FileIOException(("Datalist must only contain "
                                                  "lists with format [BLOCK, "
                                                  "SWITCH]."))
            try:
                try:
                    data[i] = docobj.blocks[reader_entry[0].upper()][int(
                        reader_entry[1])]
                except Exception:
                    data[i] = docobj.blocks[reader_entry[0].upper()][
                        reader_entry[1]]
            except ValueError as e:
                raise exceptions.FileIOException(
                    ("SWITCH '{}' could not be casted to an integer or "
                     "tuple.").format(reader_entry[1]))
            except KeyError:
                raise exceptions.FileIOException(
                    "No SWITCH '{}' in BLOCK '{}' found.".format(
                        reader_entry[1], reader_entry[0]))
        return data
    return docobj


def read_hdf5(path, name):
    """ Reads hdf5 file to :obj:`numpy.ndarray`

    Parameters
    ----------
    path: :obj:`str`
        Path to the .hdf5 file.
    name: :obj:`str`
        Name of the array to be read.

    Returns
    -------
    content: :obj:`numpy.ndarray`
        Content of the .hdf5 file. """
    with h5py.File(path, 'r') as f:
        content = f[name][()]
    return content


def read_csv(path, headerlines=False):
    """ Reads and returns the content of a .csv file

    Parameters
    ----------
    path: :obj:`str`
        Path to the .csv file to be read.
    headerlines: :obj:`bool`, :obj:`int`, optional.
        If set to an integer, that number of first lines is not included in the
        content array. If set to True, the first line is excluded. No lines are
        excluded from the content array if set to False. Default is `False`.

    Returns
    -------
    content: :obj:`numpy.ndarray`
        Content of the .csv file. """

    content = np.genfromtxt(path, delimiter=',')
    if headerlines:
        if isinstance(headerlines, int):
            content = content[:headerlines]
        else:
            content = content[:headerlines]

    return content


def read_checksum(path):
    """ Reads checksums from a checksum file and returns them in a dictionary

    Parameters
    ----------
    path: :obj:`str`
        Path to a checksum file (.sfv)

    Returns
    -------
    checksums: :obj:`dict`
        Dictionary of checksums stored in the provided checksum file. """
    if not os.path.isfile(path):
        raise exceptions.FileIOException(("Checksum file '{}' could not be "
                                          "found.").format(path))
    checksums = {}
    with open(path, 'r') as csfile:
        lines = csfile.readlines()
        for l in lines:
            word = l.split()
            checksums[word[0]] = word[1]
    return checksums


def read_yaml(path):
    """ Reads the content of a .yaml file returns it as dictionary.

    Parameters
    ----------
    path: :obj:`str`
        Path to the .yaml file to be read.

    Returns
    -------
    yamlcontent: :obj:`dict`
        Content of the read .yaml file in dictionary format. """
    if not os.path.isfile(path):
        raise ImportError(("YAML file could not be found at location "
                           "'{}'.").format(path))
    with open(path) as runcard:
        yamlcontent = yamlload(runcard, Loader=Loader)
    return yamlcontent


def get_lsp_from_slha(slha):
    """ Reads the LSP(s) for a (list of) .slha file(s)

    Finds and returns the switch of the lightest supersymmetric particle in the
    MASS block of a .slha file. As such a minimal switch value of 1000000 is
    required. If multiple particles could all be qualified as the LSP, the one
    with the smallest switch value is given.

    Parameters
    ----------
    slha: :obj:`str`, :obj:`list(str)`
        Path to a .slha file or a list of paths to .slha files.

    Returns
    -------
    lsps: :obj:`int`, :obj:`list(int)`
        The switch of the LSP in the provided .slha file. If a list of .slha
        files was provided a list of switches is returned. """

    if isinstance(slha, list):
        correct_lsp = [None] * len(slha)
        for i, s in enumerate(slha):
            correct_lsp[i] = get_lsp_from_slha(s)
        return correct_lsp
    if isinstance(slha, (str, pyslha.Doc)):
        spectrum = read_slha(slha)
        blocks = [spectrum.blocks[i].name for i in spectrum.blocks]
        if 'MASS' in blocks:
            masses = np.array([[i, spectrum.blocks['MASS'][i]]
                               for i in spectrum.blocks['MASS'].keys()
                               if i > 1e6])
            masses = masses[abs(masses[:, 1]).argsort()]
            return masses[0, 0]
        raise exceptions.FileIOException(("No MASS block found, so no LSP "
                                          "check could be performed."))
    raise exceptions.FileIOException(("Can only read the LSP of a .slha file "
                                      "(provide string of path to file) or on "
                                      "a list of .slha files. Provided was a "
                                      "'{}'").format(type(slha)))


def write_hdf5(path, name, nparray):
    """ Writes a :obj:`numpy.ndarray` to a file in .hdf5 format.

    Parameters
    ----------
    path: :obj:`str`
        Location to where the .hdf5 should be written.
    name: :obj:`str`
        Name of the array in the .hdf5 file
    nparray: :obj:`numpy.ndarray`
        Numpy array that should be saved in the .hdf5 file. """
    with h5py.File(path, 'w') as hf:
        hf.create_dataset(name, data=nparray)


def write_csv(path, nparray, header=None):
    """ Writes a :obj:`numpy.ndarray` to a file in .csv format.

    Parameters
    ----------
    path: :obj:`str`
        Location to where the .csv should be written.
    nparray: :obj:`numpy.ndarray`
        Numpy array that should be saved in the .csv file.
    header: :obj:`list`, :obj:`str`, optional.
        Header line at the top of the .csv file. Can be a string (which will
        form the literal top line of the .csv file) or a list (which will be
        joined with "," to form the top line). If `None` no header line is
        inserted. Default is `None`. """

    if isinstance(header, list):
        header = ",".join(header)
    if isinstance(header, str):
        np.savetxt(path, nparray, delimiter=",", header=header)
    elif header is None:
        np.savetxt(path, nparray, delimiter=",")
    else:
        raise exceptions.FileIOException(("Provided header was not a string "
                                          "or a list"))


def write_yaml(path, dictionary):
    """ Writes a dictionary to a file in .yaml format.

    Parameters
    ----------
    path: :obj:`str`
        Location to where the .yaml should be written.
    dictionary: :obj:`dict`
        Dictionary that should be stored in the file."""
    with open(path) as f:
        yamldump(dictionary, f)


def pickle(obj):
    """ Creates a serialization of the provided object

    Serialization is done by :mod:`pickle` module. If :mod:`cPickle` package is
    available, that package will be used instead, yielding a gain in speed.

    Parameters
    ----------
    obj: :obj:`obj`
        Object to be serialized.

    Returns
    -------
    pickle: :obj:`pickle.pickle`
        Serialized version of the provided object. """
    return codecs.encode(pkl.dumps(obj), "base64").decode()


def unpickle(pickle):
    """ Creates an object from a serialized one

    Unserialization is done by :mod:`pickle` module. If :mod:`cPickle` package
    is available, that package will be used instead, yielding a gain in speed.

    Be aware that unpickling a serialized object or file from an unknown source
    yields safety risks: serialized files are just compressed computer code
    that can be executed.

    Parameters
    ----------
    pickle: :obj:`pickle.pickle`
        Object serialized with pickle (or cPickle) package.

    Returns
    -------
    obj: :obj:`obj`
        Unserialized version of provided object. """
    return pkl.loads(codecs.decode(pickle.encode(), "base64"))
