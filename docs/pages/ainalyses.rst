AInalysis Basics
================

PhenoAI is in a sense just a framework: it implements the functionality to simply use trained machine learning models in almost any Python workflow. It however *does not* provide any models directly; these have to be provided by the user.

Contents of an AInalysis
------------------------
PhenoAI can not guess how to pass and handle data from and to the trained model on its own. Because of this, the trained model is part of a folder containing a set of files that describe the behaviour of the model and how PhenoAI should handle it. This set of files is called an **AInalysis**. It always contains the following files:

- **estimator.pkl** or **estimator.hdf5**: The trained model stored as a python pickle file or as hdf5 file. Which of the two is stored depends on the library with which the esimator was trained (keras: .hdf5, sklearn: .pkl).
- **configuration.yaml**: Configuration of the AInalysis used by PhenoAI to determine how to handle the estimator. It is stored as a human-readable .yaml file. Explanation on what each entry in the configuration while means and does can be found `here <ainalysis_configuration>`_ or in ...
- **about.html**: A webpage container all information from the configuration, accompanied with an explanation on what each entry means.
- **functions.py**: A python module containing functions that are used by the AInalysis.
- **checksums.sfv**: A set of checksums for the AInalysis folder. These checksums are used the check if the AInalysis was not altered in any way without the owner of the files knowing about it, as any change might influence the predictions of the AInalysis.

Apart from that, the AInalysis might also contain a folder called **data**, containing the data used in the creation of the model.

Where to get AInalyses
----------------------
In order to get your hands on a PhenoAI compatible AInalysis, you have two choices. Either you download one from an online library (like `ours <library.html>`_) or you create one yourself. Using our library is the easier option, but it might happen that we don't have the AInalysis you are looking for. In that case you can make your own AInalysis, which would mean that you would also have to train the machine learning model yourself. We have created a series of `examples <examples.html>`_ on how to create your own AInalyses to make this proces as easy as possible.