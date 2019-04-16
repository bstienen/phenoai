"""
Example 09a: Update AInalysis
=============================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, is used in this example to create
an AInalysis that implements a classifier AInalysis based on an existing
AInalysis. This has as advantage that not all information has to be provided
again, but elements like the estimator, configuration or data can just be reused
in the new AInalysis. In this example the estimator is created from scratch,
so the only thing that is reused is the configuration of the original AInalysis.

The AInalysis that is used as a base in this example is the AInalysis created by
example 08a. In order for this script to run correctly, example 08a has to be
run first.

Example 09b and 09c show how to only change the meta information and how to update
the AInalysis checksums respectively.
"""

# Check if example 08a was run

import os

if not os.path.exists("./my_first_ainalysis"):
	raise Exception("The AInalysis 'my_first_ainalysis' as created by example 08a could not be found in the 'examples' folder. Run example 08a to create this AInalysis.")

# Create the data to be used in classification

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X,y = make_classification(
	n_samples = 100000,
	n_features = 5,
	n_informative = 4,
	n_redundant = 1,
	n_classes = 2
)
X = np.around(X, 4)
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8)

# Create RandomForestClassifier

from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(n_estimators=25)
clf.fit(X_train, y_train)
y_pred = clf.predict_proba(X_test)[:,1]
print("Accuracy of trained classifier: {}".format(clf.score(X_test, y_test)))

# Load PhenoAI and make sure EVERYTHING is logged to the screen

from phenoai import logger
from phenoai import maker
logger.to_stream(lvl=0)

# Create AInalysis maker

m = maker.AInalysisMaker(
	default_id="my_own_classifier",
	location="./my_updated_first_ainalysis",
	versionnumber=2,
	overwrite=True)

# Add meta information

m.set_about("Test AInalysis from example08c", "This AInalysis is created by the 08a example and serves no purpose other than showcasing how AInalyses are made. It is an updated version of the AInalysis of example 08a.")
m.add_author("Bob Stienen", "b.stienen@science.ru.nl")

# Define dependency versions (on top of used versions)

m.load("./my_first_ainalysis",
	load_estimator=False,
	load_data=False)

# Set the estimator and output classes

m.set_estimator(
	estimator=clf,
	estimator_type='classifier',
	output="pointclass",
	classes={0:"classA", 1:"classB"})

# Set classifier configuration: allow for calibration with 40 bins

import numpy as np
m.set_classifier_settings(
	calibrated=False,
	do_calibrate=True,
	calibration_truth=y_test,
	calibration_pred=y_pred,
	calibration_nbins=40)

# Add the data to the AInalysis folder

m.add_data(X_train, y_train, "training")
m.add_data(X_test, y_test, "testing")

# Create AInalysis

m.make()

# Validate the configuration
# This is called AFTER the AInalysis is made, since validation might change values in the configuration

m.validate_configuration()
