""" Implements classes and interfaces used in the handling of individual AInalyses

This module implements the two classes crucial in the handling of AInalyses: AInalysis and AInalysisConfiguration. Where AInalysis implements methods to load relevant AInalysis files and handle data streams to and from its estimator, the AInalysisConfiguration implements checks to validate the configuration of the AInalysis' configuration.yaml file, to prevent errors from happening (and indicate users of possible mistakes).

Although instances of the AInalysis class can be used directly on AInalysis folders, it is in many cases advisable to use instances of phenoai.phenoai as interface instead. """

from . import splash
splash.splash()

import os
import importlib
from importlib.machinery import SourceFileLoader
from inspect import signature
from copy import deepcopy

import numpy as np

from . import __versionnumber__, __version__
from . import containers
from . import estimators
from . import exceptions
from . import io
from . import logger
from . import updatechecker
from . import utils


class AInalysis(object):
	""" Main data juggler class, dealing with dataflows from and to estimators in Estimator instances.

	AInalysis objects form the interface between the user / PhenoAI object and the estimator stored in the AInalysis. Apart from the run method (which starts the AInalysis), it also implements methods to map data and read files. The main purpose of the object is to shift data around in a coherent way (and change it if needed) in such a way that is in agreement with the configuration of the AInalysis in the configuration card.

	Properties
	----------
	id: string
		Unique identifier for this AInalysis. Results from different AInalyses can be distinguished uniquely by this variable, as this value is copied to the AInalysisResults objects created by this AInalysis object.
	configuration: AInalysisConfiguration instance
		The configuration of the AInalysis from the configuration card stored in a AInalysisConfiguration instance.
	estimator: Estimator derived class from the estimators module
		The estimator of the AInalysis stored in an instance of an Estimator class from the estimators module.
	folder: string
		Location of the AInalysis

	Constructor arguments
	---------------------
	folder: string
		Location of the AInalysis. Will be used to load all information from the AInalysis. This location will be stored in the folder property of the object.
	ainalysis_id: string (default=`None`)
		Unique identifier fot his AInalysis. Will set the id property of the object.
	load_estimator: boolean (default=`True`)
		Boolean indicating if the estimator has to be loaded into memory on initialization of the AInalysis object. If set to False the estimator will be loaded on running of the AInalysis. """
	def __init__(self, folder, ainalysis_id = None, load_estimator=True):
		self.ainalysis_id = ainalysis_id
		self.folder = None
		self.estimator = None
		self.configuration = AInalysisConfiguration()
		self.load(folder, load_estimator)
		if utils.is_none(self.ainalysis_id):
			self.ainalysis_id = self.configuration["defaultid"]
	def load(self, folder, load_estimator=True):
		""" Load the configuration from the AInalysis (and the estimator as well, if requested) into memory

		Parameters
		----------
		folder: string
			Location of the AInalysis. Will be used to load all information from the AInalysis. This location will be stored in the folder property of the object.
		load_estimator: boolean (default=`True`)
			Boolean indicating if the estimator has to be loaded into memory. If set to False the estimator will be loaded on running of the AInalysis. """

		logger.info("Loading AInalysis with ID '{}'".format(self.ainalysis_id))
		# Check if provided ainalysis folder exists
		if not os.path.exists(folder):
			raise FileNotFoundError("AInalysis folder '{}' could not be found".format(folder))
		# Alter folder indication if not conform expectation
		if folder[-1] == "/":
			folder = folder[:-1]
		self.folder = folder
		# Load and validate configuration
		self.configuration.load(self.folder+"/configuration.yaml")
		self.configuration.validate()
		# Initialize estimator
		logger.set_indent("+")
		estfac = estimators.EstimatorFactory()
		self.estimator = estfac.create_estimator(self.configuration["class"], self.folder)
		if load_estimator:
			self.estimator.load()
		logger.set_indent("-")
		logger.info("AInalysis loaded".format(self.ainalysis_id))
		self.check_for_update()
	def can_run(self):
		""" Checks if the AInalysis can be run with the information in the AInalysis folder.

		Checks if the configuration has been validated (which it should do automatically on loading via the load method) and if the estimator is loaded. If either of these is not True, the appropriate methods are called to try to fix this (e.g. self.configuration.validate() is called when the configuration is not validated yet. If the check remains untrue after these operations, False is returned. Else True is returned.

		Returns
		-------
		valid: boolean
			Boolean indicating if AInalysis can run with provided information in the AInalysis folder. """
		if not self.configuration.validated:
			self.configuration.validate()
		if not self.estimator.is_loaded():
			self.estimator.load()
		if not self.configuration.validated or not self.estimator.is_loaded():
			return False
		return True
	def read_files(self, paths):
		""" Reads the content from requested files following the definitions provided in the AInalysis configuration.

		Attempts to read the contents of the provided files via the filereader defined in the AInalysis configuration card. If filereader was not set in this configuration or it was set to False (or any equivalent of it), an AInalysisException is raised. Else the defined filereader if used to extract data from the provided files.

		Parameters
		----------
		paths: String or a list of strings
			Locations of the files that should be read.

		Returns
		-------
		data: numpy.ndarray
			A numpy array containing data from the provided files. Shape of the numpy array will be (x, y), where x is the number of provided files and y the number of parameters defined for this AInalysis (as defined in the parameters value in the configuration card). """

		# Check if file reading is enabled
		if utils.is_none(self.configuration["filereader"]) or self.configuration["filereader"] == False:
			raise exceptions.AInalysisException("AInalysis {} has no file reader.".format(self.ainalysis_id))
		# Initialize reader by function if necessary
		if self.configuration["filereader"] == "function":
			functions = SourceFileLoader("module", self.folder+"/functions.py").load_module()
		# Make paths to list if a string
		if isinstance(paths, str):
			paths = [paths]
		# Loop over paths
		logger.debug("AInalysis '{}' is reading {} file(s)".format(self.ainalysis_id, len(paths)))
		data = None
		warning_given = False
		for i in range(len(paths)):
			# Check if file extension is in format list
			if isinstance(self.configuration["filereader.formats"], list) and not warning_given:
				found = False
				for f in self.configuration["filereader.formats"]:
					if path.endswith(f):
						found = True
				if not found:
					logger.warning("One or more files did not have the defined extension for file reading: {}. This might yield errors later in the program.".format(self.configuration["filereader.formats"]))
			# Get data from file
			if self.configuration["filereader"] == "function":
				d = functions.read(paths[i])
			elif isinstance(self.configuration["filereader"], list):
				d = io.read_slha(paths[i], self.configuration["filereader"])
			# Create data array if not existing
			if utils.is_none(data):
				data = np.zeros((len(paths), len(d)))
			# Add new data to data array
			data[i,:] = d
		# Return data to user
		logger.debug("Files read")
		return data
	def map_data(self, data):
		""" Maps provided data

		Maps provided data to the inside of the training region. The mapping method is defined by the mapping variable in the AInalysis configuration card. See the documentation for the AInalysis configuration and the documentation documentation for the mapping procedure for more information.

		This method returns 2 values. The first value (mapped) contains the mapped data, whereas the second (has_changed) is a numpy array containing booleans indicating on a per data point basis if the mapping procedure changed the point. If no mapping procedure was defined in the AInalysis configuration (or it was explicitely disabled) this value will be the plain boolean False.

		Parameters
		----------
		data: numpy.ndarray
			Numpy array of shape (nDatapoints, nParameters) containing the data to be mapped
		
		Returns
		-------
		mapped: numpy.ndarray
			Data after mapping procedure. Has the same shape as the provided data array.
		has_changed: numpy.ndarray
			Numpy array of shape (nDatapoints,) containing boolean values indicating on a per point basis is the data point was changed by the mapping procedure. """

		# If AInalysis does not support mapping return data as is
		logger.debug("AInalysis '{}' is mapping data".format(self.ainalysis_id))
		if (self.configuration["mapping"] == False and isinstance(self.configuration["mapping"], bool)) or utils.is_none(self.configuration["mapping"]):
			logger.debug("Data mapping is not enabled, returning data unaltered")
			return (data, False)
		mapped = deepcopy(data)
		# If mapping is "function" send data to map function and return its result
		if self.configuration["mapping"] == "function":
			logger.debug("Data mapping by function")
			functions = SourceFileLoader("module", self.folder+"/functions.py").load_module()
			mapped = functions.map(mapped, self.configuration["parameters"])
		# If mapping is a floating point, perform SUSY-AI mapping
		elif isinstance(self.configuration["mapping"], float):
			logger.debug("Data mapping by mapping list")
			for i in range(len(self.configuration["parameters"])):
				newmax = (self.configuration["parameters"][i][3] - self.configuration["mapping"]*self.configuration["mapping"])
				newmin = (self.configuration["parameters"][i][2] + self.configuration["mapping"]*self.configuration["mapping"])
				if len(mapped.shape) > 1:
					mapped[mapped[:,i] < newmin, i] = newmin
					mapped[mapped[:,i] > newmax, i] = newmax
				else:
					mapped[i] = newmin
					mapped[i] = newmax
		# Raise exception if mapping mode not understood
		else:
			raise exceptions.AInalysisException("Mapping mode was not recognized. Could not map data.")
		has_changed = (np.sum(np.equal(mapped, data)*1.0, axis=1) != len(self.configuration["parameters"]))
		logger.debug("Data is mapped, returning results")
		return (mapped, has_changed)
	def run(self, data, map_data=False, data_ids=None):
		""" Runs the AInalysis over provided data

		The run method takes data as input and uses the internal estimator to create a prediction for it. Data can be mapped following the mapping procedure for this AInalysis by setting map_data to True. Data and prediction results will automatically be transformed by use of the functions in the functions.py file of this AInalysis before prediction and returning the results to the user respectively.

		Results of the estimation run are returned in an instance of the AInalysisResults class.

		Parameters
		----------
		data: numpy.ndarray, string or list of strings
			Data that has to be subjected to the estimator. Can be the raw data (numpy.ndarray), the location of a file to be read by the built-in file reader in the AInalysis or a list of file locations.
		map_data: boolean (default=False)
			Determines if data has to be mapped before prediction. Mapping uses the map_data method of this AInalysis and follows the mapping procedure defined in the configuration file for this AInalysis.
		data_ids: list or numpy.ndarray (default=`None`)
			List or numpy.ndarray of IDs for the data points. By setting this value, results can be extracted from the AInalysisResults object by using the IDs in this list/array instead of by its location in the result array. If `None`, this functionality will not be available.

		Returns
		-------
		result: AInalysisResults instance
			Instance of the AInalysisResults class containing all prediction results for this AInalysis run. """

		# Read files if file paths were provided as data + do some preprocessing
		logger.info("Running AInalysis '{}'".format(self.ainalysis_id))
		logger.debug("Validating input data type and length")
		if isinstance(data, str):
			data = [data]
		if isinstance(data, list):
			if isinstance(data[0], str):
				data_ids = data 
				data = self.read_files(data)
			else:
				data = np.array(data)
		# Check data shape
		data = np.array(data)
		if len(data.shape) == 1:
			data = data.reshape(1,-1)
		if len(data[0]) != len(self.configuration["parameters"]):
			raise exceptions.AInalysisException("Input data should have {} parameters ({} provided)".format(len(self.configuration["parameters"]), len(data[0])))
		logger.debug("Provided {} data points".format(len(data)))
		# Check if data_ids have same length as data (if set)
		if not utils.is_none(data_ids):
			logger.debug("Validating input data_ids")
			if isinstance(data_ids, list) or isinstance(data_ids, np.ndarray):
				if len(data_ids) != len(data):
					raise exceptions.AInalysisException("Length of provided ID list (data_ids) has to be equal to the length of the provided data array.")
			else:
				raise exceptions.AInalysisException("Data IDs have to be provided as a list or array")
			# Transform entries in data_ids to strings
			if isinstance(data_ids, np.ndarray):
				data_ids = data_ids.tolist()
			for i in range(len(data_ids)):
				data_ids[i] = str(data_ids[i])
			logger.debug("Data IDs validated")
		# Check if AInalysis is ready for run
		estimator_was_loaded = self.estimator.is_loaded()
		if not self.can_run():
			raise exceptions.AInalysisException("Cannot run AInalysis {}".format(self.ainalysis_id))
		# Map data if requested
		if map_data:
			logger.info("Mapping data")
			data, mapped = self.map_data(data)
		else:
			mapped = False
		# Create result object
		result = containers.AInalysisResults(self.ainalysis_id, self.configuration, data, data_ids, mapped)
		# Perform data transformation
		functions = SourceFileLoader("module", self.folder+"/functions.py").load_module()
		if "transform" in dir(functions):
			logger.debug("Transforming data")
			data = functions.transform(data)
		# Perform prediction
		logger.info("Perform prediction")
		logger.set_indent("+")
		predictions = self.estimator.predict(data)
		logger.set_indent("-")
		# Perform inverse transformation on prediction results
		if "transform_predictions" in dir(functions):
			logger.debug("Transforming results")
			predictions = functions.transform_predictions(predictions)
		# Store results in AInalysisResults
		result.predictions = predictions
		# Remove estimator from memory if was not loaded
		if not estimator_was_loaded:
			logger.debug("Clearing estimator from memory")
			self.estimator.clear()
		# Return result object
		logger.info("Prediction finished, result returned")
		return result
	def check_for_update(self, print_info=True):
		""" Checks for update of the AInalysis

		Uses the updatechecker.check_ainalysis_update function to check if there is an updated version of this AInalysis available. For this the unique_db_id entry in the AInalysis configuration card is used. If an update is found, this is communicated to the user via the logger module.

		Parameters
		----------
		print_info: boolean (default=True)
			Boolean indicating if information should be printed to terminal

		Returns
		-------
		error: boolean
			Boolean indicating if an error occurred on the server during processing of request. If True, return variable `text` will be the unformatted error message.
		update: boolean
			Boolean indicating if an update is available. If return variable `error` is True, this variable will be `None`.
		text: string
			Return message. If return variable `update` is True, this message will be formatted. """

		if utils.is_none(self.configuration["uniquedbid"]):
			logger.info("No uniquedbid defined in configuration, no update checking will be performed")
			return (True, None, "no uniquedbid defined in configuration, no update checking will be performed")

		error, updatable, txt = updatechecker.check_ainalysis_update(self.configuration["unique_db_id"], self.configuration["ainalysisversion"])
		if print_info:
			print("\n===========================================================================\n|       Always look up if this AInalysis is applicable to your case       |\n|                     Don't forget to cite the author                     |\n===========================================================================\n")
			if not error:
				print(txt+"\n")
		else:
			logger.warning("Could not check for updates of this ainalysis, because: "+txt)
		return (error, updatable, txt)


class AInalysisConfiguration(containers.Configuration):
	""" Interface and validation class for the AInalysis configuraton.

	Interface class that inherits from containers.Configuration. This class is meant to contain the information from AInalysis configuration cards in its configuration property (see containers.Configuration). This derived class builts onto its parent class by implementing validation methods (of which `validate` is the main one). It adds no new properties.

	Any changes made by the validation methods to the configuration are made to the configuration in active memory. Changes are never made to the configuration file itself. """
	def validate(self, validate_checksum=True):
		""" Validates the configuration in the configuration property

		Runs all relevant validation methods of the AInalysisConfiguration class on the loaded configuration.

		Parameters
		----------
		validate_checksum: boolean (default: True)
			Indicates if the checksum in the folder has to be validated as well.

		Returns
		-------
		valid: boolean
			Boolean value indicating if the configuration was good as-is. If any value in the configuration file has to be altered or new ones had to be added, this value will be False. Else it will be True"""

		logger.info("Validating AInalysis configuration")
		valid = True
		# General information
		valid *= self.validate_uniquedbid()
		valid *= self.validate_defaultid()
		valid *= self.validate_version()
		valid *= self.validate_phenoaiversion()
		valid *= self.validate_class()
		valid *= self.validate_libaries()
		valid *= self.validate_type()
		valid *= self.validate_output_and_classes()
		if validate_checksum:
			valid *= self.validate_checksum()
		# Parameters
		valid *= self.validate_parameters()
		# Estimator type specifics
		if self.configuration["type"] == "classifier":
			valid *= self.validate_classifier_calibrated()
			if self.configuration["classifier.calibrated"] == False:
				valid *= self.validate_classifier_calibrate()
				valid *= self.validate_classifier_calibratedata()
		elif self.configuration["type"] == "regressor":
			pass
		# File reading
		valid *= self.validate_filereader()
		# Mapping
		valid *= self.validate_mapping()
		self.validated = True
		if valid:
			logger.info("Configuration valid")
		else:
			logger.warning("Configuration did not fully specify AInalysis behaviour: some behaviour might be infered / set to default")
		return bool(valid)

	# General information validator
	def validate_uniquedbid(self):
		""" Checks for the presence of `unique_db_id` in the AInalysis configuration

		Checks if there is an entry in the configuration named unique_db_id. If not present, this entry will be made (set to `None`). Not providing this value in the configuration does not mean the configuration is invalid, so the returned boolean will always be True (in order to let all validate_* methods have the same interface and behaviour).

		Returns
		-------
		valid: boolean
			Will always be True. """
		if "uniquedbid" not in self.configuration:
			self.configuration["uniquedbid"] = None
			logger.debug("Configuration entry 'uniquedbid' not found; entry is set to `None`")
		return True
	def validate_defaultid(self):
		""" Checks if a default ID (`defaultid`) was provided in the AInalysis configuration

		Checks if there is an entry in the configuration named defaultid. If not present, this entry will be made and set to a random 5 character long string. False will be returned if this happens. In all other cases True will be returned.

		Returns
		-------
		valid: boolean
			Boolean indicating if defaultid was set in the configuration."""
		if "defaultid" not in self.configuration:
			logger.warning("No default id was found. Will create a random string to serve as one.")
			defaultid = utils.random_string(5)
			self.configuration["defaultid"] = defaultid
			return False
		logger.debug("Configuration entry 'defaultid' was validly defined.")
		return True
	def validate_version(self):
		""" Checks for the presence of AInalysis version information (`ainalysisversion`) in the AInalysis configuration.

		Checks if the version number of the AInalysis was provided in the AInalysis configuration. If no version number was provided, the `ainalysisversion` entry will be made in the configuration and set to `1`. This method will always return True, since the configuration does not get less valid by not providing this value.

		Returns
		-------
		valid: boolean
			Will always be True. """
		if "ainalysisversion" not in self.configuration:
			logger.warning("No version number provided for this AInalysis. No checking for updates can be performed.")
			self.configuration["ainalysisversion"] = 1
		else:
			logger.debug("Configuration entry 'ainalysisversion' was validly defined.")
		return True
	def validate_phenoaiversion(self):
		""" Checks if the currently running PhenoAI version (`phenoaiversion`) is actively supported by this AInalysis.

		Checks if the configuration contains an entry `phenoaiversion`. If so the version defined in the AInalysis configuration is checked against the versionnumber of the currently running PhenoAI package. If the configuration explicitely mentions the current PhenoAI version, True is returned. In all other cases False is returned.

		Returns
		-------
		valid: boolean
			Boolean value indicating if currently running PhenoAI versionnumber is mentioned in the AInalysis configuration as actively supported/tested. """
		if "phenoaiversion" not in self.configuration:
			logger.warning("No supported PhenoAI version was defined. Will assume currently used version is supported.")
			return False
		if isinstance(self.configuration["phenoaiversion"], int):
			self.configuration["phenoaiversion"] = [self.configuration["phenoaiversion"]]
		if __version__ not in self.configuration["phenoaiversion"]:
			logger.warning("This AInalysis does not explicitely support the current version of PhenoAI. Program will continue but errors may occur.")
			return False
		logger.debug("Configuration entry 'phenoaiversion' was validly defined.")
		return True
	def validate_class(self):
		""" Checks if the estimator class (`class`) is supported.

		Checks if `class` is defined in the configuration. If so, the value for this entry is checked for support by the current version of PhenoAI. Currently supported values are 'sklearnestimator' and 'kerastfestimator'. Only if the value in the configuration is one of these values, True will be returned. In all other cases a ConfigurationException will be raised. 

		Returns
		-------
		valid: boolean
			Boolean value indicating if the `class` entry exists in the AInalysis configuration and if it is supported by the current version of PhenoAI."""
		if "class" not in self.configuration:
			logger.error("No class was provided for the AInalysis estimator.")
			raise exceptions.ConfigurationException("No class was provided for the AInalysis estimator.")
			return False
		self.configuration["class"] = self.configuration["class"].lower()
		if self.configuration["class"] not in ["sklearnestimator", "kerastfestimator"]:
			logger.error("Class '{}' is not implemented in this version of PhenoAI.".format(self.configuration["class"]))
			raise exceptions.ConfigurationException("Class '{}' is not implemented in this version of PhenoAI.".format(self.configuration["class"]))
			return False
		logger.debug("Configuration entry 'class' was validly defined.")
		return True
	def validate_libaries(self):
		""" Checks if the needed libraries defined in the configuration (`libraries`) are installed with supported versions.

		Checks if the configuration contains a `libraries` entry and loops over all entries in it if it is found. For each of these libraries the version numbers mentioned in the configuration are checked against the version of the library currently installed. If all libraries defined in the configuration are installed with supported versions, True is returned. In all other cases False is returned.

		Returns
		-------
		valid: boolean
			Boolean False if there are required libraries installed with version numbers that are not actively tested / supported. True if all installed and required libraries have the correct version. """

		if "libraries" not in self.configuration:
			logger.warning("No information was provided on needed libraries. This might cause problems during prediction.")
			return False
		# Load libraries and save versions for installed ones
		libraries = {"sklearn": None, "keras": None, "tensorflow": None}
		for lib in libraries:
			try:
				package=importlib.import_module(lib)
				libraries[lib] = package.__version__
			except:
				pass
		unsupported = 0
		for lib in self.configuration["libraries"]:
			if utils.is_none(self.configuration["libraries"][lib]):
				continue
			if libraries[lib] == None:
				logger.error("AInalysis uses library '{}', but it is not installed.".format(lib))
				raise exceptions.AInalysisException("AInalysis uses library '{}', but it is not installed.".format(lib))
				return False
			elif libraries[lib] not in self.configuration["libraries"][lib]:
				logger.warning("Explicitly supported versions of {} don't list the currently installed one ({}). This might cause errors down the line.".format(lib, libraries[lib]))
		if unsupported == 0:
			logger.debug("Configuration entry 'libraries' was validly defined.")
		return (unsupported == 0)
	def validate_type(self):
		""" Checks if the estimator type (`type`) was validly defined in the configuration.

		Checks if an entry `type` was defined in the AInalysis configuration and if it equals 'classifier' or 'regressor'. If so, True is returned. In all other cases a ConfigurationException is raised.

		Returns
		-------
		valid: boolean
			Boolean value indicating if the estimator type (`type` in the configuration) was defined as 'classifier' or 'regressor'. """

		if "type" not in self.configuration:
			logger.error("No estimator type was defined.")
			raise exceptions.ConfigurationException("No estimator type was defined.")
			return False
		if self.configuration["type"] not in ["classifier", "regressor"]:
			logger.error("Estimator type '{}' was not recognized.".format(self.configuration["type"]))
			raise exceptions.ConfigurationException("Estimator type '{}' was not recognized.".format(self.configuration["type"]))
			return False
		logger.debug("Configuration entry 'type' was validly defined.")
		return True
	def validate_output_and_classes(self):
		""" Checks if output value name(s) (`output`) is(are) defined in the AInalysis configuration.

		Checks if there is an entry named `output` in the AInalysis configuration. If not, a ConfigurationException is raised, else True is returned. If the value for this entry is not a list, the entry is converted to a list containing the provided entry. 

		Returns
		-------
		valid: boolean
			Boolean value indicating if `output` was defined in the AInalysis configuration."""
		if "output" not in self.configuration:
			logger.error("No information on estimator output is provided.")
			raise exceptions.ConfigurationException("No information on estimator output is provided.")
			return False
		if not isinstance(self.configuration["output"], str):
			logger.error("Estimator output should have been defined as a string.")
			raise exceptions.ConfigurationException("Estimator output should have been defined as a string.")
			return False

		if self.configuration["type"] == "classifier":
			if "classes" not in self.configuration:
				logger.error("No information on estimator classes is provided.")
				raise exceptions.ConfigurationException("No information on estimator output is provided.")
				return False
			if not isinstance(self.configuration["classes"], dict):
				logger.error("Estimator classes should have been defined as a dictionary.")
				raise exceptions.ConfigurationException("Estimator classes should have been defined as a dictionary.")
				return False
			classes = {}
			for k,v in self.configuration["classes"].items():
				try:
					classes[int(k)] = v
				except:
					logger.error("Classes dictionary should contain integers as keys.")
					raise exceptions.ConfigurationException("Classes dictionary should contain integers as keys.")
					break
			self.configuration["classes"] = classes
			logger.debug("Configuration entry 'classes' was validly defined.")

		logger.debug("Configuration entry 'output' was validly defined.")
		return True
	def validate_checksum(self):
		""" Checks the validness of the AInalysis Checksum.

		Checks if a checksum is stored in the AInalysis folder and calculates if this checksum corresponds to the one calculated from the AInalysis folder as it currently exists. If the checksum either does not exist or any of the calculated checksums does not correspond to the one stored, False is returned. In any other case True is returned. """
		try:
			stored_checksums = io.read_checksum(self.folder+"/checksums.sfv")
		except exceptions.FileIOException:
			logger.warning("No checksum file found. Could not check if data is uncorrupted.")
			return False
		calculated_checksums = utils.calculate_ainalysis_checksums(self.folder)
		invalid_checksums = []
		# Check checksums of important files
		for i in calculated_checksums:
			if i not in stored_checksums:
				logger.warning("No checksum found for '{}' in the checksums.sfv file, could not check if data is uncorrupted.".format(i))
				return False
			if calculated_checksums[i] != stored_checksums[i]:
				invalid_checksums.append(i)
		# Check if checksums were invalid and if so show error (but not fatal)
		if len(invalid_checksums) > 0:
			logger.warning("Checksum of following files where invalid:")
			logger.set_indent("+")
			for i in range(len(invalid_checksums)):
				logger.warning("- {}".format(invalid_checksums[i]))
			logger.warning("This hints at corruption of data (or at the very least: the data has been changed). Use with care and if possible redownload the AInalysis.", "-")
			return False
		if len(invalid_checksums) == 0:
			logger.debug("Checksums are valid.")
		return True
	def validate_classifier_calibrated(self):
		""" Check if information was provided in the configuration on calibration of the estimator.

		Checks if there is an estimator type defined in the configuration (`type`) and if it equals 'classifier'. If so, the presence of `classifier.calibrated` is checked. If it is not present in the configuration False is returned. In all other cases True is returned.

		Returns
		-------
		valid: boolean
			If the estimator is a classifier and calibration information is *not* provided in the AInalysis configuration, this value is False. In all other cases this value is True. """
		if "type" in self.configuration and self.configuration["type"] == "classifier":
			if "classifier.calibrated" not in self.configuration:
				self.configuration["classifier.calibrated"] = False
				logger.warning("No calibration information was provided. Assuming classifier is not calibrated.")
				return False
			self.configuration["classifier.calibrated"] = bool(self.configuration["classifier.calibrated"])
			logger.debug("Configuration entry 'classifier.calibrated' was validly defined.")
		return True
	def validate_classifier_calibrate(self):
		""" Checks if information on calibration of estimator output is provided.

		Checks if the estimator is a classifier. If it is and the classifier is not calibrated, the presence of `classifier.calibrate` is checked. If this entry is not provided, False is returned. In all other cases True is returned.

		If `classifier.calibrate` is indeed found, it is cast to a boolean to avoid problems in other parts of the program. If no `calssifier.calibrate` was found but all requirements (uncalibrated classifier) were fulfilled, the entry is set to False.

		Returns
		-------
		valid: boolean
			If the estimator is an uncalibrated classifier and no information was provided in the `classifier.calibrate` entry of the configuration, this value is False. In all other cases it is False. """
		if "type" in self.configuration and self.configuration["type"] == "classifier":
			if "classifier.calibrated" in self.configuration and self.configuration["classifier.calibrated"] == False:
				if "classifier.calibrate" not in self.configuration:
					self.configuration["classifier.calibrate"] = False
					logger.warning("No information provided on whether or not to calibrate classifier output. Assuming this is not the case.")
					return False
				self.configuration["classifier.calibrate"] = bool(self.configuration["classifier.calibrate"])
			logger.debug("Configuration entry 'classifier.calibrate' was validly defined.")
		return True
	def validate_classifier_calibratedata(self):
		""" Checks if information provided to calibrate estimator output is formatted correctly.

		Checks if the estimator is a classifier (`type`) that is uncalibrated (`classifier.calibrated`) and of which the output has to be calibrated (`classifier.calibrate`). If one of these requirements is not met, True is returned. If all requirements are met, the presence of `classifier.calibrate.bins` and `classifier.calibrate.values` is checked. The values of these entries in the configuration have to be lists with equal length. If the entries do not exist or the lists of equal length is not met, a ConfigurationException is raised. In all other cases, True is returned.

		If values and bins were validly defined, they are converted from list to numpy array.

		Returns
		-------
		valid: boolean
			True if information on classifier output calibration was provided in correct format (see above). If this is not the case, this value is False. In all other cases this value is True. """
		if "type" not in self.configuration or self.configuration["type"] != "classifier":
			return True
		if "classifier.calibrated" not in self.configuration or self.configuration["classifier.calibrated"] == True:
			return True
		if "classifier.calibrate" not in self.configuration or self.configuration["classifier.calibrate"] == False:
			return True
		if "classifier.calibrate.bins" not in self.configuration:
			self.configuration["classifier.calibrate"] = False
			logger.error("No information on calibration bins is provided. No calibration will take place.")
			raise exceptions.ConfigurationException("No information on calibration bins is provided. No calibration will take place.")
			return False
		if "classifier.calibrate.values" not in self.configuration:
			self.configuration["classifier.calibrate"] = False
			logger.warning("No information on calibration values is provided. No calibration will take place.")
			raise exceptions.ConfigurationException("No information on calibration values is provided. No calibration will take place.")
			return False
		if not isinstance(self.configuration["classifier.calibrate.bins"], list) and not isinstance(self.configuration["classifier.calibrate.bins"], np.ndarray):
			self.configuration["classifier.calibrate"] = False
			logger.error("Calibration bin information is not provided as a list. No calibration will take place.")
			raise exceptions.ConfigurationException("Calibration bin information is not provided as a list. No calibration will take place.")
			return False
		if not isinstance(self.configuration["classifier.calibrate.values"], list) and not isinstance(self.configuration["classifier.calibrate.values"], np.ndarray):
			self.configuration["classifier.calibrate"] = False
			logger.error("Calibration values information is not provided as a list. No calibration will take place.")
			raise exceptions.ConfigurationException("Calibration values information is not provided as a list. No calibration will take place.")
			return False
		if len(self.configuration["classifier.calibrate.values"]) != len(self.configuration["classifier.calibrate.bins"]):
			self.configuration["classifier.calibrate"] = False
			logger.error("Number of calibration bins and values do not correspond. No calibration will take place.")
			raise exceptions.ConfigurationException("Number of calibration bins and values do not correspond. No calibration will take place.")
			return False
		self.configuration["classifier.calibrate.values"] = np.array(self.configuration["classifier.calibrate.values"])
		self.configuration["classifier.calibrate.bins"] = np.array(self.configuration["classifier.calibrate.bins"])
		logger.debug("Configuration entry 'classifier.calibrate.bins' was validly defined.")
		logger.debug("Configuration entry 'classifier.calibrate.values' was validly defined.")
		return True
	def validate_filereader(self):
		""" Checks if a valid filereader was provided in the AInalysis configuration.

		Checks if `filereader` was provided in the AInalysis configuration. If not, False is returned. If it is provided, it has to be "function", a list or `None`, otherwise False is returned. If the entry is set to "function", the `data` function has to be defined in the "functions.py" file in the AInalysis folder, which takes 1 input argument (file location). If this function was not found or the function takes a different kind of parameters False is returned.

		If the `filereader` entry is a list, it has to be a list of lists of length 2 following the format [BLOCK, SWTICH], indicating the blocks and switches from the entries in a .slha file from which the information has to be extracted. If this format is violated, False is returned.

		If False is returned, the `filereader` entry is set to None.

		In all other cases True is returned.

		Returns
		-------
		valid: boolean
			True if a valid filereader was defined (see above). If not, this value is False. """
		if "filereader" not in self.configuration:
			self.configuration["filereader"] = None
			logger.warning("No readmode defined.")
			return False
		if isinstance(self.configuration["filereader"], bool) and not self.configuration["filereader"]:
			self.configuration["filereader"] = None
		if self.configuration["filereader"] == "function":
			try:
				functions = SourceFileLoader("module", self.folder+"/functions.py").load_module()
				narguments = len(signature(functions.read).parameters)
				if narguments != 1:
					self.configuration["filereader"] = None
					logger.warning("Function for data reading 'read' takes {} arguments, 1 argument expected. No automated file reading can take place.".format(narguments))
					return False
			except FileNotFoundError:
				# File functions.py was not found in AInalysis folder
				self.configuration["filereader"] = None
				logger.warning("No functions file could be found in AInalysis folder. No automated file reading can take place.")
				return False
			except AttributeError:
				# No function defined called data
				self.configuration["filereader"] = None
				logger.warning("No reader function 'read' defined in functions file. No automated file reading can take place.")
				return False
		elif self.configuration["filereader"] == "None":
			self.configuration["filereader"] = None
		elif isinstance(self.configuration["filereader"], list):
			for i in range(len(self.configuration["filereader"])):
				if len(self.configuration["filereader"][i]) != 2:
					self.configuration["filereader"] = None
					logger.warning(".slha readerlist has an invalid format. No automated file reading can take place")
					return False
			# Check if length of reader list is equal to the number of parameters
			if len(self.configuration["filereader"]) != len(self.configuration["parameters"]):
				self.configuration["filereader"] = None
				logger.warning("Length of .slha readerlist should correspond to the length of the parameter list.")
				return False
		elif not utils.is_none(self.configuration["filereader"]):
			logger.warning("Readmode '{}' was not recognized. No reading can take place.".format(self.configuration["filereader"]))
			self.configuration["filereader"] = None
			return False
		logger.debug("Configuration entry 'filereader' was validly defined.")
		
		# validate filereader formats
		if "filereader.formats" not in self.configuration:
			self.configuration["filereader.formats"] = None
		if utils.is_none(self.configuration["filereader.formats"]):
			logger.warning("Filereader.formats not defined / defined as None, unclear which file formats can be read.")
			return False
		elif isinstance(self.configuration["filereader.formats"], list):
			formats = self.configuration["filereader.formats"]
			for i in range(len(formats)):
				if not isinstance(formats[i], str):
					formats[i] = None
					logger.warning("Filereader.formats ill defined, should be a string or list of strings.")
			for i in range(len(formats)-1,-1,-1):
				if utils.is_none(formats[i]):
					del(formats[i])
			if len(formats) == 0:
				logger.warning("No valid formats defined, no file format validation will be performed.")
				self.configuration["filereader.formats"] = None
				return False
			self.configuration["filereader.formats"] = formats
		elif isinstance(self.configuration["filereader.formats"], str):
			self.configuration["filereader.formats"] = [self.configuration["filereader.formats"]]
		logger.debug("Configuration entry 'filereader.formats' was validly defined.")
		return True
	def validate_mapping(self):
		""" Checks if information on data mapping is provided in the configuration.

		Checks for the presence of `mapping` in the AInalysis configuration. If it is present, but is not of type boolean, type float or equals "function", False is returned. If it equals "function", but no valid `map` function is defined in the functions.py file in the AInalysis folder (valid means: existing and taking 1 argument, namely the data array), False is returned. In all other cases True is returned.

		If the entry is the boolean True it is changed to 0.0. This does not change the functionality of the code, but makes interpretation of the entry easier. If no entry was found `mapping` is set to False.

		Returns
		-------
		valid: boolean
			True is `mapping` is set in the configuration and is of valid format (boolean, float or equalling "function"). In all other cases this value is False. """
		if "mapping" not in self.configuration:
			self.configuration["mapping"] = False
			logger.warning("No information was provided if mapping should take place. Assuming not.")
			return False
		if not isinstance(self.configuration["mapping"], bool) and self.configuration["mapping"]!="function" and not isinstance(self.configuration["mapping"], float):
			self.configuration["mapping"] = False
			logger.warning("Mapping mode was not recognized. Has to be False, 'function' or a floating point number. Mapping is disabled for this AInalysis.")
			return False
		if self.configuration["mapping"] == "function":
			try:
				functions = SourceFileLoader("module", self.folder+"/functions.py").load_module()
				narguments = len(signature(functions.map).parameters)
				if narguments != 1:
					self.configuration["mapping"] = False
					logger.warning("Function for data mapping 'map' takes {} arguments, 1 argument expected. No data mapping can take place.".format(narguments))
					return False
			except FileNotFoundError:
				# File functions.py was not found in AInalysis folder
				self.configuration["mapping"] = False
				logger.warning("No functions file could be found in AInalysis folder. No data mapping can take place.")
				return False
			except AttributeError:
				# No function defined called data
				self.configuration["mapping"] = False
				logger.warning("No 'map' function defined in functions file. No data mapping can take place.")
				return False
		if self.configuration["mapping"] == True and isinstance(self.configuration["mapping"], bool):
			self.configuration["mapping"] = 0.0
		logger.debug("Configuration entry 'mapping' was validly defined.")
		return True
	def validate_parameters(self):
		""" Checks if information on input parameters is provided in the AInalysis configuration.

		Checks if `parameters` is set in the AInalysis configuration. If not, a ConfigurationException is raised. If it is set, it has to be a list consisting out of lists of length 3 with entries [NAME, MINIMUM, MAXIMUM]. If this format is broken in *any* of the list entries, a ConfigurationException is raised. In all other cases True is returned.

		Returns
		-------
		valid: boolean
			True is `parameters` entry in the AInalysis configuration was set and follows the required format (see above). If not, this value equals False. """
		if "parameters" not in self.configuration:
			logger.error("No parameter information was provided.")
			raise exceptions.ConfigurationException("No parameter information was provided.")
			return False
		for i in range(len(self.configuration["parameters"])):
			if not isinstance(self.configuration["parameters"][i], list) or len(self.configuration["parameters"][i]) != 4:
				logger.error("Parameter definitions dont follow the [NAME, UNIT, MIN, MAX] format.")
				raise exceptions.ConfigurationException("Parameter definitions dont follow the [NAME, UNIT, MIN, MAX] format.")
				return False
		logger.debug("Configuration entry 'parameters' was validly defined.")
		return True

