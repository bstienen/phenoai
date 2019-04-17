"""
Example 12: Update Checksums
============================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, also implements the function
'update_checksums', that is able to update the checksums.sfv file. This file is
used to check during the loading of the AInalysis if the AInalysis has not been
compromized by unvalidated changes.

It is recommended to always run this function over your AInalyses after you made
a deliberate change to them and know what changed (e.g. you altered the
functions.py file).

To run this example, example 08a has to be run first, since this code attempts
to update the checksums of the AInalysis created by that example.

To see how to update an entire AInalysis or the about.html page, see examples
09a and 09b respectively.
"""

# Check if example 08a was run

import os

if not os.path.exists("./my_first_ainalysis"):
	raise Exception("The AInalysis 'my_first_ainalysis' as created by example 08a could not be found in the 'examples' folder. Run example 08a to create this AInalysis.")

# Load PhenoAI and make sure EVERYTHING is logged to the screen

from phenoai import logger
from phenoai import maker
logger.to_stream(lvl=0)

# Update checksums

maker.update_checksums("./my_first_ainalysis")
