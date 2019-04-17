"""
Example 11: Update About
========================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, is used in this example to create
an AInalysis that implements a classifier AInalysis based on an existing
AInalysis. This has as advantage that not all information has to be provided
again, but elements like the estimator, configuration or data can just be reused
in the new AInalysis. In this example everything from the original AInalysis is
reused and only the about page is updated in the new version.

The AInalysis that is used as a base in this example is the AInalysis created by
example 08a. In order for this script to run correctly, example 08a has to be
run first.

Example 09a and 09c show how to update the entire AInalysis, reusing only the
configuration, and how to update the AInalysis checksums respectively.
"""

# Check if example 08a was run

import os

if not os.path.exists("./my_first_ainalysis"):
	raise Exception("The AInalysis 'my_first_ainalysis' as created by example 08a could not be found in the 'examples' folder. Run example 08a to create this AInalysis.")

# Load PhenoAI and make sure EVERYTHING is logged to the screen

from phenoai import logger
from phenoai import maker
logger.to_stream(lvl=0)

# Create AInalysis maker

m = maker.AInalysisMaker(
	default_id="my_own_classifier",
	location="./my_updated_first_analysis_09b",
	versionnumber=1,
	overwrite=True)

# Add meta information

m.set_about("Test AInalysis from example09b", "This AInalysis is created by the 08a example and serves no purpose other than showcasing how AInalyses are made. Only the meta information (this about file) should be different from the 08a AInalysis.")
m.add_author("Bob Stienen", "b.stienen@science.ru.nl")
m.add_author("Sascha Caron", "scaron@nikhef.nl")

# Define dependency versions (on top of used versions)

m.load("./my_first_ainalysis",
	load_estimator=True,
	load_data=True)

# Create AInalysis

m.make()
