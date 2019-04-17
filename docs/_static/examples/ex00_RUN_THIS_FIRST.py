"""
Example 00: RUN THIS FIRST
==========================
Examples 01 to 06 need an AInalysis in order to work. This script will create
the needed AInalysis in the correct format and will store it in a newly created
folder named 'example_ainalysis'. Said scripts will raise an Exception if this
AInalysis is not made yet (i.e. when this script is not run yet)."""

# Create the data to be used in classification

import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

X,y = make_regression(
	n_samples = 100000,
	n_features = 3,
	n_informative = 3
)
X = np.around(X, 7)
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8)

# Create RandomForestRegressor

import sklearn
from sklearn.ensemble import RandomForestRegressor

clf = RandomForestRegressor(n_estimators=10)
clf.fit(X_train, y_train)
print("R^2 of trained regressor: {}".format(clf.score(X_test, y_test)))

# Load PhenoAI and make sure EVERYTHING is logged to the screen

from phenoai import logger
from phenoai import maker
from phenoai import __version__
logger.to_stream(lvl=20)

# Create AInalysis maker

m = maker.AInalysisMaker(
	default_id="my_own_classifier",
	location="./example_ainalysis",
	overwrite=True)

# Add meta information

m.set_about("AInalysis to run the examples", "This AInalysis is created in order to run the example scripts of PhenoAI. It serves no physics-related purpose.")
m.add_author("Bob Stienen", "b.stienen@science.ru.nl")

# Define dependency versions (on top of used versions)

m.set_dependency_version("phenoai", [__version__])
m.set_dependency_version("sklearn", sklearn.__version__)

# Set the estimator and output classes

m.set_estimator(
	estimator=clf,
	estimator_type='regressor',
	output='pointvalue')

# Set the application box via the training data

m.set_application_box(
	data=X_train,
	names=['x','y','z'],
	units=['unitless','unitless','unitless'])

# Add the data to the AInalysis folder

m.add_data(X_train, y_train, "training")
m.add_data(X_test, y_test, "testing")

# Don't allow file reading and mapping
# These don't have to be called when using these settings in principle, because these are the defaults.

m.set_filereader(filereader=True, formats=".csv")
m.set_mapping(mapping=False)

# Create AInalysis

m.make()

# Validate the configuration
# This is called AFTER the AInalysis is made, since validation might change values in the configuration

m.validate_configuration()
