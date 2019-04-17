Mapping
=======
Models that are trained on a sufficiently large data set can only be expected to work in the range defined by their training data. In some cases it is however possible that due to the nature of the parameter space the prediction at the edge of this range can be extrapolated to the rest of the parameter space. There is however no guarantee that this is what the model will do.

For example: the RandomForest classifier trained for `SUSY-AI <http://www.susy-ai.org>`_ predicts the exclusion of model points in a 19-dimensional parameter space for a supersymmetric model in particle physics. The true exclusion was determined by the ATLAS experiment, which is for this model primarily sensitive to the lower range of the parameters (with the exception for maybe one of them). This means that any prediction at the edge of the sampling region, which lays far in the high-value domain, can be extrapolated to beyond this boundary. Due to the structure of the classifier however it happened in development that the prediction certainty dropped below this boundary and some points came out as excluded, whereas any intuitive sense of physics told that said modelpoint were to be allowed.

To overcome this problem, SUSY-AI implemented a mapping method, which is now also implemented in PhenoAI. This mapping moves points outside of the sampling range of the training data to a place well inside this range. Where this location is, is defined by the user.

Mapping is activated for an AInalysis if the ``mapping`` setting in the `configuration <ainalysis_configuration.html>`_ is set to anything else than ``None`` or ``False``. There are a couple of modes that can be enabled (only one at a time though):

Simple mapping
--------------
If the ``mapping`` setting is set to ``True`` or to a value between ``0.0`` and ``0.5`` all points outside of the sampling region will be mapped to the inside of this region. This is done on a per parameter basis, so any parameter that is inside the sampling range will remain untouched. Any parameter outside of the range will be changed using the following formula::

    new_value = minimum_of_parameter +/- parameter_range * mapping_setting

where the ``mapping_setting`` is the value provided in the configuration setting ``mapping`` (``True`` is interpreted as ``0.0``) and the ``+/-`` is decided based on the direction in which the point is deviating from the sampling range.

Mapping by function
-------------------
By setting ``mapping`` to ``"function"`` the mapping is performed by the ``map(data)`` function in the ``functions.py`` file (see `AInalysis Functions <ainalysis_functions.html>`_ for more information). This mode allows the most freedom for the AInalysis developer.
