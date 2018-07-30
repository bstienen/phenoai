"""
Example 02: Using a single AInalysis
====================================
Although PhenoAI objects contain some powerful functionality, in some cases it might be
easier to use the smaller AInalysis object. It functions like PhenoAI objects, but only
allows for the usage of a single AInalysis.
"""

# Generate data points without labeling

import numpy as np
X = np.random.rand(1000,3)*10-5

# Create PhenoAI instance and load AInalysis

from phenoai.ainalyses import AInalysis
from phenoai import logger

logger.to_stream(0)
ainalysis = AInalysis("./example_ainalysis", "example", load_estimator=True)

# Run AInalysis over data

results = ainalysis.run(X)

# Print summary of AInalysisResults object

results.summary()