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
This script shows how to use the phenoai.client module to query a server for its
predictions. To run this script, a server should be running and be accessible over
the network from this machine (e.g. by running the server and the client on the
same machine).
"""


# Define server variables

# IP is the IP address of the server itself. If you intend to run the server and
# client on the same machine, you can use "localhost" as IP address, in any other
# case you need to define the IP address along which the client can reach
# the server.
IP = "127.0.0.1"

# PORT defines the port along which the communication will be sent. Use a port that
# is not already in use yet. For this reason all ports below 1024 are not allowed.
# See the specific documentation of your operating system on how to find out which
# ports are already in use.
PORT = 31415

# OBJECT is a boolean indicating if the server should return the full PhenoAIResults
# object or the string based variant defined on the server side (see ex06a for more
# information on this).
OBJECT = True


# Create client object

from phenoai.client import PhenoAIClient
client = PhenoAIClient(IP, PORT)

# Create data to query to server, query server and show result summary

import numpy as np
X = np.random.rand(5,3)
results = client.predict(data=X, map_data=False, data_ids=['a','b','c','e','d'], return_object=OBJECT)
results.summary()

X = np.random.rand(5,3)
results = client.predict(data=X, map_data=False, data_ids=['f','h','k','m','z'], return_object=OBJECT)
results.summary()
