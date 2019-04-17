"""
Example 05: How to use AInalysisResults objects
===============================================
The results of a prediction of an AInalysis are stored in AInalysisResults objects.
To increase the speed of PhenoAI, these objects store only the bare minimum of
information and calculate extra information when asked. In order to access all
possible information from the prediction routines, a good knowledge of the
AInalysisResults' interface is therefore needed. This example script showcases the
possibilities that this interface offers.
"""

# Generate data points without labeling

import numpy as np
X = np.random.rand(10,3)*10-5
# Data IDs are unique identifiers for the data points. Supplying them to the
# run() method of PhenoAI or AInalysis objects allows you to access results
# by datapoint ID, as shown below
data_ids = ['a','b','c','d','e','f','g','h','i','j']

# Create PhenoAI instance and load AInalysis

from phenoai.core.PhenoAI import PhenoAI
from phenoai import logger

logger.to_stream(0)
master = PhenoAI()
master.add("./example_ainalysis", "example")

# Predict labeling and get results for added AInalysis

phenoai_result = master.run(X, data_ids=data_ids, map_data=True)
result = phenoai_result["example"]

# Get all data (X) and data for a specific data point

print("All data: {}".format(result.get_data()))
print("Data for 'd': {}".format(result.get_data('d')))

# Get predictions and the predictions for 'e' and 'f'

print("\nAll predictions: {}".format(result.get_predictions()))
print("Predictions for 'e' and 'f': {}".format(result.get_predictions(['e', 'f'])))

# Check if 'b' is an outlier

print("\nIs 'b' an outlier: {}".format(result.is_outlier('b')))

# Check if 'a' was mapped

mapped = result.is_mapped('a')
print("\nIs mapping of data allowed via the run() method and AInalysis configuration: {}".format(mapped[0]))
print("Is 'a' mapped (None if line above indicates FALSE): {}".format(mapped[1]))

# For classifiers there is also a classification array to return:

print("\nClassification for all points: {}".format(result.get_classifications()))
print("    This AInalysis was a regressor, so no classifications were found\n")

# A summary of the AInalysisResults object can be outputted

result.summary()