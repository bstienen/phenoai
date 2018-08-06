# Currently on Github
## Added
* Changelog is now added to package

# Version 0.1.3 (Aug 6th, 2018)
## Added
* Timout parameters in all functions and methods that make connection to an outside server
## Improvements
* All docstrings are improved to guarentee they are correctly displayed in the terminal and the official documentation on the website.
* Example 01 was renamed to reflect the name of the package.
## Changed behaviour
* The `filetype` parameter in the set_filereader method of the AInalysisMaker is now set to `None` by default, removing the need to set it by hand if no filetype extension check has to be performed.
## Bug fixes
* The code showed incorrect behaviour in checking the versions of the installed ML libraries against the versions required by an AInalysis, resulting in unexpected raising of Exceptions.
* An incorrect error was raised when an Estimator object was created for which the corresponding ML package was not installed.
* Example 01 refered incorrectly to the used and loaded AInalysis in the .summary() line. This reference is corrected.
