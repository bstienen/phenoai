AInalysis Functions
===================
Although PhenoAI has a lot of preprogrammed functionalities that can be switched on or off at will, it can of course not be so general that every edge case is covered by it, without having the useability of the program suffering because of it. Because of this every AInalysis contains a file called ``functions.py``. This file contains four functions that can be filled by the creator of the AInalysis with the required functionality, so that new functionalities can be added to the workflow of the AInalysis by the user him or herself.

Currently four functions are supported by PhenoAI. On this page these functions are listed and an explanation of their use is given.

read(data)
----------
A custom file reader function, allowing the user to read files with not natively supported (domain-specific) extensions.

This function takes filepaths as a ``list`` and returns the read content of the files in the form of a ``numpy.ndarray`` or shape ``(nDatapoints, nParameters)``. This function is used if the ``filereader`` setting in the `configuration <ainalysis_configuration.html>`_ is set to ``"function"``.

transform(data)
---------------
A function that trandforms the data before it is subjected to prediction routines. You would place normalisation and scaling in this function for example.

This function takes data as a ``numpy.ndarray`` with shape ``(nDatapoints, nParameters)`` and returns the transformed data in the same shape.

transform_predictions(data)
---------------------------
This function transforms the output of the estimator before it is spit out by the AInalysis in an :obj:`~phenoai.containers.AInalysisResults` object. 

It should take the predictions in the form of a ``numpy.ndarray`` with shape ``(nDatapoints, )`` and return the transformed prediction in the same type and shape shape.

map(data)
---------
A mapping function that allows mapping of data via a custom method. This function is used if ``mapping`` is set to ``"function"`` in the  the `configuration <ainalysis_configuration.html>`_. See `Mapping <functions.mapping.html>`_ for more information.
