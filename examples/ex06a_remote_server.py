"""
Example 06a: Remote server
===============================================
It might happen that in your specific application of PhenoAI you need to start the
package and load an AInalysis for the prediction of a single data point. If this
happens once that might be fine, but if you need to do this multiple times, the
loading time might become extremely unwanted. For this, you can run PhenoAI in a
server-client set-up, in which a continuous proces (server) has all the AInalyses
in memory and another process (client, not necesarily on the same machine) queries
the datapoints to it.
This script creates the server side of this set-up. To see it in action, you need
to run example script 06b after this script has been started.
"""

# Create PhenoAI instance and load AInalysis

import numpy as np

from phenoai import PhenoAI
from phenoai import logger
from phenoai import utils

logger.to_stream(lvl=0)
master = PhenoAI(dynamic=False)
master.add("./example_ainalysis", "example")

# Define server variables

# IP is the IP address of the server itself. If you intend to run the server and
# client on the same machine, you can use "localhost" as IP address, in any other
# case you need to define the IP address along which the client can reach
# the server.
IP = "localhost"

# PORT defines the port along which the communication will be sent. Use a port that
# is not already in use yet. For this reason all ports below 1024 are not allowed.
# See the specific documentation of your operating system on how to find out which
# ports are already in use.
PORT = 31415

# LOGPATH sets the path to which all log information should be outputted. If file
# already exists, new information will be appended to it. If set to `None`, a new
# logging path will be created and used.
LOGPATH = "phenoai_server.log"

# When a PhenoAI server is called via a PhenoAI python client, the PhenoAI results object
# is compressed and sent back. The client can then reinterpret this compressed version
# of the PhenoAIResults object and reconstruct it. When the C++ client is however querying
# the server, this reinterpretation is impossible, so results should be encoded
# differently. The TO_STRING function is a function that defines how the PhenoAIResults
# object should be converted to a string. This string is then sent back to the client
# for interpretation in C++.
# If TO_STRING is defined as a variable `None`, the results are encoded by joining the
# elements of PhenoAIResults.predictions with commas, as is implemented below in TO_STRING.
def TO_STRING(PhenoAIResults):
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
		if out is None:
			if PhenoAIResults[i].data_ids is not None:
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

# Create server

master.run_as_server(IP, PORT, logging_path=LOGPATH, to_string_function=TO_STRING)


