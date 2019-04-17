Tutorial: Running a Classification AInalysis
============================================

To most basic use of PhenoAI is running an AInalysis an analysing its results. In this tutorial we will do this by trying to replicate the results of PhenoAI's predecessor: SUSY-AI. We assume that you've successfully installed PhenoAI. If not, see the `installation page <installation.html>`_ for more information on how to do this.

Step 1: Using the AInalysis Library
-----------------------------------
For this tutorial we will use a pre-made AInalysis. This AInalysis evaluates the exclusion of modelpoints in the 19-dimensional pMSSM. We will download it from the library.

1. Go to the AInalysis library.
2. Search for the AInalysis with ID arxiv:1605.09502.
3. Download the AInalysis folder by clicking the download button in the bottom right of the result.
4. Unpack the .tar.gz file to the desired location.

Step 2: Understanding the AInalysis
-----------------------------------
The AInalysis you just downloaded is not a file but a folder containing a collection of different file types. Although you might want to skip this step -- for it is strictly speaking not needed to follow it -- it it advisable to always have a look at what AInalyses do before you use them. In this step we will have a look at the files in the AInalysis.

The most important file for interpreting the AInalysis is the `about.html` file. This file, which you can open in any browser, contains a description about what the AInalysis is, what it does, who made it, which input it expects etc. etc. If the AInalysis is a classifier, the file `calibration_curve.png` might be located in the AInalysis folder as well and will be displayed in this page. It shows how the output of the trained algorithm (stored in `estimator.pkl` or `estimator.hdf5`) will be mapped to create a confidence level).

The file `functions.py` contains four python functions that are used to handle data. The functions contain docstrings on what each of these functions does. Please be aware that although you can change these functions to your own wishes, you are adviced not to do this, for it might alter the behaviour of the AInalysis and corrupt the output if you don't now exactly what you are doing.

Finally the `checksums.sfv` file contains checksum encodings of the AInalysis. These encodings are used to validate the AInalysis contents and check if none of the files are corrupted or have been tempered with. If the checksums calculated by PhenoAI during runtime do not match the checksums stored in this file, a warning is shown (but the AInalysis will continue to run).


Step 3: Running the AInalysis
-----------------------------
Having downloaded the AInalysis and having read the about.html file, it is time to load the AInalysis into PhenoAI. In order to do this, you need just three lines of code:::

    from phenoai.core.PhenoAI import PhenoAI
    master = PhenoAI()
    master.add("LOCATION", "NAME")

where you need to replace `LOCATION` with the location of the unpacked AInalysis. Replace `NAME` with `susyai`: this will be the name used internally for this AInalysis (and you will need it later to read out the results. You can now run the AInalysis on data. We will assume the data is stored in a variable called `X`. This variable should be a numpy.ndarray with the shape `(nDatapoints, nParameters)`, where `nDatapoints` is the number of data points you want the prediction for and `nParameters` the number of parameters accepted by the AInalysis (for the AInalysis is question this is 19, as mentioned in step 1).::

    result = master.run(X)

Step 4: Reading the results
---------------------------
PhenoAI encodes its results in a container called PhenoAIResults. This container is needed, because in principle you are able to use the master.add( ... ) line multiple times to use multiple AInalyses at the same time. In order to get the results from the AInalysis that we ran, we need to select that AInalysis first. This can be done via a dictionary-like accessor:::

    result["NAME"]

where you need to replace `NAME` with `susyai` (the name we gave the AInalysis internally). Retrieving the results of a specific AInalysis can be done with the following line of code:::

    prediction = result["NAME"].get_predictions()

Since this AInalysis performs a classification task, you can also grab the classification directly via:::

    prediction = result["NAME"].get_classifications()