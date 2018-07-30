""" The classes module implements classes from which other classes in the PhenoAI package are derived. Currently these classes are Estimator and Configuration. """

from . import splash
splash.splash()

from copy import deepcopy
import os.path

import numpy as np

from . import exceptions
from . import io
from . import logger
from . import utils



class Estimator(object):
	""" The basic interface methods for estimator classes in the estimators module.
	
	Properties
	----------
	est: estimator
		The estimator to which Estimator derived classes provide an interface. Type of this variable is determined by the derived class.
	path: string
		Path to the stored estimator.
	
	Constructor arguments
	----------------------
	path: string
		Path to the location of the stored estimator.
	load: boolean (default=False)
		Defines if the estimator has to be loaded on initialisation of the interface class.""" 
	def __init__(self, path=None, load=False):
		if not utils.is_none(path):
			if not os.path.isdir(path):
				raise FileNotFoundError("Estimator could not be found at path '{}'.".format(path))
			self.est = None
			if path[-1] == "/":
				path = path[:-1]
			self.path = path
			if load:
				self.load()
	def clear(self):
		""" Removes the loaded estimator from memory.

		This saves memory, but does mean that the estimator has to be reloaded as soon as a new prediction with it has to be made."""
		self.est = None
	def is_loaded(self):
		""" Checks if the estimator is loaded.

		Returns
		-------
		is_loaded: bool
			True if estimator is currently loaded, False otherwise."""
		return (not utils.is_none(self.est))

class Configuration(object):
	""" The basic interface to configuration classes.
	
	This base class defines all loading, resetting and printing functions for configuration classes throughout the package (currently only ainalyses.AInalysisConfiguration). Handles only configuration files following the .yaml format, see http://www.yaml.org.
	
	Properties
	----------
	configuration: dictionary (default={})
		Content of the configuration. Contains an empty dictionary if configuration is not loaded.
	folder: string (default=`None`)
		AInalysis folder. Is deduced from provided path of the AInalysis configuration.
	path: string (default=`None`)
		Location where the .yaml configuration is stored.
	validated: boolean (default=False)
		Boolean indicating if the configuration stored in the configuration property has been validated by the validate method in the derived class.
	
	Constructor parameters
	----------------------
	path: string (default=`None`)
		Location where the .yaml configuration file is stored."""
	def __init__(self, path=None, entries=None):
		self.configuration = {}
		self.path = None
		self.folder = None
		if not utils.is_none(path):
			self.load(path)
		elif not utils.is_none(entries) and isinstance(entries, dict):
			self.configuration = entries
		self.validated = False
	def __getitem__(self, key):
		return self.configuration[key]
	def __setitem__(self, key, value):
		self.configuration[key] = value
	def get(self, key = None):
		""" Returns the configuration in dictionary form or an entry of the configuration

		Parameters
		----------
		key: string (default=`None`)
			Key of the dictionary entry that has to be returned. If no key or `None` was provided the entire dictionary is returned.

		Returns
		-------
		configvalue: dictionary or dictionary entry
			If key was provided as input argument the entry of the configuration with that key is returned. If no key or `None` was provided, the entire configuration directionary is returned."""
		if utils.is_none(key):
			return self.configuration
		else:
			return self.configuration[key]
	def show(self, printdict = None):
		""" Prints the entire configuration via the print() command.

		Parameters
		----------
		printdict: dictionary (default=`None`)
			The dictionary that has to be printed by the print() command. If no dictionary or `None` is provided the self.configuration property will be used instead. """
		if printdict == None:
			printdict = self.configuration
		maxkeylength = 0
		for k in printdict.keys():
			if not isinstance(k, str):
				printdict[str(k)] = printdict[k]
				del(printdict[k])
				k = str(k)
			if len(k) > maxkeylength:
				maxkeylength = len(k)
		for key, value in sorted(printdict.items()):
			if isinstance(value, dict):
				self.show(printdict[key])
			elif isinstance(value, list):
				if len(value) == 1:
					print(key.ljust(maxkeylength+6)+"list of length {}: [{}]".format(len(value), value[0]))
				elif len(value) <= 5:
					print(value)
					liststr = utils.multi_join(value)
					print(key.ljust(maxkeylength+6)+"list of length {}: [{}]".format(len(value), liststr))
				else:
					print(key.ljust(maxkeylength+6)+"list of length {}: [{}, {}, ... {}, {}]".format(len(value), value[0], value[1], value[-2], value[-1]))
			else:
				print(key.ljust(maxkeylength+6)+str(value))
	def load(self, path):
		""" Loads the configuration indicated by the provided path.

		The loaded configuration is stored as a dictionary in the configuration property of the object. The provided path is stored in the path property. Configuration files have to follow the .yaml format (see http://www.yaml.org/)

		Parameters
		----------
		path: string
			Location of the configuration .yaml file. """
		self.configuration = io.read_yaml(path)
		self.path = path
		pathparts = path.split('/')
		folderparts = pathparts[:-1]
		self.folder = "/".join(folderparts)
	def validate(self):
		""" This method is only implemented in derived classes. If called on a Configuration instance a ConfigurationException is raised. """
		raise ConfigurationException("Cannot call validate method on Configuration instance. Only available in instances derived from the Configuration class.")

class AInalysisResults(object):
	""" Container for and interface to results of an AInalysis instance
	
	The AInalysisResults class functions as a container for results produced by an AInalysis instance and provides methods to access these results efficiently.
	
	Properties
	----------
	result_id: string
		ID of the result object. Equal to the AInalysisID of the AInalysis that produced the results stored in this instance.
	configuration: AInalysisConfiguration instance
		Configuration of the AInalysis that produced the results stored in this instance.
	data: numpy.ndarray
		Data that has been subjected to prediction (after possible mapping).
	data_ids: list of strings
		List if unique IDs (strings) by which data points can be identified. If set, data points and their classifications and predictions can be read from the AInalysisResults object by referencing their ID. If not set (i.e. ids is set to `None`) this functionality is not available.
	mapped: list or boolean
		False if no mapping has taken place. If mapping has taken place, this property stores a list of booleans indicating on a per datapoint basis if that specific datapoint has been mapped or not. In that case the data stored in the data property of this AInalysisResults instance is this mapped data.
	predictions: numpy.ndarray
		Results of the prediction method of the estimator stored in the AInalysis object with the data stored in the data property of this AInalysisResults instance.
	
	Constructor parameters
	----------------------
	result_id: string
		ID of the result object. Equal to the AInalysisID of the AInalysis that produced the results stored in this instance.
	configuration: AInalysisConfiguration instance
		Configuration of the AInalysis that produced the results stored in this instance.
	data: numpy.ndarray
		Data that has been subjected to prediction (after possible mapping).
	data_ids: list of strings (default=`None`)
		List if unique IDs (strings) by which data points can be identified. If set, data points and their classifications and predictions can be read from the AInalysisResults object by referencing their ID. If not set (i.e. ids is set to `None`) this functionality is not available.
	mapped: boolean (default=False)
		Boolean indicating if the data has been mapped before prediction. If True, the data stored in the data property of this AInalysisResults instance is this mapped data.
	predictions: numpy.ndarray (default=`None`)
		Results of the prediction method of the estimator stored in the AInalysis object with the data stored in the data property of this AInalysisResults instance. """
	def __init__(self, result_id, configuration, data, data_ids=None, mapped=False, predictions=None):
		self.result_id = result_id
		self.data = data
		self.data_ids = data_ids
		self.mapped = mapped
		self.configuration = Configuration(entries=configuration.configuration)
		self.predictions = predictions
	def get(self, array, reference=None):
		""" Returns the content of the array at location of the reference

		Selects and returns the rows from the provided array which are referenced by the reference argument of this function.

		Parameters
		----------
		array: numpy.ndarray
			Numpy array from which rows have to be selected
		reference: numpy.ndarray or list of references (default=`None`)
			If this reference is an integer, that row of the array with that integer as rownumber will be returned. If the reference is a string, the rownumber of the entry in the self.data_ids equal to this reference will be used instead. The reference variable can also be a list or numpy.ndarray of integers and/or strings. In that case a numpy.ndarray with the selected entries will be returned.

		Returns
		-------
		selection: numpy.ndarray
			Selected row(s) from array corresponding to the provided reference(s). """

		if utils.is_none(reference):
			return array
		elif isinstance(reference, int):
			return array[reference]
		elif isinstance(reference, str):
			for i, did in enumerate(self.data_ids):
				if reference == did:
					return array[i]
		elif isinstance(reference, np.ndarray) or isinstance(reference, list):
			if len(array.shape) == 1:
				a = len(array)
			else:
				a = len(array[0])
			selection = np.zeros(( len(reference), a ))
			for i in range(len(reference)):
				selection[i,:] = self.get(array, reference[i])
			return selection
		raise exceptions.ResultsException("Unknown reference format for get: {}.".format(type(reference)))
	def get_ids(self):
		""" Returns data ids

		Returns
		-------
		ids: numpy.ndarray
			All IDs for the data in this AInalysisResults object"""
		return self.data_ids
	def get_data(self, i=None):
		""" Returns data (rows) used for prediction

		Parameters
		----------
		i: integer, string or list of integers/strings (default=`None`)
			Reference used for selecting rows in the data array. See the documentation for the get method for allowed values and consequences.

		Returns
		-------
		data: numpy.ndarray
			Selected rows from the data array."""
		return self.get(self.data, i)
	def get_classifications(self, i=None, variable=None, calibrated=True):
		""" Returns the classification results based on the predictions stored in the predictions property.

		Uses the information stored in the configuration property to classify the results in the predictions property. These classifications are then returned. If the results are not interpretable as classifications (e.g. because the AInalysis implemented a regressor instead of a classifier) `None` is returned.

		Classification names or indicators or extracted from the 'output' entry in the configuration.

		Parameters
		----------
		i: integer or numpy.ndarray (default=`None`)
			Reference used for generating classifications from the predictions array. See the documentation for the get method for allowed values and consequences.
		calibrated: boolean (default=True)
			Boolean indicating if prediction results have to be calibrated. See documentation for the get_predictions method for requirements.

		Returns
		-------
		classifications: numpy.ndarray
			Requested classifications. """
		if not self.configuration["type"] == "classifier":
			return None
		# Select data
		predictions = self.get(self.predictions, i)
		# Get maxima
		if len(predictions.shape) == 1:
			maxs = np.argmax(predictions, axis=0)
		else:
			maxs = np.argmax(predictions, axis=1)
		# Return classifications
		return self.configuration["classes"][maxs]
	def get_predictions(self, i=None, variable=None, calibrated=True):
		""" Returns the predictions stored in predictions property.

		Returns the prediction results stored in the predictions property of this object. By setting the `calibrated` argument to True (default), the prediction results will first be calibrated before returning, if all of the following requirements are met:

		- the estimator is a classifier;
		- the estimator is not already calibrated;
		- the configuration validly defines a method to calibrate the results.

		If any of these requirements is violated, the bare prediction results are returned. If `calibrated` is set to False, the raw prediction results will be returned either way.

		Parameters
		----------
		i: integer or numpy.ndarray (default=`None`)
			Reference used for selecting rows in the predictions array. See the documentation for the get method for allowed values and consequences.
		calibrated: boolean (default=True)
			Boolean indicating if prediction results have to be calibrated. See documentation for this method for requirements.

		Returns
		-------
		predictions: numpy.ndarray
			Requested (calibrated) predictions. """

		# Get predictions
		preds = self.get(self.predictions, i)
		# Check requirements for calibration
		if calibrated:
			if self.configuration["type"] == 'classifier':
				if not self.configuration["classifier.calibrated"]:
					if self.configuration["classifier.calibrate"]:
						# Get calibration configuration
						bins = self.configuration["classifier.calibrate.bins"]
						values = self.configuration["classifier.calibrate.bins"]
						# Perform calibration
						cut = bins[np.argmin(np.abs(values-0.5))]
						classifications = 1.0*(predictions > cut)
						predscal = np.zeros(len(preds))
						for i in range(len(predictions)):
							b = np.argmin(np.abs(bins - preds[i]))
							predscal[i] = values[b]
						return predscal
		return preds
	def is_outlier(self, i=None, use_map_target_area=False):
		""" Returns information about whether or not data used in prediction lies outside of region sampled with training data.

		Checks for all data selected via reference variable i if it is outside of the region from which training data was sampled for the training of the estimator of the AInalysis that created this AInalysisResults object. By setting the use_map_target_area argument to True the reference area will be taken as the target area for the mapping procedure (if any is defined via a floating point number in the AInalysis configuration). Returns a numpy.ndarray containing booleans indicating if the data points are outside of the sample region (True) or not (False). 

		Note that if mapping took place before prediction (checkable via the is_mapped method) all values returned will be False.

		Parameters
		----------
		i: integer or numpy.ndarray (default=`None`)
			Reference used for selecting data for which the outsiderness has to be determined. See the documentation for the get method for allowed values and consequences.
		use_map_target_area: boolean (default=False)
			Use the mapping target area as reference area instead of the area from which training data was sampled. If set to True but the mapping was not configured via a floating point value in the AInalysis configuration, the method will continue as if this value was set to False.

		Returns
		-------
		outsider: numpy.ndarray
			Numpy array containing booleans. True if data point is an outsider, False otherwise."""

		if not isinstance(self.configuration["mapping"], float) and use_map_target_area:
			raise exceptions.ResultsException("No mapping target area defined in AInalysis configuration.")
		selection_mins = self.get(self.data, i)
		selection_maxs = deepcopy(selection_mins)
		for i in range(len(self.configuration["parameters"])):
			i_min = self.configuration["parameters"][i][2]
			i_max = self.configuration["parameters"][i][3]
			if use_map_target_area:
				r = self.configuration["parameters"][i][3] - self.configuration["parameters"][i][2]
				i_min += r*self.configuration["mapping"]
				i_max -= r*self.configuration["mapping"]
			selection_mins[i] -= i_min
			selection_maxs[i] -= i_max
		outofrange = selection_mins[selection_mins<0]*1.0 + selection_maxs[selection_maxs>0]*1.0
		return np.sum(outofrange) == 1.0
	def is_mapped(self, i=None):
		""" Returns information about whether or not provided data was mapped before prediction took place.

		Parameters
		----------
		i: integer or numpy.ndarray (default=`None`)
			Reference used for selecting data of which mapping information is requested. See the documentation for the get method for allowed values and consequences.

		Returns
		-------
		mapped_global: boolean
			Boolean indicating if mapping procedure has been called at all. Can indicate that map_data was set to False by the user (or left at this default value) or that the AInalysis does not support data mapping.
		mapped: numpy.ndarray of booleans or `None`
			If mapped_global is True this variable will contain a numpy array filled with booleans indicating per data point indicated via reference variable i if it was mapped. This variable will contain `None` if mapped_global was False. """
		if (isinstance(self.mapped, bool) and self.mapped == False) or utils.is_none(self.mapped):
			return (False, None)
		else:
			selection = self.get(self.mapped, i)
			return (True, selection)
	def num(self):
		""" Returns the length of the data (i.e. the number of data points) stored in the AInalysisResults instance.

		Returns
		-------
		L: integer
			Number of data points (and hence the number of predictions) stored in the AInalysisResults instance. """
		return len(self.data)
	def __len__(self):
		return self.num()
	def summary(self):
		""" Prints a summary of the contents of this object """
		logger.debug("Print report for AInalysisResults")
		print("---------------------------")
		print("| AInalysisResults report |")
		print("---------------------------")
		print("ID: {}".format(self.result_id))
		print("Length: {}".format(self.num()))
		# Information on data
		contains_data = not isinstance(self.get_data(), type(None))
		print("Contains data: {}".format(contains_data))
		if contains_data:
			print("   Data shape: {}".format(self.get_data().shape))
			print("   Access via .get_data( args )")
		# Information on Data ids
		contains_data_ids = not isinstance(self.get_ids(), type(None))
		print("Contains data IDs: {}".format(contains_data_ids))
		if contains_data_ids:
			print("   Data IDs length: {}".format(len(self.get_ids())))
			print("   Get full list via .get_ids()")
			print("   Use as argument in .get_*() methods")
		# Information on data mapping
		data_is_mapped = self.is_mapped()[0]
		print("Data is mapped: {}".format(data_is_mapped))
		if data_is_mapped:
			if isinstance(self.is_mapped()[1], list):
				print("   Data IDs length: {}".format(len(self.is_mapped()[1])))
			elif isinstance(self.is_mapped()[1], np.ndarray):
				print("   Data IDs shape: {}".format(self.is_mapped()[1].shape))
			print("   Access via .is_mapped( args )")
		# Information on Data ids
		contains_predictions = not isinstance(self.get_predictions(), type(None))
		print("Contains predictions: {}".format(contains_predictions))
		if contains_predictions:
			print("   Predictions shape: {}".format(self.get_predictions().shape))
			print("   Access via .get_predictions( args )")

class PhenoAIResults(object):
	""" Container class for AInalysisResults.
	
	This class functions as a container class for AInalysisResults from multiple AInalyses. Methods are implemented to aid accessing these instances.
	
	Properties
	----------
	results: list
		List of AInalysisResults. """
	def __init__(self):
		self.results = []
	def add(self, result):
		""" Appends an AInalysisResults instance to the container.

		An error is raised if the result that is to be appended has an AInalysisID that is already present in the stored AInalysisResults instances.

		Parameters
		----------
		result: AInalysisResults instance
			AInalysisResults instance that has to be added to the container. """
		if not utils.is_none(self.get(result.result_id)):
			raise exceptions.ResultsException("Already an AInalysisResults instance stored with AInalysisID '{}'".format(result.result_id))
		self.results.append(result)
	def num(self):
		""" Returns the number of stored AInalysisResults in this container.

		Returns
		-------
		n: integer
			Number of AInalysisResults stored in this container. """
		return len(self.results)
	def __len__(self):
		return self.num()
	def get(self, result_id):
		""" Returns the AInalysis with a given AInalysisID.

		Looks in stored results if there is an AInalysisResults instance with provided ID as Result ID. If found, this instance is returned. If none is found, the provided id is checked if it is an integer in range 0 ... len(results)-1. If so, the result with that internal index is returned (corresponding to the ID from get_ids() at that index). If no such result could be returned, `None` is returned instead.

		Parameters
		----------
		result_id: string
			The Result ID of the AInalysisResults that has to be returned.

		Returns
		-------
		result: AInalysisResults instance / `None`
			AInalysisResults instance with the requested AInalysisID. If no such instance was found, `None` is returned. """
		for i in range(len(self.results)):
			if self.results[i].result_id == result_id:
				return self.results[i]
		if isinstance(result_id, int) and result_id >= 0 and result_id < len(self.results):
			return self.results[result_id]
		return None
	def __getitem__(self, result_id):
		return self.get(result_id)
	def get_ids(self):
		""" Returns a list of the ResultIDs of all stored AInalysisResults instances.

		Returns
		-------
		ids: list
			List of all ResultIDs fo all stored AInalysisResults instances. """
		ids = []
		for i in range(len(self.results)):
			ids.append(self.results[i].result_id)
		return ids
	def summary(self):
		""" Prints a summary of the contents of this object """
		logger.debug("Print report for AInalysisResults")
		print("===========================")
		print("||  PhenoAIResults report  ||")
		print("===========================")
		print("Contains {} AInalysisResults object(s)".format(self.num()))
		print("AInalysisResult IDs:")
		for i in range(self.num()):
			print("  - {} (length: {})".format(self.get_ids()[i], self.get(self.get_ids()[i]).num()))
		print("Access AInalysisResults objects by id via PhenoAIResults[ id ]")