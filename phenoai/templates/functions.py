# IMPORTS
""" No imports defined atm """

# FILE READER FUNCTION
""" Reads files into data arrays.

Takes filepaths in as a list and returns the content of the files in the form
of a numpy.ndarray of shape (nDatapoints, nParameters). This function is used
if "filereader" is set to "function" in the configuration.yaml file. """
def read(data):
	return data

# TRANSFORM DATA FUNCTION
""" Transforms the data before it is subjected to prediction routines.

Takes in data as a numpy.ndarray with shape (nDatapoints, nParameters) and
should return data in the same shape. This function is used if defined
here. """
def transform(data):
	return data

# TRANSFORM PREDICTIONS FUNCTION
""" Transforms the predictions before it is outputted by the AInalysis.

Takes in predictions as a numpy.ndarray with shape (nDatapoints, ) and should
return predictions in the same shape. This function is used if defined
here. """
def transform_predictions(data):
	return data

# DATA MAPPING FUNCTION
""" Allows mapping of data via arbitraty function.

Takes in data as a numpy.ndarray with shape (nDatapoints, nParameters) and
should return data in the same shape. This function is used if "mapping" is
set to "function" in the configuration.yaml file. """
def mapping(data):
	return data
