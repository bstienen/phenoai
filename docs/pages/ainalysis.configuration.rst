AInalysis Configuration
=======================
The configuration file (`configuration.yaml`) of an AInalysis configures how PhenoAI will handle the estimator stored in the AInalysis. It is written in the human-readable .yaml format, but does not contain explanation on what each entry means. This page therefore lists all possible entries in this file and explains their use.

.. note:: In normal circumstances you should not have to alter the contents of the configuration. If you only want to view what the configuration is, the `about.html` file in the AInalysis is better suited for this, as this file contains explanations for each of the entries as well.

----------

Meta information
----------------
.. glossary::

    unique_db_id
        Unique identifier for the AInalysis. This ID is used to check if there is a newer version avaiable of the AInalysis in `the library <library.html>`_. If it is not given or it has no value, this update is not checked, as this means there is no entry in the data base for this AInalysis (e.g. because you made the AInalysis yourself).

    defaultid
        When using an AInalysis, you can provide an identifier to the AInalysis for that run, which is then used to access that AInalysis and its results. If no such identified is provided, the default identified provided by this configuration entry is used instead.

    ainalysisversion
        Integer indicating the version of the AInalysis. For example: ``1``.

    phenoaiversion
        List of PhenoAI version which were actively tested and found to support the current AInalysis. For example: ``[0.1.2, 0.1.3, 0.1.4]``

    type
        Indicates if the estimator is a classifier or a regressor, which influences how output of the estimator is treated and which functionalities are available to the user. For example: ``regressor``.

    class
        Determines with which library the estimator is trained an therefore with which internal class the trained estimator should be read. Currently there are two possible settings for this configuration variable: ``sklearnestimator`` and ``kerasestimator``.

    libraries: 
        List of libraries and their supported versions. For example::
            
            libraries:
                sklearn: [0.18.1, 0.18.1]
                numpy: [1.14.5]

----------

Estimator output
----------------
.. glossary::

    output
        Name of the thing the estimator tries to predict

    classes *(only for classifiers)*
        List linking numeric output to classes. For example: for a neural network with a 3 node softmax output layer this setting might look like this::

            classes:
                0: class A
                1: class B
                2: class C

----------

Classifier *(only for classifiers)*
-----------------------------------

.. note:: The entries in this block of settings only need to be provided if the estimator in the AInalysis is a classifier, indicated through the ``type`` setting in the meta information block (see above).

.. glossary::

    classifier.calibrated
        Boolean value indicating if the classifier is calibrated

    classifier.calibrate
        Boolean value indicating if the output of the classifier should be calibrated by PhenoAI after prediction. In order for this to work, the ``classifier.calibrate.bins`` and ``classifier.calibrate.values`` settings should be set as well. See `calibration <calibration.html>`_ for more information on this calibration method.

    classifier.calibrate.bins:
        List of bin centers for calibration to take place. See `calibration <calibration.html>`_ for more information on this calibration method. Example::

            [0.0125, 0.037500000000000006, 0.0625, 0.08750000000000001, 0.1125, 0.1375, 0.16250000000000003, 0.18750000000000003, 0.21250000000000002, 0.23750000000000002, 0.2625, 0.28750000000000003, 0.31250000000000006, 0.3375, 0.36250000000000004, 0.3875, 0.41250000000000003, 0.43750000000000006, 0.4625, 0.48750000000000004, 0.5125, 0.5375, 0.5625, 0.5875, 0.6125, 0.6375, 0.6625, 0.6875, 0.7125, 0.7375, 0.7625, 0.7875, 0.8125, 0.8375, 0.8625, 0.8875, 0.9125, 0.9375, 0.9625, 0.9875]

    classifier.calibrate.bins:
        List of values for the calibration bins used in calibration of classifier output. See `calibration <calibration.html>`_ for more information on this calibration method. Example::

            [0.9897213957262645, 0.5, 0.5, 0.5, 0.9393638170974155, 0.5, 0.5, 0.5, 0.8509719222462203, 0.5, 0.5, 0.7045454545454546, 0.5, 0.5, 0.5, 0.5, 0.6038961038961039, 0.5, 0.5, 0.5, 0.5373134328358209, 0.5, 0.5, 0.6426799007444168, 0.5, 0.5, 0.5, 0.75, 0.5, 0.5, 0.5, 0.5, 0.8568306010928962, 0.5, 0.5, 0.5, 0.9207920792079208, 0.5, 0.5, 0.9754755541581512]

----------

Filereader settings
-------------------

.. glossary::
    filereader
        Indicates *if* and *how* files can be read by the AInalysis. This setting can have one of the following values:

        - ``False`` or ``None``: indicates no file reading can be done
        - ``"function"``: indicates that file reading is done through the ``read()`` function in ``functions.py``. See `AInalysis functions <ainalysis_functions.html>`_ for more information.
        - a list of shape N*[BLOCK, SWITCH]: indicates the built-in .slha file reader should be used. ``N`` is the number of entries to be taken from the .slha file. For each entry in the list the ``BLOCK`` and ``SWITCH`` indicator should be given. For example::

            filereader: [[MASS, 1000022], [MASS, 1000021]]

    filereader.formats:
        List of file formats that the filereader function can read. The files are only checked for their extension, no in-depth MIME-type validation is performed.

----------

Parameter mapping
-----------------
.. glossary::
    mapping
        Indicates if input for the estimator should be mapped before it should be supplied to the estimator. It can have one of the following values:

        - ``False`` or ``None``: indicates no mapping will take place
        - ``"function"``: indicates the mapping should be done by the `map()` function in ``functions.py``. See `AInalysis functions <ainalysis_functions.html>`_ for more information.
        - ``float``: Sets the relative inset to which data points should be mapped to if laying outside of the sampling range set by ``parameters`` (see below).

        For more information on the mapping procedure, see `Mapping <functions.mapping.py>`_.

----------

Paramters
---------
.. glossary::
    Parameters
        2-dimensional list containing all parameters, their units, the minimum and maximum of this parameter during training. For example::

            parameters:[[x, unitless, -4.3656121, 3.904351],
                [y, unitless, -4.7876877, 3.9979007],
                [z, unitless, -4.569824, 4.5338359]]

