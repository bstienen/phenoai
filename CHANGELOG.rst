###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Version 0.2.0
************

Added
-----
* Changelog is now added to package
* Sphinx documentation

Improvements
------------
* Code style now in corespondence with PEP8 style guide

Changed behaviour
-----------------
* Disabled updatechecker by setting the API URL to `None` for the time being, as the API of this online interface has to be revised.

Version 0.1.4 (Aug 6th, 2018)
*****************************

Added
-----
* Timout parameters in all functions and methods that make connection to an outside server

Improvements
------------
* All docstrings are improved to guarentee they are correctly displayed in the terminal and the official documentation on the website.
* Example 01 was renamed to reflect the name of the package.

Changed behaviour
-----------------
* The `filetype` parameter in the set_filereader method of the AInalysisMaker is now set to `None` by default, removing the need to set it by hand if no filetype extension check has to be performed.

Bug fixes
---------
* The code showed incorrect behaviour in checking the versions of the installed ML libraries against the versions required by an AInalysis, resulting in unexpected raising of Exceptions.
* An incorrect error was raised when an Estimator object was created for which the corresponding ML package was not installed.
* Example 01 refered incorrectly to the used and loaded AInalysis in the .summary() line. This reference is corrected.
