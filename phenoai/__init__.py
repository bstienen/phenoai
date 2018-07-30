""" PhenoAI allows users to import and use trained sklearn estimators and keras models out-of-the-box in existing workflows. Once loaded, PhenoAI implements methods to call and compare multiple AInalyses and run PhenoAI in a server-client structure.

Generalization over machine learning methods is a key concept of PhenoAI: it depends as little as possible on the loaded estimator. Although PhenoAI as a package is focussed on applications within data analysis in high energy physics, the interface is also usable outside of this field.

To load estimators, they have to be wrapped in a PhenoAI-specific format: an AInalysis. The .maker module allows the user to store estimators in this format."""

# Package meta data
__version__ = "0.1.2"
__versionnumber__ = 3
__versiondate__ = "2018-05-09"
__author__ = "Bob Stienen"
__apiurl__ = "http://www.hef.ru.nl/~bstienen/phenoai/api/update_{}.php"