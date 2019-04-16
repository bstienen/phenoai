""" Miscellaneous functions

This module implements various functions that are used throughout the package
and serve general purposes. """

import random
import string
import os
import zlib

import numpy as np


def random_string(length):
    """ Creates a random string with specified length

    Returned string contains uppercase characters, lowercase characters and
    digits

    Parameters
    ----------
    length: :obj:`int`
        Length of the returned string

    Returns
    -------
    rndstr: :obj:`str`
        Random string with specified length. """
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits +
                       string.ascii_lowercase,
                       k=length))


def bool_to_text(b):
    """ Changes a provided boolean into a 'Yes' or 'No' string

    No test is performed on whether or not the provided variable is boolean or
    not, only an 'if b: / else:' test is performed.

    Parameters
    ----------
    b: any
        Object that will be tested for its evaluation to a boolean.

    Returns
    -------
    text: :obj:`str`
        'Yes' if input variable is evaluated as `True`, 'No' otherwise. """
    if b:
        return "Yes"
    return "No"


def stringify(l):
    """ Converts all entries in a list or array to strings

    Parameters
    ----------
    l: :obj:`list(float)`, :obj:`numpy.ndarray`
        List or numpy ndarray that has to be converted to strings.

    Returns
    -------
    strings: :obj:`list(str)`, :obj:`numpy.ndarray`
        List or numpy ndarray with strings for entries. """

    # Return stringified version of numpy array
    if isinstance(l, np.ndarray):
        return l.astype(np.str)
    # Raise exception if not a list
    if not isinstance(l, list):
        raise Exception("Can only stringify lists and numpy.ndarrays")
    strings = [None] * len(l)
    for i, el in enumerate(l):
        # Check if element not a list itself
        if isinstance(el, list):
            strings[i] = stringify(el)
        else:
            # Stringify element
            strings[i] = str(el)
    # Return list of strings
    return strings


def multi_join(l):
    """ Converts a multi-dimensional list into a string

    Parameters
    ----------
    l: iterable
        List that has to be converted into a string.

    Returns
    -------
    s: :obj:`str`
        String of the provided list. """

    content = ""
    for _, el in enumerate(l):
        if isinstance(el, list):
            item = multi_join(el)
        else:
            item = str(el)
        if content != "":
            content += ", "
        content += item
    return "[{}]".format(content)


def dict_to_matrix(dictionary, nrows, ncols):
    """ Converts a dictionary to a 2-dimensional numpy ndarray

    Creates a numpy ndarray with specified number of rows and columns. This
    matrix will be filled with the entries in the dictionary. If the dictionary
    contains too few entries to fill the matrix, the matrix is zero-padded. An
    :obj:`Exception` will be raised if the dictionary contains too many
    entries.

    Parameters
    ----------
    dictionary: :obj:`dict`
        Dictionary containing the entries with which the matrix has to be
        filled.
    nrows: :obj:`int`
        Number of rows for the to-be-generated matrix.
    ncols: :obj:`int`
        Number of columnns for the to-be-generated matrix.

    Returns
    -------
    matrix: numpy.ndarray
        Numpy ndarray of specified size with entries from provided
        dictionary. """
    if len(dictionary) > nrows * ncols:
        raise Exception(("Dictionary has more entries than the matrix would "
                         "have with shape (nrows, cols)."))
    matrix = np.zeros((int(nrows), int(ncols)))
    for i in range(nrows):
        for j in range(ncols):
            matrix[i, j] = dictionary[i + 1, j + 1]
    return matrix


def dict_to_square_matrix(dictionary, n=None):
    """ Converts a dictionary to a 2-dimensional square numpy ndarray

    Creates a numpy ndarray with specified number of rows and columns. If no
    number of rows and columns is provided, this number will be set to the
    square root of the number of entries in the dictionary (unless this is not
    an integer, in which case an :obj:`Exception` will be raised).

    This matrix will be filled with the entries in the dictionary. If the
    dictionary contains too few entries to fill the matrix, the matrix is
    zero-padded. An Exception will be raised if the dictionary contains too
    many entries.

    Parameters
    ----------
    dictionary: :obj:`dict`
        Dictionary containing the entries with which the matrix has to be
        filled.
    n: :obj:`int`. Optional
        Number of rows and columns for the square matrix. If `None`, the square
        root of the number of entries in the dictionary will be used instead.
        Default is `None`.

    Returns
    -------
    matrix: :obj:`numpy.ndarray`
        :obj:`numpy.ndarray` of specified size with entries from provided
        dictionary. """
    if n is None:
        n = np.sqrt(len(dictionary))
        if not isinstance(n, int) or n < 1:
            raise Exception("Dictionary has a non-integer square root.")
    return dict_to_matrix(dictionary, n, n)


# Checksum functions
def convert_to_hex(number, n=9):
    """ Convert number to hexadecimal notation

    Parameters
    ----------
    number: :obj:`int`
        Number that has to be converted.
    n: :obj:`int`. Optional
        Length of the hexadecimal number. Default is 9.

    Returns
    -------
    hex: :obj:`str`
        Hexadecimal representation of provided number. """
    return format(number & 0xFFFFFFFFF, '0{}x'.format(n))


def calculate_file_checksum(filepath, format_checksum=True):
    """ Calculate the checksum of specified file

    Checksum is calculated with :func:`zlib.crc32`.

    Parameters
    ----------
    filepath: :obj:`str`
        Path to the file for which the checksum has to be calculated.
    format_checksum: :obj:`bool`. Optional
        Boolean indicating if the checksum has to be formatted to hexadecimal
        notation. Default is `True`.

    Returns
    -------
    checksum: :obj:`int`, :obj:`str`
        Calculated checksum. If format_checksum was `True`, a hexadecimal
        string representation of integer checksum is returned. If `False`,
        this integer is returned. """
    buffersize = 65536
    crcvalue = 0
    if os.path.exists(filepath):
        with open(filepath, 'rb') as afile:
            buffr = afile.read(buffersize)
            while buffr:
                crcvalue = zlib.crc32(buffr, crcvalue)
                buffr = afile.read(buffersize)
    if format_checksum:
        return convert_to_hex(crcvalue)
    return crcvalue


def calculate_folder_checksum(folderpath, format_checksum=True,
                              recursive=True):
    """ Calculate the checksum of a specified folder

    Checksum is calculated with :func:`zlib.crc32`.

    Parameters
    ----------
    folderpath: :obj:`str`
        Path to the folder for which the checksum has to be calculated.
    format_checksum: :obj:`bool`. Optional
        Boolean indicating if the checksum has to be formatted to hexadecimal
        notation. Default is `True`.
    recursive: :obj:`bool`. Optional
        Boolean indicating if the folder has to be searched resursively, also
        making checksums of files in folders in the folder (depth: unlimited).
        Default is `True`.

    Returns
    -------
    checksum: :obj:`int`, :obj:`str`
        Calculated checksum. If format_checksum was `True`, a hexadecimal
        string representation of integer checksum is returned. If `False`,
        this integer is returned. """

    # buffersize = 65536
    crcvalue = 0
    if os.path.exists(folderpath):
        for root, subdirs, files in os.walk(folderpath):
            for f in files:
                if f != 'checksums.sfv':
                    crcvalue += calculate_file_checksum(
                        "{}/{}".format(root, f), False)
            if recursive:
                for s in subdirs:
                    crcvalue += calculate_folder_checksum(
                        folderpath + "/" + s, False)
    if format_checksum:
        return convert_to_hex(crcvalue)
    return crcvalue


def calculate_ainalysis_checksums(folder):
    """ Calculate checksums of specified AInalysis

    Calculates all relevant checksums for an AInalysis, namely for

    - the estimator.pkl or estimator.hdf5 file
    - the configuration.yaml file
    - the functions.py file
    - the AInalysis folder as a whole (recursive)

    Results are returned as a dictionary of hexadecimal representations of the
    checksums.

    Parameters
    ----------
    folder: :obj:`str`
        Path to the AInalysis folder.

    Returns
    -------
    checksums: :obj:`dict`
        Dictionary containing the checksums of the AInalysis folder (see above
        for specification). """
    if os.path.isfile(folder + "/estimator.pkl"):
        cs_estimator = calculate_file_checksum(folder + "/estimator.pkl")
    else:
        cs_estimator = calculate_file_checksum(folder + "/estimator.hdf5")
    cs_card = calculate_file_checksum(folder + "/configuration.yaml")
    cs_functions = calculate_file_checksum(folder + "/functions.py")
    cs_total = calculate_folder_checksum(folder)
    return {
        "estimator": cs_estimator,
        "configuration.yaml": cs_card,
        "functions.py": cs_functions,
        "total": cs_total
    }
