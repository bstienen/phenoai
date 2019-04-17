Calibration
===========
The output of classifiers might be known to be distored from the distribution one actually wants. Consider for example the following case: a classifier outputs a continuous variable between 0 and 1, where a 0 indicates a "negative" prediction and a 1 a "positive" prediction. A RandomForest classifier is for example a classifier that is able to do this. However, due to the way RandomForests work, the output of the classifier can not be interpreted as a proper probability (i.e. an output of 0.1 does not correspond to a probability of 10% of being a "positive" data point). The following figure, taken from `the examples page of scikit-learn <https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html#sphx-glr-auto-examples-calibration-plot-compare-calibration-py>`_, shows this:

.. image:: https://scikit-learn.org/stable/_images/sphx_glr_plot_compare_calibration_001.png
    :align: center
    :alt: Why calibration is needed in some cases

Not all classifiers need calibration in order to interpret their output as a proper probability: softmax output layers in a neural network output such a proper probability for example.

In order to accommodate this difference between classifiers, PhenoAI has a couple of settings (set in the `configuration of the AInalysis <ainalysis_configuration.html>`_) concerning this calibration. For properly calibrated classifiers the ``classifier.calibrated`` setting can be set to ``True``. For binary classifiers that are not calibrated PhenoAI can do some rough calibration after prediction. In order to activate this functionality, three configuration variables have to be set:

- ``classifier.calibrate``: has to be set to ``True``
- ``classifier.calibrate.bins``: has to be set to a list of length ``N``
- ``classifier.calibrate.values``: has to be set to a list of length ``N``

If no calibration has to be done by PhenoAI, only ``classifier.calibrate`` has to be set to ``False``; the other two settings don't have to be provided.

The calibration procedure implemented by PhenoAI works by binning the output of the classifier. The center of each of these bins is stored in the ``classifier.calibrate.bins`` list. For each of the bins the probability is calculated that the predicted class is correct. These probabilities are stored in ``classifier.calibrate.values``. The class prediction is based on the minimum of ``classifier.calibrate.values``: every ``classifier.calibrate.bins`` value lower than the bin in which this minimum is reached is classified as "excluded", any value higher than this minimum bin is classifier as "allowed".

Note that although this assigns a proper probability to the output of the estimator, this probability is not the probability of being "allowed", but the probability that the given prediction is correct. Moreover, due to the binned nature of the calibration method, possibly continuous nature of the classifier output can be lost. 

The calculation of the bins and values is done automatically by the :obj:`~phenoai.maker.AInalysisMaker` when requested to do so. This object will then make a calibration curve and store it in the AInalysis folder, showing ``classifier.calibrate.bins`` against ``classifier.calibrate.values``.