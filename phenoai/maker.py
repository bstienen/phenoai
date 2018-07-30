""" With the maker module existing sklearn and keras estimators can be converted into AInalyses to be used in PhenoAI. """

import os
import shutil
import datetime
try:
	import cPickle as pkl
except:
	import pickle as pkl

import numpy as np
import matplotlib.pyplot as plt

from . import __versionnumber__,__version__
from . import exceptions
from . import utils
from . import logger
from .ainalyses import AInalysisConfiguration, AInalysis
from . import estimators


class AInalysisMaker:
	""" The AInalysisMaker takes all required information to create an AInalysis and stores this in the correct format to be used in PhenoAI. The AInalysisMaker explicitely does *not* create estimators, these should be made by the user using sklearn or keras.

	Properties
	----------
	configuration: ConfigurationMaker object
		Object to construct and store the configuration.yaml file for the AInalysis.
	data: dictionary
		Dictionary containing data names (keys) and numpy arrays with the data itself (values) to be stored within the AInalysis. Data should be added via the .add_data() method of this object.
	estimator: None or sklearn estimator or keras model
		The estimator to be used in the AInalysis. To be set via the .set_estimator() method
	flags: dictionary
		Internal flag system to keep track of all settings that are set validly.
	location: string
		Location where the AInalysis has to be stored. To be set exclusively via the constructor.

	Constructor arguments
	---------------------
	default_id: string
		ID the AInalysis should have if the user is not providing one. Has to be unique in running PhenoAI.
	location: string
		Location where the AInalysis has to be stored.
	versionnumber: integer
		Version number of the AInalysis (default: 1)
	overwrite: boolean (default: False)
		If the location already exists and contains a configuration.yaml file, all AInalysis related files are overwritten if this setting is set to True. If set to False and the location exists, an exceptions.MakerError is raised."""
	def __init__(self, default_id, location, versionnumber=1, overwrite=False):
		# Clean location from closing '/' if provided
		if location[-1] == "/":
			location = location[:-1]
		# Check if location already exists
		if os.path.isdir(location):
			# Raise error if overwrite == False and the location contains a valid AInalysis
			if overwrite == False and os.path.exists(location+"/configuration.yaml"):
				logger.error("Location '{}' already stores an AInalysis (overwrite is set to False).".format(location))
				raise exceptions.MakerError("Location '{}' already stores an AInalysis (overwrite is set to False).".format(location))
		# Make location if needed
		else:
			logger.debug("Location '{}' is made".format(location))
			os.mkdir(location)

		# Create internal variables
		self.estimator = None
		self.aboutmaker = AboutMaker()
		self.location = location
		self.data = {}

		# Set flags dictionary
		self.flags = {"application_box":False,"estimator":False,"estimator_type":False,"estimator_configuration":False}

		# Create ConfigurationMaker
		self.configuration = ConfigurationMaker()

		# Set default_id in ConfigurationMaker
		self.configure("defaultid", default_id)
		self.set_version(versionnumber)
		self.functions = None

	# Load existing AInalysis
	def load(self, location, load_data=True, load_estimator=False, load_functions=True):
		""" Load a secundary AInaysis as template for the new one

		This function allows the user to select an existing AInalysis and load its configuration, data, estimator and functions into the maker instance. It was written especially for the creation of new versions of the same AInalysis, but can be used in broader context.
		
		Parameters
		----------
		location: string
			Path to the AInalysis to be loaded
		load_data: boolean (default=`True`)
			Indicates if data should be loaded from the AInalysis. If set to `True`, all data will be loaded and copied to the new AInalysis folder (unless overwritten by use of the add_data method).
		load_estimator: boolean (default=`True`)
			Indicates if the estimator of the existing AInalysis should be loaded.
		load_functions: boolean (default=`True`)
			Indicates if the functions.py file of the existing AInalysis should be copied. If set to `False` a new functions.py template will be created in the AInalysis folder. """
		# Clean location indication
		if location[-1] == '/':
			location = location[:-1]
		# Load AInalysis into AInalysis object to read it out afterwards
		a = AInalysis(location, load_estimator)
		# Copy configuration from AInalysis
		self.configuration.configuration = a.configuration.configuration
		# Copy data
		if load_data and os.path.exists(location+"/data"):
			for filename in os.listdir(location+"/data"):
				if filename.endswith(".npy"): 
					dataname = '.'.join(filename.split('.')[:-1])
					self.data[dataname] = np.load(location+'/data/'+filename)
		# Copy estimator
		if load_estimator:
			self.estimator = a.estimator.est
			self.flags["estimator"] = True
			if "type" in self.configuration.configuration:
				self.flags["estimator_type"] = True
				self.flags["estimator_configuration"] = True
		# Set flags
		if "parameters" in self.configuration.configuration:
			self.flags["application_box"] = True
		# Copy content of functions.py
		if load_functions:
			with open(location+"/functions.py", 'r') as funcfile:
				self.functions = funcfile.read()

	# Provide about information
	def set_about(self, name, description):
		""" Sets about information for the about.html file

		With this function the meta information about the AInalysis can be set. It is not interpreted by the Maker instance in any way, it is purely meant for interpretation of the AInalysis by the user. 

		Parameters
		----------
		name: string
			Name of the AInalysis
		description: string
			Description of the AInalysis"""
		self.aboutmaker.set_name(name)
		self.aboutmaker.set_description(description)
	def add_author(self, name, email=None):
		""" Adds an author by name and email to the about.html file

		Only authors of the AInalysis should be added in this way. Authors of the original data can be linked via the .add_paper method.

		Parameters
		----------
		name: string
			Full name of the author
		email: string (default=`None`)
			The emailaddress of the author. If set to `None`, no email will be displayed. """
		self.aboutmaker.add_author(name, email)
	def add_paper(self, paper_id, paper_url):
		""" Adds a reference to the about.html file

		This method can be used to reference papers which supplied the required data for example.

		Parameters
		----------
		paper_id: string
			Name of the paper or ID (e.g. arxiv number or DOI)
		paper_url: string
			URL via which the paper can be accessed. """
		self.aboutmaker.add_paper(paper_id, paper_url)

	# Set accepted dependency versions
	def set_dependency_version(self, dependency, version, add=True):
		""" Sets/adds the supported version for a dependency

		Parameters
		----------
		dependency: string
			Name of the dependency. Supported: phenoai, sklearn, tensorflow, keras
		version: string or list
			Supported version for the provided dependency. Multiple versions van be provided as a list.
		add: boolean (default=`True`)
			If set to `True`, the provided version(s) for the provided dependency is(are) added to the list of already present versions for said dependency. If set to `False` the current list is replaced by the provided version(s)."""
		if dependency == "phenoai":
			if add and isinstance(self.configuration["phenoaiversion"], list):
				if isinstance(version, list):
					self.configuration["phenoaiversion"].extend(version)
				else:
					self.configuration["phenoaiversion"].append(version)
			elif add:
				if isinstance(version, list):
					version.append(self.configuration["phenoaiversion"])
					self.configuration["phenoaiversion"] = version
				else:
					self.configuration["phenoaiversion"] = [self.configuration["phenoaiversion"], version]
			else:
				self.configuration["phenoaiversion"] = version
		elif dependency in ["sklearn", "tensorflow", "keras"]:
			if dependency not in self.configuration["libraries"]:
				self.configuration["libraries"][dependency] = version
			else:
				if add and isinstance(self.configuration["libraries"][dependency], list):
					if isinstance(version, list):
						self.configuration["libraries"][dependency].extend(version)
					else:
						self.configuration["libraries"][dependency].append(version)
				elif add:
					if isinstance(version, list):
						version.append(self.configuration["libraries"][dependency])
						self.configuration["libraries"][dependency] = version
					else:
						self.configuration["libraries"][dependency] = [self.configuration["libraries"][dependency], version]
		else:
			logger.error("Dependency '{}' unknown, can only set dependency for ['phenoai', 'keras', 'sklearn', 'tensorflow']".format(dependency))
			raise exceptions.MakerError("Dependency '{}' unknown, can only set dependency for ['phenoai', 'keras', 'sklearn', 'tensorflow']".format(dependency))

	# Version number setter
	def set_version(self, versionnumber):
		""" Define the version number of the AInalysis

		If the supplied version number is not an integer and could not be cast to one, an exceptions.MakerError is raised.
		
		Parameters
		----------
		versionnumber: integer
			Version number of the AInalysis """
		if not isinstance(versionnumber, int):
			try:
				versionnumber = int(versionnumber)
			except:
				logger.error("Version number should be an integer.")
				raise exceptions.MakerError("Version number should be an integer.")
				return False
		self.configure("ainalysisversion", versionnumber)
	# Defining estimator
	def set_estimator(self, estimator, estimator_type, output, classes=None):
		""" Sets the estimator and settings of the estimator to be used in the AInalysis.

		Parameters
		----------
		estimator: sklearn estimator or keras model
			Estimator object to be stored in the AInalysis for usage.
		estimator_type: "classifier" or "regressor"
			Indicates if the estimator is to be used as a classifier or a regressor. Is internally handled via the .set_estimator_type() method.
		output: string
			String explaining what the output represents
		classes: dictionary (default: None)
			Dictionary specifying what the output classes represent. Should only be defined if the estimator is a classifier. If the estimator is an estimator, this dictionary should follow format {class: name, class: name, ...}. """
		# Check which package the estimator belongs to
		m = estimator.__module__
		if "sklearn" in m:
			# Set Estimator class in configuration
			self.configure("class","sklearnestimator")
			e = estimators.SklearnEstimator()
			libs = e.libraries
		elif "keras" in m:
			# Set Estimator class in configuration
			self.configure("class","kerastfestimator")
			e = estimators.KerasTFEstimator()
			libs = e.libraries
		else:
			# Raise exception
			logger.error("Package defining the estimator could not be identified")
			raise exceptions.MakerError("Package defining the estimator could not be identified")
		# Set estimator package versions
		for l in libs:
			self.set_dependency_version(l, libs[l])
		# Store estimator internally and set flag
		self.estimator = estimator
		self.flags["estimator"] = True
		logger.info("Estimator set for AInalysis")

		# Check estimator_type
		if estimator_type != "regressor" and estimator_type != "classifier":
			logger.error("estimator_type should be either 'classifier' or 'regressor'.")
			raise exceptions.MakerError("estimator_type should be either 'classifier' or 'regressor'.")
		# Set estimator_type
		self.set_estimator_type(estimator_type)

		# Set what the estimator is trying to estimate
		if not (isinstance(output, str)):
			logger.error("Estimator output should be defined as a string.")
			raise exceptions.MakerError("Estimator output should be defined as a string.")
		if not isinstance(classes, dict) and not utils.is_none(classes):
			logger.error("Classes should be defined as a dictionary or as None.")
			raise exceptions.MakerError("Classes should be defined as a dictionary or as None.")
		self.configure("output", output)
		if not utils.is_none(classes):
			c = {}
			for k,v in classes.items():
				try:
					c[int(k)] = v
				except:
					logger.error("Classes should be integers.")
					raise exceptions.MakerError("Classes should be integers.")
					break
			self.configure("classes", classes)
	def set_estimator_type(self, estimator_type):
		""" Defines the estimator type in the configuration of the AInalysis.

		In calling this method, the flags 'estimator_type' (for regressors and classifiers) and 'estimator_configuration' (for regressors only) are set to True.

		Parameters
		----------
		estimator_type: "classifier" or "regressor"
			Defines if the estimator of the AInalysis is a classifier or a regressor."""
		# Check if estimator type is defined correctly
		if estimator_type == "classifier":
			# Estimator is a classifier
			self.flags["estimator_type"] = True
		elif estimator_type == "regressor":
			# Estimator is a regressor
			self.flags["estimator_type"] = True
			self.flags["estimator_configuration"] = True
		else:
			# Raise exception because type is unknown
			logger.error("Estimator type '{}' unknown, must be 'classifier' or 'regressor'.".format(estimator_type))
			raise exceptions.MakerError("Estimator type '{}' unknown, must be 'classifier' or 'regressor'.".format(estimator_type))
		# Set estimator type in configuration
		self.configure("type", estimator_type)
		logger.info("Estimator type set for AInalysis")

	def set_classifier_settings(self, calibrated=False, do_calibrate=False, calibration_truth=None, calibration_pred=None, calibration_nbins=100):
		""" Defines the classifier classes and calibration settings for the estimator if it is a classifier

		If calibration has to be done by PhenoAI (as defined when do_calibration == True), the needed arrays for this calibration are created from the calibration_truth, calibration_prediction and calibration_nbins via the generate_calibration_arrays function in this module.

		Parameters
		----------
		calibrated: boolean (default: False)
			Boolean indicating if the classifier is calibrated, i.e. if the output can be interpreted as a proper probability.
		do_calibrate: boolean (default: False)
			Boolean indicating if the classifier output has to be calibrated by PhenoAI after prediction. This setting is ignored if 'calibrated' was set to True. Calibration can only take place for classifiers creating predictions on two classes.
		calibration_truth: None or numpy.ndarray (default: None)
			Defines true labels used in calibration. Should have same length as 'calibration_prediction' and has to be set as numpy.ndarray of 'do_calibrate' is True. This setting is ignored if 'do_calibrate' is set to False.
		calibration_prediction: None or numpy.ndarray (default: None)
			Predictions belonging to the true labels ('calibration_truth') used in calibration. Should have same length as 'calibration_truth' and has to be set as numpy.ndarray of 'do_calibrate' is True. This setting is ignored if 'do_calibrate' is set to False.
		calibration_nbins: integer (default: 100)
			Number of bins to create calibrations for (i.e. number of unique probabilities to be created). This setting is ignored if 'do_calibrate' is set to False."""

		# Check if classifier is calibrated
		if not calibrated:
			self.configure("classifier.calibrated", False)
			# Check if output has to be calibrated by PhenoAI
			if do_calibrate:
				self.configure("classifier.calibrate", True)
				# Create calibration arrays
				logger.info("Create calibration arrays")
				bins, values = generate_calibration_arrays(calibration_truth, calibration_pred, calibration_nbins)
				# Store calibrate information
				self.configure("classifier.calibrate.bins", bins.tolist())
				self.configure("classifier.calibrate.values", values.tolist())
			else:
				self.configurate("classifier.calibrate", False)
		else:
			self.configure("classifier.calibrated", True)
			self.configure("classifier.calibrate", False)
		self.flags["estimator_configuration"] = True
		logger.info("Classifier settings set for AInalysis")

	# Data
	def set_application_box(self, data, names, units):
		""" Defines the box within which the training data was sampled and therefore within which the estimator is expected to work

		If this method is validly called an execution succeeded, the internal 'application_box' flag is set to True.

		Parameters
		----------
		data: numpy.ndarray
			Numpy.ndarray of shape (nDatapoints, nParameters) containing the training data.
		names: list of strings
			List of the parameter names. Length of this list should match the number of parameters defined by `data` (= nParameters).
		units: list of strings
			List of units for the parameters defined in `names`. Length of this list should match the number of parameters defined by `data` (= nParameters). """

		# Check if data is a numpy array
		if not isinstance(data, np.ndarray):
			logger.error("Data for application box definition should be numpy.ndarray of shape (nDatapoints, nFeatures).")
			raise exceptions.MakerError("Data for application box definition should be numpy.ndarray of shape (nDatapoints, nFeatures).")
		# Check if names is a list
		if not isinstance(names, list):
			logger.error("Names should be a list naming the features of the data array.")
			raise exceptions.MakerError("Names should be a list naming the features of the data array.")
		# Check if names fits data shapewise
		if len(data[0]) != len(names):
			logger.error("Number of features in the data array should match the number of names in the names array.")
			raise exceptions.MakerError("Number of features in the data array should match the number of names in the names array.")
		# Create parameters variable
		mins = np.amin(data, axis=0)
		maxs = np.amax(data, axis=0)
		parameters = [[names[i], units[i], mins[i], maxs[i]] for i in range(len(names))]
		# Store parameters in configuration
		self.configure("parameters",parameters)
		self.flags["application_box"] = True
		logger.info("Application box for AInalysis is defined")

	def add_data(self, X, y, name):
		""" Adds data to the AInalysis to be stored in the data subfolder of the AInalysis.

		Parameters
		----------
		X: numpy.ndarray
			Numpy.ndarray of shape (nDatapoints, nParameters) containing the data.
		y: numpy.ndarray
			Numpy.ndarray of shape (nDatapoints, ) containing the true labeling of the data provided in 'X'.
		name: string
			Name of the data, e.g. 'training', 'testing' or 'validation'. Data will be stored as [name]_data and [name]_labeling."""
		self.data[name+"_data"] = X
		self.data[name+"_labeling"] = y
		logger.info("Dataset '{}' is added".format(name))

	# Filereader
	def set_filereader(self, filereader, formats=None):
		""" Defines the method through which files are read by the AInalysis.

		This method can only be called after the .set_application_box() method is successfully called.

		Parameters
		----------
		filereader: boolean, 'function' (str) or list
			Defines the method through which files are read by the AInalysis. If set as a boolean, False will disable filereading by the AInalysis, True will outsource the file reading to the 'read' function in the functions.py file of the AInalysis. This can also be done by setting this argument to 'function'. Alternatively this argument can also be set to a list of shape [BLOCK, SWITCH]*N, defining the reader interface for .slha files. The BLOCK should be a string and SWITCH should be an integer or a list of integers (for matrices defined in .slha files). N is the number of parameters accepted by the estimator and should match the number of parameters defined via the .set_application_box() method.
		formats: string, list of strings (default: `None`)
			Defines which file formats can be read by the filereader."""
		# Check if application box is already defined
		if utils.is_none(self.configuration["parameters"]):
			logger.error("File reader can only be defined after defining the application box via .set_application_box()")
			raise exceptions.MakerError("File reader can only be defined after defining the application box via .set_application_box()")
		# Check if filereader is boolean
		if isinstance(filereader, bool):
			# If True, user has to define a function
			if filereader:
				self.configure("filereader", "function")
			# Otherwise no filereader is defined
			else:
				self.configure("filereader", False)
		# Check if filereader is a string and if it equals "function", if so filereader by function is defined
		elif isinstance(filereader, str) and filereader == "function":
			self.configure("filereader", "function")
		# Check if filereader is a list
		elif isinstance(filereader, list):
			# Loop over all list elements
			listformaterror = False
			# Verify for each element in the filereader list if the format is correct
			for item in filereader:
				if not isinstance(item[0], str):
					listformaterror = True
				if not (isinstance(item[1], int) or isinstance(item[1], list) or isinstance(item[1], tuple)):
					listformaterror = True
				if not isinstance(item[1], int) and len(item[1]) != 2:
					listformaterror = True
			if listformaterror:
				logger.error("List definitions of filereader should have format [BLOCK, SWITCH]*N, where BLOCK is a string, SWITCH an integer, list or tuple of length 2 and N the number of features in the data.")
				raise exceptions.MakerError("List definitions of filereader should have format [BLOCK, SWITCH]*N, where BLOCK is a string, SWITCH an integer, list or tuple of length 2 and N the number of features in the data.")
			# Check if length of list is equal to number of features in data
			if len(filereader) != len(self.configuration["parameters"]):
				logger.error("Length of the filereader list should match the number of features in the application box.")
				raise exceptions.MakerError("Length of the filereader list should match the number of features in the application box.")
			self.configure("filereader", filereader)
		else:
			logger.error("Filereader formats should be defined as a string or a list of strings, where each string defines a file extension.")
			raise exceptions.MakerError("Filereader formats should be defined as a string or a list of strings, where each string defines a file extension.")
		# Define file format
		if not isinstance(formats, str) and not isinstance(formats, list) and not utils.is_none(formats):
			logger.error("Filereader formats should be defined as a string or a list of strings, where each string defines a file extension.")
			raise exceptions.MakerError("Filereader formats should be defined as a string or a list of strings, where each string defines a file extension.")
		if isinstance(formats,list):
			for f in formats:
				if not isinstance(f, str):
					logger.error("Filereader formats should be defined as a string or a list of strings, where each string defines a file extension.")
					raise exceptions.MakerError("Filereader formats should be defined as a string or a list of strings, where each string defines a file extension.")
		self.configure("filereader.formats",formats)
		logger.info("Filereader is defined")

	# Mapping
	def set_mapping(self, mapping=False):
		""" Defines if the AInalysis should allow mapping and if so, what the mapping border should be.

		Parameters
		----------
		mapping: boolean, 'function' (str) of float (default: False)
			Sets the mapping capabilities of the AInalysis. If set to False, no mapping will take place. If set to True, all mapping will be done to the border to the application box. Can also be set to a floating point number between 0.0 and 0.5, where 0.0 indicates mapping to the border of the application box and 0.5 indicates mapping to the center of the application box. If set to 'function' (string), the map() function in the functions.py file will be used for mapping."""
		if isinstance(mapping, bool):
			self.configure("mapping", mapping)
		elif isinstance(mapping, float) and mapping <= 0.5 and mapping >= 0.0:
			self.configure("mapping", mapping)
		elif mapping == "function":
			self.configure("mapping", mapping)
		else:
			raise exceptions.MakerError("Mapping should be a boolean, 'function' (str) or a float between 0.0 and 1.0")
		logger.info("Mapping is set to '{}'".format(mapping))

	def configure(self, parameter, value):
		""" Sets configuration parameters

		Redirects input arguments to the .set() method of the ConfigurationMaker instance in the configuration property of this object.

		Parameters
		----------
		parameter: string
			Name of the parameter to be set in the configuration.
		value: *
			Value of the parameter to be set in the configuration."""
		self.configuration.set(parameter, value)
	def validate_configuration(self):
		""" Validate the configuration 

		Calls the AInalysisConfiguration.validate() parent method of the ConfigurationMaker instance in the configuration property of this object.

		Returns
		-------
		valid: boolean
			Boolean value indicating if the configuration was good as-is. If any value in the configuration file has to be altered or new ones had to be added, this value will be False. Else it will be True. """
		logger.info("Validate configuration")
		v = self.configuration.validate()
		logger.info("Configuration validated")
		return v

	def make(self):
		""" Creates the AInalysis

		Creats the AInalysis at the location provided in construction of this object. Will raise an exceptions.MakerError if not all flags are True."""

		logger.info("Create AInalysis")

		# Check if about page can be made
		if not self.aboutmaker.is_configured():
			logger.error("Cannot make AInalysis, because not all meta information has been provided (see errors above).")
			raise exceptions.MakerError("Cannot make AInalysis, because not all meta information has been provided (see errors above).")

		# Check if all flags are True
		for f in self.flags:
			if not self.flags[f]:
				raise exceptions.MakerError("Could not make the AInalysis, the '{}' flag is not set to True.".format(f))

		# Estimator
		# Store sklearn estimator
		if self.configuration["class"] == "sklearnestimator":
			with open(self.location+"/estimator.pkl", "wb") as f:
				pkl.dump(self.estimator, f)
		# Store keras estimator
		elif self.configuration["class"] == "kerastfestimator":
			self.estimator.save(self.location+"/estimator.hdf5")
		logger.debug("Estimator stored")

		# If data is defined, make data folder
		if len(self.data) > 0 and not os.path.exists(self.location+"/data"):
			os.mkdir(self.location+"/data")
			# Create data .npy files
			for d in self.data:
				np.save(self.location+"/data/{}.npy".format(d), self.data[d])
			logger.debug("Datasets are stored")

		# Create functions.py
		with open(self.location+"/functions.py","w") as f:
			if utils.is_none(self.functions):
				f.write('import numpy as np\n')
				f.write('\n')
				f.write('# FILE READER FUNCTION\n')
				f.write('# Reads files into data arrays.\n')
				f.write('# Takes filepaths in as a list and returns the content of the files in the form of a numpy.ndarray of shape (nDatapoints, nParameters).\n')
				f.write('# This function is used if "filereader" is set to "function" in the configuration.yaml file.\n')
				f.write('def read(data):\n')
				f.write('	return data\n')
				f.write('\n')
				f.write('# TRANSFORM DATA FUNCTION\n')
				f.write('# Transforms the data before it is subjected to prediction routines.\n')
				f.write('# Takes in data as a numpy.ndarray with shape (nDatapoints, nParameters) and should return data in the same shape.\n')
				f.write('# This function is used if defined here.\n')
				f.write('def transform(data):\n')
				f.write('	return data\n')
				f.write('\n')
				f.write('# TRANSFORM PREDICTIONS FUNCTION\n')
				f.write('# Transforms the predictions before it is outputted by the AInalysis.\n')
				f.write('# Takes in predictions as a numpy.ndarray with shape (nDatapoints, ) and should return predictions in the same shape.\n')
				f.write('# This function is used if defined here.\n')
				f.write('def transform_predictions(data):\n')
				f.write('	return data\n')
				f.write('\n')
				f.write('# DATA MAPPING FUNCTION\n')
				f.write('# Allows mapping of data via arbitraty function.\n')
				f.write('# Takes in data as a numpy.ndarray with shape (nDatapoints, nParameters) and should return data in the same shape.\n')
				f.write('# This function is used if "mapping" is set to "function" in the configuration.yaml file.\n')
				f.write('def map(data):\n')
				f.write('	return data\n')
			else:
				f.write(self.functions)
		logger.debug("functions.py file is created")

		# Create configuration.yaml
		self.configuration.save(self.location+"/configuration.yaml")
		logger.debug("Configuration is stored in configuration.yaml file")

		# Create about page
		self.aboutmaker.make(self.configuration, self.location)

		# Create checksums
		update_checksums(self.location)
		logger.debug("Checksums are created")

		# Closing statements
		logger.info("AInalysis is successfully created")
		logger.warning("Don't forget to alter the functions.py file to specify a file reader function / mapping function or to perform data transformations before and after predictions!")
		logger.warning("If the functions.py file is altered, call the update_checksums([ainalysisfolder]) function of this module to update the checksums file.")

class AboutMaker:
	""" The AboutMaker is able to create about.html files that summarize AInalyses in a user readable format.

	An AboutMaker instance is automatically created and managed by the AInalysisMaker and any function of the AboutMaker has an interface in the AInalysisMaker. In normal circumstances, you therefore should not have to use instances of this specific class directly.

	Properties
	----------
	authors: list of strings
		List of author names
	configuration: dictionary
		Configuration dictionary as made by a ConfigurationMaker instance or as loaded by an AInalysisConfiguration instance.
	contact: list of strings/`None`s
		List of emailaddresses corresponding to the list of authors. If an author has no emailaddress associated with it, the entry will be `None` instead.
	description: string
		Description of the AInalysis
	location: string
		Location where the about.html page will be stored.
	name: string
		Name of the AInalysis, will become the title of the web page
	page: string
		Code of the page as constructed so far
	papers: list of strings
		List of names/IDs of papers that need to be referenced on the about.html page
	paper_urls: list of strings
		List of URLs corresponding to the list of papers. URLs direct the user to the webpage where the associated paper can be found. """
	def __init__(self):
		self.name = None
		self.description = None
		self.authors = []
		self.contact = []
		self.papers = []
		self.paper_urls = []

		self.configuration = None
		self.location = None

		self.page = ""

	def add_author(self, name, email=None):
		""" Adds an author by name and email to the about.html file

		Only authors of the AInalysis should be added in this way. Authors of the original data can be linked via the .add_paper method.

		Parameters
		----------
		name: string
			Full name of the author
		email: string (default=`None`)
			The emailaddress of the author. If set to `None`, no email will be displayed. """
		self.authors.append(name)
		self.contact.append(email)
	def add_paper(self, paper_id, paper_url):
		""" Adds a reference to the about.html file

		This method can be used to reference papers which supplied the required data for example. If the paper_url variable does not start with 'http', the text 'http://' is added in front of this variable before storing it in the paper_urls property of this instance.

		Parameters
		----------
		paper_id: string
			Name of the paper or ID (e.g. arxiv number or DOI)
		paper_url: string
			URL via which the paper can be accessed. """
		self.papers.append(paper_id)
		if paper_url[:4] != "http":
			paper_url = "http://"+paper_url
		self.paper_urls.append(paper_url)
	def set_name(self, name):
		""" Sets the name of the AInalysis

		Parameters
		----------
		name: string
			Name of the AInalysis """
		self.name = name
	def set_description(self, description):
		""" Sets the description of the AInalysis

		Parameters
		----------
		description: string
			Description of the AInalysis """
		self.description = description

	def is_configured(self):
		""" Checks if the AboutMaker is fully configured and is able to produce the about.html file

		Checks that are performed are:
		- There has to be at least 1 author
		- At least one author has to ahve an associated emailaddress
		- The AInalysis should have a name
		- The AInalysis should have a description

		If all these checks are passed, `True` is returned. In any other case `False` is returned. 

		Returns
		-------
		configured: boolean
			`True` if all tests as mentioned above are passed, `False` otherwise."""
		if len(self.authors) == 0:
			logger.error("No authors are specified for the AInalysis.")
			return False
		n = 0
		for c in self.contact:
			if not utils.is_none(c):
				n += 1
		if n == 0:
			logger.error("No contact information was provided for the AInalysis.")
			return False
		if utils.is_none(self.name):
			logger.error("The AInalysis has no name.")
			return False
		if utils.is_none(self.description):
			logger.warning("No description of the AInalysis has been provided.")
		return True

	def make_begin(self):
		""" Creates the header and static top of the webpage and stores it in the page property of the AboutMaker instance. Any content stored in this property before this function is called is deleted in the proces."""
		self.page = '<!DOCTYPE html>\
		<html>\
		<head>\
		<title>{} | PhenoAI AInalysis</title>'.format(self.name)
		self.page +='<style>\
		*{ padding: 0; margin: 0; font-family: sans-serif;}\
		body{ background-color: #b5cee0; }\
		\
		h1{ text-align: center; font-weight: bold;}\
		h2{ text-align: center; font-weight: normal; font-size: 16pt;}\
		h3{ margin-top: 30px; padding: 10px; background-color: #6ea8d1; color: white;  font-weight: bold; text-align: center;}\
		h4{ padding: 6px 10px; background-color: #4b86af; color: white; font-weight: normal; }\
		\
		#container{ width: 60%; min-width: 660px; margin: 40px auto; padding: 30px 0 0; background-color: white; border: 1px #ddd solid;}\
		\
		#authors{ text-align: center; margin-top: 30px; }\
		#contact{ text-align: center; font-size: 10pt; }\
		#description{ font-style: italic; text-align: center; padding: 0 30px 20px; margin-top: 30px;}\
		#colofon{ font-size: 9pt; text-align: center; margin: 30px 0 10px; color: #ddd;}\
		\
		.row{ padding: 10px; overflow: auto;}\
		.row div{ float: left; }\
		.color:nth-child(even) { background-color: #eee; }\
		.name{ width: 30%; font-weight: bold; }\
		.value{ width: 70%; }\
		.value img{ width: 100%;}\
		.subvalue{ font-size: 10pt; }\
		.classinfo{ font-style: italic; }\
		.information{ width: 100%; font-size: 10pt; color: #aaa; }\
		\
		.parameter{ width: 100%; padding: 10px;}\
		.parameter .parameter_num{ width: 4%; text-align: center; font-size: 10pt; color: #aaa; }\
		.parameter div{ float: left; width: 24%;}\
		.parameter .parameter_unit{ color: #555; }\
		.parameter div span{ padding-right: 10px; font-size: 9pt; color: #aaa; }\
		\
		.filereader_line{ padding: 0 10px 0 0; width: 100%;}\
		.filereader_line .filereader_num{ width: 5%; text-align: center; font-size: 10pt; color: #aaa; }\
		.filereader_line .filereader_name{ width: 35%; text-align: left; }\
		.filereader_line .filereader_block{ width: 30%; text-align: left; }\
		.filereader_line .filereader_switch{ width: 30%; text-align: right; }\
		.filereader_line div span{ padding-right: 10px; font-size: 9pt; color: #aaa; }\
		\
		</style>\
		</head><body><div id="container">\n'
	def make_header(self):
		""" Creates the non-static top of the webpage (up to the description) and adds it to the page property of the AboutMaker instance. """
		authors = ''
		contacts = 0
		for author, email in zip(self.authors, self.contact):
			if not utils.is_none(email):
				authors += '{} <a href="mailto:{}">{}</a><br />'.format(author, email, email)
				contacts += 1
			else:
				authors += "{}<br />".format(author)
		if authors == '':
			logger.error("No author information was provided.")
			raise exceptions.MakerError("No author information was provided.")
		if contacts == 0:
			logger.warning("No contact information was supplied for the AInalysis description, it is recommended to supply this.")

		now = datetime.datetime.now()
		self.page += '<h2>PhenoAI AInalysis</h2>\
			<h1>{}</h1>\
			<h2>version {} ({})</h2>\
			\
			<p id="authors">{}</p>\
			<p id="description">{}</p>\n'.format(self.name,self.configuration["ainalysisversion"],now.strftime("%Y-%m-%d %H:%M"),authors, self.description)
	def make_body(self):
		""" Creates the code for the non-static body part of the webpage (everything between the description and the footer) and adds this code to the page property of the AboutMaker instance.

		If the associated AInalysis contains a classifier that is calibrated by PhenoAI, a calibration plot will be created and stored as calibration_curve.png at the location defined in the location property of the AboutMaker instance."""

		# Meta information
		phenoaidb = self.configuration["unique_db_id"]
		if utils.is_none(phenoaidb):
			phenoaidb = '<i>No</i>'
		self.page += '<h3>Meta information</h3>\n'
		self.make_cell('Default ainalysis ID', self.configuration["defaultid"], 'The default AInalysis ID defines how the AInalysis is named by phenoai.phenoai objects when no AInalysis name is provided. This is also the name that will be used by AInalysisResults objects to uniquely identify the AInalysis from which the results originate.')
		self.make_cell('In PhenoAI Database', phenoaidb, 'This flag indicates if this AInalysis can be found in the PhenoAI AInalysis database. If this is the case, PhenoAI will automatically query the server if there is an update available when the AInalysis is loaded and the user will be notified if this is indeed the case. The AInalysis is never automatically updated.')

		# Estimator information
		# Package
		if self.configuration["class"] == "sklearnestimator":
			packagedef = 'scikit-learn (<a href="http://www.scikit-learn.org/">website</a>)'
		elif self.configuration["class"] == "kerastfestimator":
			packagedef = 'keras (<a href="http://www.keras.io">website</a>)'
		# Output
		output = self.configuration["output"]
		if self.configuration["type"] == "classifier":
			for c, desc in self.configuration["classes"].items():
				output += '<p class="subvalue"><span class="classint">{}</span>: <span class="classinfo">{}</span></p>'.format(c, desc)
		self.page += '<h3>Estimator information</h3>\n'
		self.make_cell('Packages', packagedef, 'The package in which the trained machine learning algorithm is defined. Can currently be Keras+Tensorflow or scikit-learn.')
		self.make_cell('Estimator type', self.configuration["type"], 'Indicates if the output of the estimator in the AInalysis is meant to be interpreted as discrete (classifier) or as contiuous (regressor). If the estimator is a classifier, details about the classifier are given below in the block "Classifier details".')
		self.make_cell('Output', output, 'Indicates if the output of the estimator in the AInalysis is meant to be interpreted as discrete (classifier) or as contiuous (regressor). If the estimator is a classifier, details about the classifier are given below in the block "Classifier details".')
		if self.configuration["type"] == "classifier":
			self.page += '<h4>Calibration</h4>\n'
			self.make_cell('Calibrated', utils.bool_to_text(self.configuration["classifier.calibrated"]), 'Whether or not the estimator has calibrated output, i.e. the continuous output can be interpreted as a probability.')
			if not self.configuration["classifier.calibrated"]:
				self.make_cell('Let PhenoAI calibrate', utils.bool_to_text(self.configuration["classifier.calibrate"]), 'Indicates if PhenoAI will do some calibration itself based on information provided at creation of the AInalysis.')
				if self.configuration["classifier.calibrate"]:
					plt.plot(self.configuration["classifier.calibrate.bins"], self.configuration["classifier.calibrate.values"], color='k', linewidth=2)
					plt.axhline(0.5, linestyle='--', color='k')
					plt.axhline(0.68, linestyle='--', color='k')
					plt.axhline(0.95, linestyle='--', color='k')
					plt.grid()
					plt.xlabel("Classifier output")
					plt.ylabel("Confidence in classification")
					plt.savefig("{}/calibration_curve.png".format(self.location))
					self.make_cell('Calibration curve', '<img src="calibration_curve.png" alt="Calibration curve" />', 'Curve indicating how estimator output will be mapped. Value to which is mapped indicates the probability the provided classification is correct.')

		# Dependencies and validated versions
		libraries = ""
		for l in self.configuration["libraries"]:
			libraries += "<strong>{}</strong>: ".format(l)
			libraries += ', '.join(self.configuration["libraries"][l])
			libraries += '<br />'
		phenoai = ""
		for v in self.configuration["phenoaiversion"]:
			if phenoai == "":
				phenoai = str(v)
			else:
				phenoai += ", "+str(v)
		self.page += '<h3>Dependencies and validated versions</h3>\n'
		self.make_cell('PhenoAI', phenoai, 'The version numbers of PhenoAI for which this AInalysis is tested and validated. If the version number of your PhenoAI package is not in this list you might encounter unexpected behaviour or errors.')
		self.make_cell('Dependencies', libraries, 'The versions of dependency libraries for which this AInalysis is tested and validated. The libraries listed here have to be installed. Installing different versions of the libraries than listed here might yield unexpected behaviour or errors.')

		# Extra configuration
		# File reading
		define_fileformats = False
		if self.configuration["filereader"] == "function":
			filereader = "Yes, via function read( data ) in functions.py"
			define_fileformats = True
		elif isinstance(self.configuration["filereader"], list):
			filereader = "<p>Yes, via .slha interface:</p><br />"
			for i,p in enumerate(self.configuration["parameters"]):
				filereader += '<div class="filereader_line"><div class="filereader_num">{}.</div><div class="filereader_name">{}</div><div class="filereader_block"><span>BLOCK</span> {}</div><div class="filereader_switch"><span>SWITCH</span> {}</div></div>'.format(i, p[0], self.configuration["filereader"][i][0], self.configuration["filereader"][i][1])
		else:
			filereader = "No"
		# Mapping
		if self.configuration["mapping"] == "function":
			mapping = "Yes, via function map( data ) function in functions.py"
		elif isinstance(self.configuration["mapping"], float) and not isinstance(self.configuration["mapping"], bool):
			mapping = "Yes, relocate points to {}*range the the inside of the boundary if originally outside of the boundary".format(self.configuration["mapping"])
		else:
			mapping = "No"

		# Parameters
		parameters = ''
		for n,i in enumerate(self.configuration["parameters"]):
			parameters += '<div class="parameter">'
			parameters += '<div class="parameter_num">{}.</div>'.format(n)
			parameters += '<div class="parameter_name">{}</div>'.format(i[0])
			parameters += '<div class="parameter_unit"><span>unit</span>{}</div>'.format(i[1])
			parameters += '<div class="parameter_min"><span>min</span>{}</div>'.format(i[2])
			parameters += '<div class="parameter_max"><span>min</span>{}</div>'.format(i[3])
			parameters += '</div>\n'
		self.page += '<h3>Parameters and training ranges (in correct order)</h3>\n'
		self.page += '<div id="parameters" class="color">\n{}<br /></div>\n'.format(parameters)
		self.make_cell('Mapping', mapping, 'Sets if data points outside of the training box (see below) will be moved to the inside of the training box and if so how this replacing is done exactly.')

		self.page += '<h3>Extra configuration</h3>\n'
		self.make_cell('File reading', filereader, 'Defines if the AInalysis has a definition on how to read files. It does not define uniquely which files can be read.')
		if define_fileformats:
			formats = self.configuration["filereader.formats"]
			if isinstance(formats, list):
				formats = ', '.join(formats)
			self.make_cell('File formats', formats, 'Indicates which file type can be read by the file reader. The file format is not thoroughly validated, only the extensions are checked. If the provided file does not match any of the extensions provided here, a warning is given, but normal procedure continues.')
	def make_cell(self, name, content, description):
		""" Creates the code for a single row in the about.html page and adds this code to the page property of the AboutMaker instance

		Parameters
		----------
		name: string
			Name of the property as it will be displayed
		content: any object that can be displayed as string
			Property that will be displayed
		description: string
			Description of the property written in such a way that it makes clear what the property exactly does. """
		self.page += '<div class="row color"><div class="name">{}</div><div class="value">{}</div><div class="information">{}</div></div>\n'.format(name, content, description)
	def make_footer(self):
		""" Creates the footer for the about.html page and adds this code to the page property of the AboutMaker instance. """
		now = datetime.datetime.now()
		self.page += '<p id="colofon">This webpage is automatically generated by PhenoAI {} on {}<br />PhenoAI is created by Bob Stienen</p></div></body></html>'.format(__version__, now.strftime("%Y-%m-%d %H:%M"))

	def make(self, configuration, location):
		""" Create the about.html page

		This method starts the construction of the about.html page based on the provided configuration dictionary and stores the code (once it is generated) in an about.html file at the provided location.

		Parameters
		----------
		configuration: dictionary
			Configuration dictionary as made by a ConfigurationMaker instance or as loaded by an AInalysisConfiguration instance.
		location: string
			Location where the about.html page will be stored."""
		self.configuration = configuration
		if location[-1] == '/':
			location = location[:-1]
		self.location = location

		self.make_begin()
		self.page += "\n\n<!-- HEADER STARTS HERE -->\n\n"
		self.make_header()
		self.page += "\n\n<!-- HEADER STOPS HERE -->\n\n"
		self.page += "\n\n<!-- CONFIG CONTENT STARTS HERE -->\n\n"
		self.make_body()
		self.page += "\n\n<!-- CONFIG CONTENT STOPS HERE -->\n\n"
		self.make_footer()

		# Store
		with open('{}/about.html'.format(self.location),'w') as about:
			about.write(self.page)

class ConfigurationMaker(AInalysisConfiguration):
	""" The ConfigurationMaker class is used in the AInalysisMaker to create configuration files from scratch. It uses the ainalyses.AInalysisConfiguration class as partent class. In normal circumstances the user should not be needing to create call instances of this class directly. """
	def __init__(self):
		self.reset()

	def reset(self):
		""" Sets the configuration to its default values. See full documentation for full information about this state. """
		# Set defaults for configuration
		self.configuration = {}
		self.set("unique_db_id", None)
		self.set("default_id", None)
		self.set("ainalysisversion", 1)
		self.set("phenoaiversion", [__version__])
		self.set("libraries", {})
		self.set("output", None)
		self.set("filereader", False)
		self.set("mapping", False)
		self.set("parameters", None)

	def reset_classifier_block(self):
		""" Sets the classifier.* block in the configuration to its default values. See full documentation for full information about this state. """
		self.set("classifier.classes", None)
		self.set("classifier.calibrated", False)
		self.set("classifier.calibrate", False)

	def set(self, parameter, value):
		""" Sets a parameter in the configuration to a user-defined value.
		
		Parameters
		----------
		parameter: string
			Name of the parameter to be set.
		value: *
			Value of the parameter to be set."""
		self.configuration[parameter] = value

	def get_parameter_entry(self, parameter):
		""" Creates the configuration.yaml entry for a parameter.

		Creates a string of a parameter indicated by the user. This method is used to store the parameters in the configuration.yaml file in the .save() method of this class.

		Parameters
		----------
		parameter: string
			Name of the parameter to create the string of.""" 
		if parameter not in self.configuration:
			return ""
		string = "{}: ".format(parameter)
		value = self.configuration[parameter]
		if not isinstance(value, list) and not isinstance(value, np.ndarray) and not isinstance(value, dict):
			if not utils.is_none(value):
				string += str(value)
		elif isinstance(value, dict):
			#string += ""
			for k,v in value.items():
				if isinstance(v, list):
					l = "["
					for w in v:
						l += str(w)
						if w != v[-1]:
							l += ", "
					v = l+"]"
				string += "\n    {}: {}".format(k, v)
		else:
			string += "["
			if isinstance(value, np.ndarray):
				value = value.tolist()
			if not isinstance(value[0], list):
				for i in range(len(value)):
					string += str(value[i])
					if i != len(value)-1:
						string += ", "
			else:
				indent = len(string)
				for i in range(len(value)):
					string += "["
					for j in range(len(value[i])):
						string += str(value[i][j])
						if j != len(value[i])-1:
							string += ", "
					string += "]"
					if i != len(value)-1:
						string += ",\n"
						string += " "*indent
			string += "]"
		return string

	def validate(self):
		""" Validate the configuration 

		Calls the AInalysisConfiguration.validate() parent method of this ConfigurationMaker instance.

		Returns
		-------
		valid: boolean
			Boolean value indicating if the configuration was good as-is. If any value in the configuration file has to be altered or new ones had to be added, this value will be False. Else it will be True. """
		return super(ConfigurationMaker, self).validate(False)

	def save(self, path):
		""" Save the configuration in a .yaml file at the indicated path.

		Calls for each parameter the .get_parameter_entry() method to create a string to be stored.

		Parameters
		----------
		path: string
			Path the path to where the configuration should be stored. This should include the file itself."""
		# Define parameter order (with blank lines)
		order = [["unique_db_id", "defaultid","ainalysisversion","phenoaiversion","type","class","libraries"],
			["output","classes"],
			["classifier.calibrated","classifier.calibrate","classifier.calibrate.bins","classifier.calibrate.values"],
			["filereader", "filereader.formats"],
			["mapping"],
			["parameters"]]
		# Open configuration file for writing
		with open(path, "w") as f:
			# Loop over all blocks
			for block in order:
				written = 0
				# Loop over all items
				for item in block:
					if item in self.configuration:
						f.write(self.get_parameter_entry(item)+"\n")
						written += 1
				if written != 0:
					f.write("\n")

def generate_calibration_arrays(truth, prediction, nbins=100):
	""" Creates arrays needed for calibration by PhenoAI of two-class classifiers.
	
	This method creates calibration values for predictions made by two-class classifiers. To do this, it creates two histograms with nbins, one for each of the truth classes and calculates for each of the bins the ratio of the majority class in that bin with the total data amount in that bin (sum of two histograms). This value is then a probability that the prediction for predictions in that bin is then correct.
	
	The nbins argument of this function can be quite sensitive if the amount of data is not large enough. It is advised to test the output of this function and see if the truth - probability curve is reasonably smooth.
	
	Parameters
	----------
	truth: numpy.ndarray
		Defines true labels used in calibration. Should have same length as 'prediction'.
	prediction: numpy.ndarray
		Predictions belonging to the true labels ('truth') used in calibration. Should have the same length as 'truth'.
	nbins: integer (default=100)
		Number of bins to create calibrations for (i.e. number of unique probabilities to be created).
	
	Returns
	-------
	centers: numpy.ndarray
		Numpy array containing the centers of the histogram bins (see above for explanation).
	propabilities: numpy.ndarray
		Calculated probabilities that the predicted class is correct (see above for explanation)."""


	# Check if truth is nparray (+ reshape)
	if not isinstance(truth, np.ndarray) and not isinstance(truth, list):
		raise Exception("Truth array for calibration should be a numpy.ndarray or a list")
	if isinstance(truth, list):
		truth = np.array(truth)
	truth = truth.reshape(-1,1)

	# Check if prediction is nparray (+ reshape)
	if not isinstance(prediction, np.ndarray) and not isinstance(prediction, list):
		raise truth("Truth array for calibration should be a numpy.ndarray or a list")
	if isinstance(prediction, list):
		prediction = np.array(prediction)
	prediction = prediction.reshape(-1,1)

	# Check if truth and pred have same shape
	if len(prediction) != len(truth):
		raise exceptions.MakerError("Truth and prediction array for calibration should have the same length.")
		
	# Check if truth is binary
	if len(np.unique(truth)) != 2:
		raise exceptions.MakerError("Calibration arrays can only be made for binary classification problems.")

	# Check if calibration_nbins is an integer
	if not isinstance(nbins, int):
		raise exceptions.MakerError("Number of calibration bins should be an integer.")

	# Create histograms for calibration
	bins = np.linspace(min(np.amin(truth), np.amin(prediction)), max(np.amax(truth), np.amax(prediction)), nbins+1)
	mins = np.array([prediction[i] for i in range(len(prediction)) if truth[i] == np.amin(truth)])
	maxs = np.array([prediction[i] for i in range(len(prediction)) if truth[i] == np.amax(truth)])
	vmins, _ = np.histogram(mins, bins)
	vmaxs, _ = np.histogram(maxs, bins)
	# Define values and bin centers
	probabilities = np.maximum(vmins, vmaxs)/(vmins+vmaxs)
	nans = np.isnan(probabilities)
	if len(nans) != 0:
		logger.warning("Calibration yielded NaN values. These are substituted for 0.5 in order to guarantee the workings of PhenoAI.")
	probabilities[nans] = 0.5
	centers = bins[:-1] + (bins[1] - bins[0])/2.0
	# Return centers and values
	return (centers, probabilities)

def update_checksums(location):
	""" Updates the checksums of an AInalysis

	Parameters
	----------
	location: string
		Path to the AInalysis folder. """
	csums = utils.calculate_ainalysis_checksums(location)
	with open(location+"/checksums.sfv","w") as f:
		for cname in csums:
			f.write("{:<24}{}\n".format(cname, csums[cname]))