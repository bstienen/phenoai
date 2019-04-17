Example 10: Updating an AInalysis
=================================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, is used in this example to create
an AInalysis that implements a classifier AInalysis based on an existing
AInalysis. This has as advantage that not all information has to be provided
again, but elements like the estimator, configuration or data can just be reused
in the new AInalysis. In this example the estimator is created from scratch,
so the only thing that is reused is the configuration of the original AInalysis.

.. attention:: In order for this script to work, you need to run `Example 08 <ex08_ainalysismaker_classifier.html>`_ in the same folder first.

:download:`Download example script <../_static/examples/ex10_update_ainalysis.py>`

.. literalinclude:: ../_static/examples/ex10_update_ainalysis.py

:download:`Download example script <../_static/examples/ex10_update_ainalysis.py>`