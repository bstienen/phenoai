"""
Example 03: Inspecting the configuration of an AInalysis
========================================================
AInalyses consist, at minimum, out of a machine learning algorithm and a configuration
file. This configuration defines how data is handled before and after it is subjected
to the ML algorithm. It is therefore important to know what this configuration defines
exactly. Although the configuration file is written in the human-readable .yaml
format, this script shows you how to inspect the configuration via PhenoAI itself.
"""

# Create PhenoAI instance and load AInalysis

from phenoai.ainalyses import AInalysis
from phenoai import logger

logger.to_stream(0)
ainalysis = AInalysis("./example_ainalysis", "example", load_estimator=True)

# Show entire configuration

ainalysis.configuration.show()

# Get specific configuration variable

print("\nThis estimator is a(n): {}".format(ainalysis.configuration.get("type")))