Example 11: Updating an AInalysis about page
============================================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, is used in this example to create
an AInalysis that implements a classifier AInalysis based on an existing
AInalysis. This has as advantage that not all information has to be provided
again, but elements like the estimator, configuration or data can just be reused
in the new AInalysis. In this example everything from the original AInalysis is
reused and only the about page is updated in the new version.

.. attention:: In order for this script to work, you need to run `Example 08 <ex08_ainalysismaker_classifier.html>`_ in the same folder first.

:download:`Download example script <../_static/examples/ex11_update_about.py>`

.. literalinclude:: ../_static/examples/ex11_update_about.py

:download:`Download example script <../_static/examples/ex11_update_about.py>`