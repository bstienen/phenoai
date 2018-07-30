""" The estimators module contains interfaces to estimators of different types and a factory class (EstimatorFactory) to create the estimators. The estimators all implement the same sklearn-inspired interface and all inherit from the classes.Estimator class. Currently implemented are the SklearnEstimator and KerasTFEstimator classes (for scikit-learn estimators and keras tensorflow estimators respectively). """

from . import splash
splash.splash()

import os
try:
	import cPickle as pkl
except:
	import pickle as pkl
import threading as t

from . import containers
from . import io
from . import exceptions
from . import logger
from . import utils


class EstimatorFactory(object):
	""" Factory class for implemented estimators. Contains only a single method 'create_estimator', with which new estimators of an indicated type can be created. """
	def create_estimator(self, estimator_type, path):
		""" Creates and returns an estimator of indicated type that can be found at indicated path.

		Parameters
		----------
		estimator_type: string
			Type of the estimator that has to be returned. Can be either "sklearnestimator" or "kerastfestimator" to create a scikit-learn estimator from pickle or keras estimator from hdf5 file respectively.
		path: string
			Path to the estimator.

		Returns
		-------
		estimator: Estimator
			Estimator derived class of indicated estimator type. """
		if estimator_type == "sklearnestimator":
			logger.debug("Create SklearnEstimator in EstimatorFactory instance")
			return SklearnEstimator(path)
		elif estimator_type == "kerastfestimator":
			logger.debug("Create KerasTFEstimator in EstimatorFactory instance")
			return KerasTFEstimator(path)

class SklearnEstimator(containers.Estimator):
	""" Interface to a scikit-learn estimator. Inherits its properties from the containers.Estimator class."""
	def __init__(self, path=None, load=False):
		try:
			from sklearn import __version__ as sklversion
		except:
			logger.critical("Could not create Estimator based on scikit-learn, package sklearn was not installed.")
			raise exceptions.PhenoAIException("Could not create Estimator based on scikit-learn, package sklearn was not installed.")
		self.libraries = {"sklearn": [sklversion]}
		super().__init__(path, load)
	def load(self):
		""" Loads the estimator into the self.est property from the location stored in self.path. """
		logger.debug("Loading estimator")
		with open(self.path+"/estimator.pkl", 'rb') as f:
			self.est = pkl.load(f)
	def save(self, location):
		""" Saves the estimator to provided location.

		Estimator will be stored at specified location as "estimator.pkl"

		Parameters
		----------
		location: string
			Location where the estimator should be stored, including name and extension of the estimator."""
		if location[-1] == "/":
			location = location[:-1]
		with open(location+"/estimator.pkl", "wb") as f:
			pkl.dump(self.est, f)
	def predict(self, data):
		""" Returns a prediction for the data by querying it to the loaded estimator.

		Parameters
		----------
		data: numpy.ndarray
			Data to be queried to the estimator. Should have format (nDatapoints, nParameters).

		Returns
		-------
		prediction: numpy.ndarray
			Prediction by the loaded estimator for the provided data. Shape of the array depends on the estimator. """
		logger.debug("Querying estimator for prediction (predict)")
		return self.est.predict(data)
	def predict_proba(self, data):
		""" Returns a probability prediction for provided data by querying it to the loaded estimator. Since only classifiers have this functionality in scikit-learn, this method will return `None` if the estimator does not have a prediction_proba method itself.

		Parameters
		----------
		data: numpy.ndarray
			Data to be queried to the estimator. Should have format (nDatapoints, nParameters).

		Returns
		-------
		prediction: numpy.ndarray / `None`
			Prediction by the loaded estimator for the provided data. Shape of the array depends on the estimator. If the loaded estimator does not have a predict_proba method itself, `None` will be returned."""
		logger.debug("Querying estimator for prediction (predict_proba)")
		if hasattr(self.est, predict_proba):			
			return self.est.predict_proba(data)
		logger.debug("Estimator has no predict_proba function")
		return None

class KerasTFEstimator(containers.Estimator):
	""" Interface to a Tensorflow estimator in a Keras wrapper. Inherits its properties from the containers.Estimator class."""
	def __init__(self, path=None, load=False):
		super().__init__(path, load)
		try:
			from keras import __version__ as kerasversion
		except:
			logger.critical("Could not create Estimator based on keras + tensorflow, package keras was not installed.")
			raise exceptions.PhenoAIException("Could not create Estimator based on keras + tensorflow, package keras was not installed.")
		try:
			from tensorflow import __version__ as tfversion
		except:
			logger.critical("Could not create Estimator based on keras + tensorflow, package tensorflow was not installed.")
			raise exceptions.PhenoAIException("Could not create Estimator based on keras + tensorflow, package tensorflow was not installed.")
		self.libaries = {"keras":[kerasversion], "tensorflow":[tfversion]}
	def load(self):
		""" Loads the estimator into the self.est property from the location stored in self.path. """
		from keras.models import load_model
		import tensorflow as tf
		self.est = load_model(self.path+"/estimator.hdf5")
		self.est._make_predict_function()
		self.graph = tf.get_default_graph()
	def save(self, location):
		""" Saves the estimator to provided location.

		Estimator will be stored at specified location as "estimator.hdf5"

		Parameters
		----------
		location: string
			Location where the estimator should be stored, NOT including name and extension of the estimator."""
		if location[-1] == "/":
			location = location[:-1]
		self.est.save(location+"/estimator.pkl")
	def predict(self, data):
		""" Returns a prediction for the data by querying it to the loaded estimator.

		Parameters
		----------
		data: numpy.ndarray
			Data to be queried to the estimator. Should have format (nDatapoints, nParameters).

		Returns
		-------
		prediction: numpy.ndarray
			Prediction by the loaded estimator for the provided data. Shape of the array depends on the estimator. """
		logger.debug("Querying estimator for prediction (predict)")
		with self.graph.as_default():
			return self.est.predict(data)