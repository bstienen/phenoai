"""
Example 04: How to use PhenoAIResults objects
===========================================
Results of PhenoAI objects are returned in PhenoAIResults objects. These objects contain
the results of each of the individual AInalyses run and provide an interface to access
these results efficiently. In this example the usage of this object is shown.
"""

# Generate data points without labeling

import numpy as np
X = np.random.rand(1000,3)*10-5

# Create PhenoAI instance and load AInalysis

from phenoai import PhenoAI
from phenoai import logger

logger.to_stream(0)
master = PhenoAI()
master.add("./example_ainalysis", "example")

# Predict labeling

result = master.run(X)

# Get the IDs of all AInalyses that were called and print them to the screen

ids = result.get_ids()
n = len(result)			# This equals result.num()
print("\n{} AInalyses was/were run: ".format(n))
for i in ids:
	print("  - {}".format(i))
print("\n")

# Summary of results can also be displayed via

result.summary()

# Access the results of the first AInalysis

ainalysis_result = result[ids[0]]
# ainalysis_result = results.get(ids[0])       would have worked as well