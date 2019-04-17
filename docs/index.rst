.. PhenoAI documentation master file, created by
   sphinx-quickstart on Thu Jun 21 11:07:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/phenoai.png
    :width: 200px
    :align: center
    :alt: Why calibration is needed in some cases

PhenoAI: Machine Learning for High Energy Physics Phenomenology
===============================================================
**PhenoAI is a Python package that allows the user to easily use, create and share machine learning algorithms from a variety of libraries. This allows ease of use, but also the communication scientific results in high-dimensional parameter spaces.**

PhenoAI is an interface to machine learning models and estimators from the most popular machine learning packages. By abstracting away the machine learning oriented code, the user is left with only the most important functions they need.

Any model and estimator from keras and scikit-learn can be stored in the AInalysis format: a folder containing all relevant information for running PhenoAI, ranging from the estimator/model itself to a configuration file, and from an ABOUT file to sometimes even the training data. You can make these AInalyses yourself with the maker module present in PhenoAI, or you can find pretrained ones in our library.

Storing your high-dimensional results or parameter spaces as a machine learning algorithm opens up the possibility to efficiently explore them. It also allows you to share them with others in their full-dimensional glory. PhenoAI aids this process by taking away the need for in-depth machine learning knowledge to use these stored algorithms, letting the user do what users do best: interpreting and using the results.

.. toctree::
   :hidden:
   :caption: Getting Started
   :maxdepth: 1
   :name: toc_quickstart

   pages/installation
   pages/tutorials
   pages/examples

.. toctree::
   :hidden:
   :caption: AInalyses
   :name: toc_ainalyses

   Basics <pages/ainalyses.rst>
   pages/ainalysis.configuration
   pages/ainalysis.functions
   pages/library
   pages/ainalysis.making

.. toctree::
   :hidden:
   :caption: Processing functionalities
   :name: toc_functions

   pages/functions.calibration.rst
   pages/functions.mapping.rst

.. toctree::
   :hidden:
   :caption: API Documentation
   :name: toc_api

   API <apidocs/phenoai.rst>


.. toctree::
   :hidden:
   :caption: other
   :name: toc_other

   pages/contributing.rst
   pages/changelog.rst
   pages/faq.rst