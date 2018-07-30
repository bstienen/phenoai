""" The PhenoAI module implements the main interface for the PhenoAI package: the PhenoAI class.

This module contains the PhenoAI class: the primary way to interact with the package, which implements methods to handle AInalyses, run predictions in them and run the package as a server. """

from . import splash
splash.splash()

import traceback
import ast
import cgi
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import requests
import numpy as np
import json
import pyslha

from . import ainalyses
from . import containers
from . import client
from . import exceptions
from . import io
from . import logger
from . import utils

__serverinstance__ = None

class PhenoAI(object):
	""" The main interface for running BSM-AI.

	The PhenoAI class provides an interface to send data to (multiple) AInalyses and package their results in an instance of PhenoAIResults. Its main method is the run method, which calls the run method of each AInalyses stored in the PhenoAI instance.

	Instances can run in one of two modes: dynamic or static. In static mode, the estimator of each of the AInalyses is loaded into memory and they will stay there, even after prediction. This makes making a new prediction very fast, since the estimator has not to be loaded again. However, they do take up memory space, which can be a problem in low-memory environments or when running multiple AInalyses in the same PhenoAI instance. Dynamic mode solves this problem by only loading the estimator of an AInalysis if it is needed to make a prediction. If it is loaded after this check and prediction has finished, the estimator is cleared from memory. This of course comes at the cost of speed: loading the estimator takes time.

	Instances of this class can also be run as a server via the run_as_server method. This locks the PhenoAI instance in its current modus, but allows client.phenoaiClient instances to communicate with it over the network or internet.

	Properties
	----------
	ainalyses: list of ainalyses.AInalysis instances
		List of AInalyses managed by the PhenoAI instance. These instances can be queried for prediction on data. AInalyses can be added via the add method.
	dynamic: boolean
		If True, estimators of the AInalyses will be loaded only when necessary. When finished, the estimator will be cleared from memory. This property is useful when running on low RAM machines or when a large collection of AInalyses is stored in the PhenoAI instance.

	Constructor arguments
	---------------------
	dynamic: boolean (default: True)
		If True, estimators of the AInalyses will be loaded only when necessary. When finished, the estimator will be cleared from memory. This property is useful when running on low RAM machines or when a large collection of AInalyses is stored in the PhenoAI instance. """

	def __init__(self, dynamic = True):
		self.ainalyses = []
		self.dynamic = dynamic
	def add(self, ainalysis_folder, ainalysis_id = None):
		""" Adds an AInalysis to the PhenoAI instance

		Adds and AInalysis to the list stored in the ainalyses property of this PhenoAI instance. This allows the PhenoAI instance to query it for its prediction on provided data. This method will raise a PhenoAIException if the provided AInalysis ID would not be unique in the list of AInalyses already stored in the PhenoAI instance.

		Parameters
		----------
		ainalysis_folder: string
			Path to the AInalysis folder
		ainalysis_id: string or `None` (default: `None`)
			ID of the AInalysis to be used in this instance of phenoai. This ID will also be used as identifier for the created AInalysisResults objects by that AInalysis. If set to `None` the default ID defined in the AInalysis configuration will be used. """
		logger.info("Adding AInalysis to PhenoAI object")
		logger.set_indent("+")
		a = ainalyses.AInalysis(ainalysis_folder, ainalysis_id, not self.dynamic)
		logger.set_indent("-")
		if not utils.is_none(self.get(a.ainalysis_id)):
			aid = a.ainalysis_id
			del a
			raise exceptions.phenoaiException("Cannot add AInalysis '{}' with id '{}', ID is already known".format(ainalysis_folder, aid))
		logger.info("AInalysis '{}' added to PhenoAI object".format(a.ainalysis_id))
		self.ainalyses.append(a)
	def get(self, ainalysis_id):
		""" Returns the AInalysis instance with provided AInalysis ID

		Parameters
		----------
		ainalysis_id: string
			ID of the AInalysis that has to be returned.

		Returns
		-------
		ainalysis: AInalysis instance or `None`
			AInalysis with corresponding ID. If no such AInalysis was found, `None` is returned."""
		for ainalysis in self.ainalyses:
			if ainalysis.ainalysis_id == ainalysis_id:
				return ainalysis
		return None
	def is_dynamic(self, mode=True):
		""" Sets how memory needed for estimators has to be allocated

		This method determines how memory needed for the estimators in the AInalyses is allocated and freed. There are two modes: dynamic (True) and static (False). In static mode all estimators are loaded into memory and stay there, even after prediction. In dynamic mode estimators are only loaded when needed and cleared from memory afterwards.

		Parameters
		----------
		mode: boolean
			Boolean indicating which mode the PhenoAI instance has to run in. Can either be True (dynamic) or False (static)."""
		self.dynamic = mode
		if mode:
			logger.info("PhenoAI run mode: dynamic")
		else:
			logger.info("PhenoAI run mode: static")
		for a in self.ainalyses:
			if mode:
				a.estimator.clear()
			else:
				a.estimator.load()
	def run_as_server(self, address, port, logging_path=None, to_string_function=None):
		""" Lets the PhenoAI instance into a server, allowing it to perform predictions on data sent to it from an external script.

		Calling this function lets the PhenoAI instance listen to prediction requests coming in via a specific port and to a specific address instead of prediction requests coming in from the rest of the script. As a consequence, calling this function includes an infinite loop to facilitate the listening for requests. For safety reasons the port this instance will listen to has to be larger then 1024.

		The requests coming in should be HTTP requests and can be created via the client.phenoaiClient class. Important to note is that these requests can be made on the same computer as this PhenoAI instance is running, but also on another computer that is connected to this one via a network (e.g. the internet).

		The split between the client and the server makes it possible to let the client script be written in any programming language, as long as the request follows the correct format. However, the server will return, by default, an instance of the PhenoAIResults class, which can only be used in Python. This problem is solved by letting the server extract (and calculate) the relevant information from the PhenoAIResults object and letting it return not this object, but the relevant information in string form. Since the question "what is the relevant information?" will be answers differently for each use-case, the post-processing will be done by a function written by the user and supplied to this run_as_server method via the to_string_function argument. This function should take the PhenoAIResults instance as its only argument. For example:

				phenoai = PhenoAI()
				def stringify_results(PhenoAIResults):
					return ",".join(PhenoAIResults.predictions)
				phenoai.run_as_server("localhost", 1992, to_string_function = stringify_results)

		The default stringify_results function returns the predictions in .csv format, where the first line contains the file IDs (if provided) and all subsequent lines the predictions for each of the AInalyses for each for each of the data points.

		Whether or not the server returns the full PhenoAIResults object or the generated string is always determined by the client via the requests made.

		Parameters
		----------
		address: string
			IP address of the server. 'localhost' is also a valid address.
		port: integer
			Port of the server to which the requests have to be send.
		logging_path: string or `None`
			Location to where server output has to be logged. Will be additional to any other logging path defined via the logger module. If set to `None` no new logging path will be created and used.
		to_string_function: function or `None`
			Function used to convert PhenoAIResults instance to a string. See explanation above for more information. Can be set to `None` to use the default function. """

		global __serverinstance__
		logger.info("Starting server...")
		logger.info("Checking for valid PhenoAI instance")
		if port < 1025: 
			raise exceptions.ServerException("Port of the server should be at least 1025.")
		server_address = (address, port)
		
		handler = PhenoAIServerRequestHandler
		if not utils.is_none(to_string_function):
			if not callable(to_string_function):
				raise exceptions.ServerException("Function provided to convert results object to string should be callable")
			else:
				class AlteredPhenoAIServerRequestHandler(PhenoAIServerRequestHandler):
					def convert_result_object_to_string(self, PhenoAIResults):
						return to_string_function(PhenoAIResults)
				handler = AlteredPhenoAIServerRequestHandler
		server = ThreadedHTTPServer(server_address, handler)


		__serverinstance__ = self
		if logging_path != None:
			if not utils.is_none(logger.__filechannel__):
				logger.warning("File logging will be continued in server log file '{}'".format(logging_path))
				logger.remove_file_channel()
			logger.info("Start logging to server log file")
			logger.to_file(logging_path)
		logger.warning("Server is running! Use <Ctrl-C> to stop")
		server.serve_forever()

	def run(self, data, map_data=False, ainalysis_ids=None, data_ids=None):
		""" Queries each added AInalysis for prediction on provided data

		This run method forms the core functionality of PhenoAI objects. It calls the run method of each of the added AInalyses with the provided data and configuration arguments. Returns are returned in a containers.PhenoAIResults object.

		The map_data argument is to be interpreted slightly differently here then the map_data argument of AInalysis objects. This argument controls if, for each of the AInalyses, the data is mapped before being subjected to the prediction methods of the estimator in the AInalysis. As such, this argument can either be True or False, just as the map_data argument of the AInalysis run method. However, this run method differs in the sense that is allows the entry "both", which queries all AInalyses that allow mapping of data *twice*: once with mapping and once without. These AInalyses thus have two AInalysisResults instances in the returned PhenoAIResults object, which can be differentiated based on their ID: the mapped results instance has "_mapped" appended to the ID name.

		Parameters
		----------
		data: numpy.ndarray, string or list of strings
			Data that has to be subjected to the estimator. Can be the raw data (numpy.ndarray), the location of a file to be read by the built-in file reader in the AInalysis or a list of file locations.
		map_data: boolean (default=False)
			Determines if data has to be mapped before prediction. Mapping uses the map_data method of this AInalysis and follows the mapping procedure defined in the configuration file for this AInalysis. Can also be "both", making each mapping-allowing AInalyses to be queried twice: once with and once without mapping. Mapped data returns an AInalysisResults object with "_mapped" appended to the AInalysisResults ID.
		ainalysis_ids: list of strings (default=`None`)
			If set to a list of strings, only AInalyses with an ID present in this list are queried for prediction on provided data. If set to `None`, all AInalyses are queried.
		data_ids: list or numpy.ndarray (default=`None`)
			List or numpy.ndarray of IDs for the data points. By setting this value, results can be extracted from the AInalysisResults object by using the IDs in this list/array instead of by its location in the result array. If `None`, this functionality will not be available. """

		# Use PhenoAI object locally
		# Create mapping iteration list
		mapmodes = []
		if map_data == "both":
			mapmodes.append(True)
			mapmodes.append(False)
			logger.info("Running PhenoAI with mapmode 'both'")
		else:
			mapmodes.append(bool(map_data))
			logger.info("Running PhenoAI with mapmode {}".format(bool(map_data)))

		# Create results object
		results = containers.PhenoAIResults()
		# Loop over ainalyses to request prediction
		for ainalysis in self.ainalyses:
			# Load estimator if not loaded already
			loaded = True
			if self.dynamic and not ainalysis.estimator.is_loaded():
				logger.debug("Loading estimator of AInalysis dynamically")
				ainalysis.estimator.load()
				loaded = False

			# Iterate over mapmodes
			for mapmode in mapmodes:
				# Test if this AInalysis should be queried
				if ainalysis_ids != None and ainalysis.ainalysis_id not in ainalysis_ids:
					continue

				# If multi mapmode skip mapmode True if AInalysis does not allow mapping
				if isinstance(ainalysis.configuration['mapping'], bool) and ainalysis.configuration['mapping'] == 0.0 and mapmode and len(mapmodes) > 1:
					continue
				logger.info("Running AInalysis '{}' in map mode '{}'".format(ainalysis.ainalysis_id, mapmode))

				# Do prediction
				logger.set_indent("+")
				result = ainalysis.run(data, map_data=mapmode, data_ids=data_ids)
				logger.set_indent("-")
				# Alter id if multi map mode
				if len(mapmodes) > 1:
					if mapmode:
						result.result_id += "_mapped"
				# Add result to AIResultContainer container
				results.add( result )

			# Unload estimator
			if not loaded:
				logger.debug("Clearing estimator of last AInalysis from memory")
				ainalysis.estimator.clear()

		logger.info("PhenoAI run finished, returning result")
		# Return results object
		return results


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	""" ThreadedHTTPServer implements multithreading for HTTP servers and is used to mutlithread HTTP requests for PhenoAI when run in server mode.

	Users do not have to interact with this method directly, it is created automatically and correctly when calling the run_as_server method of a PhenoAI instance. """
	pass

class PhenoAIServerRequestHandler(BaseHTTPRequestHandler):
	""" Handles HTTP requests for PhenoAI instances

	Users do not have to interact with this method directly, it is created automatically and correctly when calling the run_as_server method of a PhenoAI instance. """

	def do_GET(self):
		""" Takes care of the handling of HTTP GET requests made to PhenoAI

		Prediction requests to PhenoAI are to be made by POST request, this method returns a static text that is used to test the connection between client and server. Users dont have to interact with this method directly, it is automatically called when needed. """
		logger.info("Received GET request from {} - Connection availability is probably checked".format(self.client_address[0]))
		# Send response status code
		self.send_response(200)
		# Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Write content as utf-8 data
		self.wfile.write(bytes("phenoai-ok :: Predictions can only be made via POST request.<br />Use the phenoai.client module or the C++ interface to do this easily.", "utf8"))
		return
	def do_POST(self):
		""" Takes care of the handling of HTTP POST requests made to PhenoAI

		Performs a prediction query to PhenoAI via its run method. Returns the resulting PhenoAIResults object in the correct format. Users dont have to interact with this method directly, it is automatically called when needed. """
		logger.info("Received POST request from {}".format(self.client_address[0]))
		logger.set_indent("+")
		try:
			# Get POST data
			content_length = int(self.headers['Content-Length'])
			post = self.rfile.read(content_length)
			post = post.decode('utf-8')
			post = cgi.parse_qs(post, keep_blank_values=1)
			for k, p in post.items():
				post[k] = p[0]
			# Split by mode
			if post["mode"] == "values":
				logger.debug("Received raw values")
				# Predict lists of values
				data = ast.literal_eval(post['data'])
				if post["data_ids"] == "false" or post["data_ids"] == "False":
					data_ids = None
				else:
					data_ids = ast.literal_eval(post["data_ids"])
				ainalysis_ids = ast.literal_eval(post["ainalysis_ids"])
				# Perform prediction
				if ainalysis_ids == "all":
					ainalysis_ids = None
				logger.debug("Calling run procedure of PhenoAI server instance")
				results = __serverinstance__.run(np.array(data), map_data=bool(float(post['mapping'])), ainalysis_ids=ainalysis_ids, data_ids=data_ids)
			elif post["mode"] == "file":
				logger.debug("Received file to be interpreted")
				data_ids = ast.literal_eval(post["data_ids"])
				ainalysis_ids = ast.literal_eval(post["ainalysis_ids"])

				# Create files in tmp folder
				filepath = "/tmp/{}.phenoai".format(utils.random_string(16))
				filepath_interpreted = "/tmp/{}_interpreted.phenoai".format(utils.random_string(16))
				
				logger.debug("Calling run procedure of PhenoAI server instance")
				try:
					with open(filepath, "w") as tmpfile:
						tmpfile.write(post['data'])
					results = __serverinstance__.run(filepath, map_data=bool(float(post['mapping'])), ainalysis_ids=ainalysis_ids, data_ids=data_ids)
					os.remove(filepath)
				except:
					
					with open(filepath_interpreted, "w") as tmpfile:
						#tmpfile.write(ast.literal_eval(post['data']))
						tmpfile.write(post['data'])
					results = __serverinstance__.run(filepath_interpreted, map_data=bool(float(post['mapping'])), ainalysis_ids=ainalysis_ids, data_ids=data_ids)
					os.remove(filepath_interpreted)
				
				if os.path.exists(filepath):
					os.remove(filepath)
				if os.path.exists(filepath_interpreted):
					os.remove(filepath_interpreted)
			else:
				raise exceptions.ServerException("Mode not recognized, should be either 'values' or 'file'. Provided was '{}'.".format(post['mode']))

			if "get_results_as_string" in post and float(post["get_results_as_string"]) == 1.0:
				logger.debug("Converting results object to string")
				# Return lists of results, not PhenoAIResults object
				results_txt = self.convert_result_object_to_string(results)
			else:
				# Convert to pickled instance
				logger.debug("Encoding results object to pickle")
				results_txt = io.pickle(results)
			returndict = {"status": "ok", "results": results_txt }
		except Exception as e:
			x = traceback.format_exc()
			logger.error(x)
			returndict = {"status": "error", "type":str(type(e).__name__), "message": str(e)}

		logger.info("Return results")
		# Send response status code
		self.send_response(200)
		# Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Write content as utf-8 data
		returntext = json.dumps(returndict)
		self.wfile.write(bytes(returntext, "utf8"))
		logger.set_indent("-")
		return
	def convert_result_object_to_string(self, PhenoAIResults):
		""" Default function to convert a PhenoAIResults object to a string to be returned

		When no to_string_function is provided in the run_as_server method of the PhenoAI object but the client still requires a string to be returned instead of a PhenoAIResults object, this function is the default function to convert the PhenoAIResults object to a returnable string. It returns the results in .csv format with the data_ids in the first row (if provided). All subsequent rows contain the predictions for each of the data points.

		Parameters
		----------
		PhenoAIResults: PhenoAIResults object
			PhenoAIResults object that has to be converted to a string

		Returns
		-------
		outstr: string
			String version fo PhenoAIResults object. See description above for explanation of its contents."""
		out = None
		for i in range(len(PhenoAIResults)):
			preds = PhenoAIResults[i].get_predictions()
			if utils.is_none(out):
				if not utils.is_none(PhenoAIResults[i].data_ids):
					out = np.vstack((PhenoAIResults[i].data_ids, preds))
				if len(preds.shape) == 1:
					out = preds.reshape(1,-1)
				else:
					out = preds
			else:
				out = np.vstack((out, preds))
		out = [",".join(item) for item in out.astype(str)]
		outstr = "\n".join(out)
		return outstr