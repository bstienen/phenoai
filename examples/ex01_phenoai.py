"""
Example 01: Using PhenoAI
========================
In this example the basic functionality of PhenoAI is shown. A single analysis is loaded,
and data is subjected to its prediction routines.
"""

# Check if example_ainalysis folder exists

import os
import sys

if not os.path.exists("./example_ainalysis"):
	print("Run ex00_RUN_THIS_FIRST.py before running any of the example scripts. This creates the required AInalysis.")
	sys.exit()

# Generate data points without labeling

import numpy as np
X = np.random.rand(1000,3)*20-10

# Create PhenoAI instance and load AInalysis

from phenoai import PhenoAI
from phenoai import logger

logger.to_stream(0)
master = PhenoAI()
master.add("./example_ainalysis", "example")

# Predict labeling

result = master.run(X)

# Output content summary of PhenoAIResults object and AInalysisResults object

result.summary()
print("")
result["example"].summary()
