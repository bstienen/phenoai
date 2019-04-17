"""
Example 09: Create a regressor AInalysis
========================================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, is used in this example to create
an AInalysis that implements a regressor. The exact application case is generated
randomly by scikit-learn, the code is only meant as a show case for how to use
the AInalysisMaker class to create regression AInalyses.

Example 08a shows how to implement the creation of a classification AInalysis.
"""

# Create the data to be used in classification

import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

X,y = make_regression(
	n_samples = 100000,
	n_features = 5,
	n_informative = 5
)
X = np.around(X, 7)
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8)

# Create RandomForestRegressor

from sklearn.ensemble import RandomForestRegressor

clf = RandomForestRegressor(n_estimators=10)
clf.fit(X_train, y_train)
print("R^2 of trained regressor: {}".format(clf.score(X_test, y_test)))

# Load PhenoAI and make sure EVERYTHING is logged to the screen

from phenoai import logger
from phenoai import maker
logger.to_stream(lvl=0)

# Create AInalysis maker

m = maker.AInalysisMaker(
	default_id="my_own_regressor",
	location="./my_second_ainalysis",
	overwrite=True)

# Add meta information

m.set_about("Test AInalysis from example08b", "This AInalysis is created by the 08b example and serves no purpose other than showcasing how AInalyses are made.")
m.add_author("Bob Stienen", "b.stienen@science.ru.nl")

# Set the estimator and output classes

m.set_estimator(
	estimator=clf,
	estimator_type='regressor',
	output='pointvalue')

# Set the application box via the training data

m.set_application_box(
	data=X_train,
	names=['parameterA','parameterB','parameterC','parameterD','parameterE'],
	units=['meter','meter','meter','seconds','seconds'])

# Add the data to the AInalysis folder

m.add_data(X_train, y_train, "training")
m.add_data(X_test, y_test, "testing")

# Don't allow file reading and mapping
# These don't have to be called when using these settings in principle, because these are the defaults.

m.set_filereader(filereader=True, formats=[".csv", ".hdf5"])
m.set_mapping(mapping=False)

# Create AInalysis

m.make()

# Validate the configuration
# This is called AFTER the AInalysis is made, since validation might change values in the configuration

m.validate_configuration()