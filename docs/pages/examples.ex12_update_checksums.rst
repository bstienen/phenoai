Example 12: Updating the checksums of an AInalysis
==================================================
Apart from being able to read and use AInalyses, PhenoAI also implements a module
to create new AInalyses from an existing estimator or to alter an existing
AInalysis. This module, the maker module, also implements the function
`update_checksums`, that is able to update the `checksums.sfv` file. This file is
used to check during the loading of the AInalysis if the AInalysis has not been
compromized by unvalidated changes.

.. warning:: Updating checksums only stops warnings from appearing. There are not changes made to the AInalysis itself. The warnings are given to make clear the AInalysis was changed, which might indicate corruption of its files, which might influence the results the AInalysis gives. Use this functionality therefore responsibly!

.. attention:: In order for this script to work, you need to run `Example 08 <ex08_ainalysismaker_classifier.html>`_ in the same folder first.

:download:`Download example script <../_static/examples/ex12_update_checksums.py>`

.. literalinclude:: ../_static/examples/ex12_update_checksums.py

:download:`Download example script <../_static/examples/ex12_update_checksums.py>`