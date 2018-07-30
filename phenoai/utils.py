""" Miscellaneous functions

This module implements various functions that are used throughout the package and serve general purposes. """

import random
import string
import os
import zlib
from decimal import Decimal

import numpy as np


def is_none(x):
	""" Checks if variable equals `None`

	This is useful, because comparing a numpy ndarray to `None` yields a warning or an error (depening on installed version of numpy)

	Parameters
	----------
	x: any variable
		Variable that needs to be checked for being equal to `None`

	Returns
	-------
	b: boolean
		True of input variable equals `None`, else False. """
	return isinstance(x, type(None))
def random_string(length):
	""" Creates a random string with specified length

	Returned string contains uppercase characters, lowercase characters and digits

	Parameters
	----------
	length: integer
		Length of the returned string

	Returns
	-------
	rndstr: string
		Random string with specified length. """
	return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=length))
def bool_to_text(b):
	""" Changes a provided boolean into a 'Yes' or 'No' string

	No test is performed on whether or not the provided variable is boolean or not, only an 'if b: / else:' test is performed.

	Parameters
	----------
	b: any object
		Object that will be tested for its evaluation to a boolean.
		
	Returns
	-------
	text: string
		'Yes' if input variable is evaluated as `True`, 'No' otherwise. """
	if b:
		return "Yes"
	else:
		return "No"
def stringify(l):
	""" Converts all entries in a list or array to strings

	Parameters
	----------
	l: list or numpy.ndarray
		List or numpy ndarray that has to be converted to strings. 

	Returns
	-------
	strings: list or numpy.ndarray
		List or numpy ndarray with strings for entries. """

	# Return stringified version of numpy array
	if isinstance(l, np.ndarray):
		return l.astype(np.str)
	# Raise exception if not a list
	if not isinstance(l, list):
		raise Exception("Can only stringify lists and numpy.ndarrays")
	strings = [None]*len(l)
	for i in range(len(l)):
		# Check if element not a list itself
		if isinstance(l[i], list):
			strings[i] = stringify(l[i])
		else:
			# Stringify element
			strings[i] = str(l[i])
	# Return list of strings
	return strings
def multi_join(l):
	""" Converts a multi-dimensional list into a string

	Parameters
	----------
	l: list or numpy.ndarray
		List that has to be converted into a string.

	Returns
	-------
	s: string
		String of the provided list. """

	content = ""
	for k in range(len(l)):
		if isinstance(l[k], list):
			item = multi_join(l[k])
		else:
			item = str(l[k])
		if content != "":
			content += ", "
		content += item
	return "[{}]".format(content)
def dict_to_matrix(dictionary, nrows, ncols):
	""" Converts a dictionary to a 2-dimensional numpy ndarray 

	Creates a numpy ndarray with specified number of rows and columns. This matrix will be filled with the entries in the dictionary. If the dictionary contains too few entries to fill the matrix, the matrix is zero-padded. An Exception will be raised if the dictionary contains too many entries.

	Parameters
	----------
	dictionary: dictionary
		Dictionary containing the entries with which the matrix has to be filled.
	nrows: integer
		Number of rows for the to-be-generated matrix.
	ncols: integer
		Number of columnns for the to-be-generated matrix.

	Returns
	-------
	matrix: numpy.ndarray
		Numpy ndarray of specified size with entries from provided dictionary. """
	if len(dictionary) > nrows*ncols:
		raise Exception("Dictionary has more entries than the matrix would have with shape (nrows, cols).")
	matrix = np.zeros((int(nrows), int(ncols)))
	for i in range(nrows):
		for j in range(ncols):
			matrix[i,j] = dictionary[i+1,j+1]
	return matrix
def dict_to_square_matrix(dictionary, N=None):
	""" Converts a dictionary to a 2-dimensional square numpy ndarray

	Creates a numpy ndarray with specified number of rows and columns. If no number of rows and columns is provided, this number will be set to the square root of the number of entries in the dictionary (unless this is not an integer, in which case an Exception will be raised).

	This matrix will be filled with the entries in the dictionary. If the dictionary contains too few entries to fill the matrix, the matrix is zero-padded. An Exception will be raised if the dictionary contains too many entries.

	Parameters
	----------
	dictionary: dictionary
		Dictionary containing the entries with which the matrix has to be filled.
	N: integer (default: `None`)
		Number of rows and columns for the square matrix. If `None`, the square root of the number of entries in the dictionary will be used instead.

	Returns
	-------
	matrix: numpy.ndarray
		Numpy ndarray of specified size with entries from provided dictionary. """
	if is_none(N):
		N = np.sqrt(len(dictionary))
		if not isinstance(N, int) or N < 1:
			raise Exception("Dictionary has a non-integer square root.")
	return dict_to_matrix(dictionary, N,N)

# Checksum functions
def convert_to_hex(number, n=9):
	""" Convert number to hexadecimal notation
	
	Parameters
	----------
	number: integer
		Number that has to be converted.
	n: integer (default=9)
		Length of the hexadecimal number.

	Returns
	-------
	hex: string
		Hexadecimal representation of provided number. """
	return format(number & 0xFFFFFFFFF, '0{}x'.format(n))
def calculate_file_checksum(filepath, format_checksum=True):
	""" Calculate the checksum of specified file

	Checksum is calculated with zlib.crc32.

	Parameters
	----------
	filepath: string
		Path to the file for which the checksum has to be calculated
	format_checksum: boolean (default: True)
		Boolean indicating if the checksum has to be formatted to hexadecimal notation

	Returns
	-------
	checksum: integer or string
		Calculated checksum. If format_checksum was True, a hexadecimal string representation of integer checksum is returned. If False, this integer is returned. """
	buffersize = 65536
	crcvalue = 0
	if os.path.exists(filepath):
		with open(filepath, 'rb') as afile:
			buffr = afile.read(buffersize)
			while len(buffr) > 0:
				crcvalue = zlib.crc32(buffr, crcvalue)
				buffr = afile.read(buffersize)
	if format_checksum:
		return convert_to_hex(crcvalue)
	return crcvalue
def calculate_folder_checksum(folderpath, format_checksum=True, recursive=True):
	""" Calculate the checksum of a specified folder

	Checksum is calculated with zlib.crc32.

	Parameters
	----------
	folderpath: string
		Path to the folder for which the checksum has to be calculated
	format_checksum: boolean (default: True)
		Boolean indicating if the checksum has to be formatted to hexadecimal notation
	recursive: boolean (default: True)
		Boolean indicating if the folder has to be searched resursively, also making checksums of files in folders in the folder (depth: unlimited).

	Returns
	-------
	checksum: integer or string
		Calculated checksum. If format_checksum was True, a hexadecimal string representation of integer checksum is returned. If False, this integer is returned. """

	buffersize = 65536
	crcvalue = 0
	if os.path.exists(folderpath):
		for root, subdirs, files in os.walk(folderpath):
			for f in files:
				if f != 'checksums.sfv':
					crcvalue += calculate_file_checksum("{}/{}".format(root,f), False)
			if recursive:
				for s in subdirs:
					crcvalue += calculate_folder_checksum(folderpath+"/"+s, False)
	if format_checksum:
		return convert_to_hex(crcvalue)
	return crcvalue
def calculate_ainalysis_checksums(folder):
	""" Calculate checksums of specified AInalysis

	Calculates all relevant checksums for an AInalysis, namely for

	- the estimator.pkl or estimator.hdf5 file
	- the configuration.yaml file
	- the functions.py file
	- the AInalysis folder as a whole (recursive=True)

	Results are returned as a dictionary of hexadecimal representations of the checksums.

	Parameters
	----------
	folder: string
		Path to the AInalysis folder.

	Returns
	-------
	checksums: dictionary
		Dictionary containing the checksums of the AInalysis folder (see above for specification). """
	if os.path.isfile(folder+"/estimator.pkl"):
		cs_estimator = calculate_file_checksum(folder+"/estimator.pkl")
	else:
		cs_estimator = calculate_file_checksum(folder+"/estimator.hdf5")
	cs_card = calculate_file_checksum(folder+"/configuration.yaml")
	cs_functions = calculate_file_checksum(folder+"/functions.py")
	cs_total = calculate_folder_checksum(folder)
	return {"estimator":cs_estimator, "configuration.yaml":cs_card, "functions.py":cs_functions, "total":cs_total}