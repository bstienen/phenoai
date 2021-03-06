""" With the maker module existing :mod:`sklearn` and :mod:`keras` estimators
can be converted into :obj:`phenoai.ainalyses.AInalyses` to be used in
PhenoAI."""

import os
import datetime
try:
    import cPickle as pkl
except Exception:
    import pickle as pkl

import numpy as np
import matplotlib.pyplot as plt
import pkg_resources

from phenoai.__version__ import __version__
from phenoai import exceptions
from phenoai import utils
from phenoai import logger
from phenoai.ainalyses import AInalysisConfiguration, AInalysis
from phenoai import estimators


class AInalysisMaker:
    """ The :obj:`phenoai.maker.AInalysisMaker` takes all required information
    to create an AInalysis and stores this in the correct format to be used in
    PhenoAI. The AInalysisMaker explicitely does *not* create estimators, these
    should be made by the user using sklearn or keras.

    Attributes
    ----------
    configuration: :obj:`phenoai.maker.ConfigurationMaker`
        Object to construct and store the configuration.yaml file for the
        AInalysis.

    data: :obj:`dict`
        Dictionary containing data names (keys) and numpy arrays with the data
        itself (values) to be stored within the AInalysis. Data should be added
        via the :meth:`~phenoai.maker.AinalysisMaker.add_data` method of this
        object.

    estimator: :obj:`None`, sklearn estimator or keras model
        The estimator to be used in the AInalysis. To be set via the
        :meth:`~phenoai.maker.AinalysisMaker.set_estimator` method

    flags: :obj:`dict`
        Internal flag system to keep track of all settings that are set
        validly.

    location: :obj:`str`
        Location where the AInalysis has to be stored. To be set exclusively
        via the constructor. """

    def __init__(self, default_id, location, versionnumber=1, overwrite=False):
        """ Initialises the object

        Parameters
        ----------
        default_id: :obj:`str`
            ID the AInalysis should have if the user is not providing one. Has
            to be unique in running PhenoAI.

        location: :obj:`str`
            Location where the AInalysis has to be stored.

        versionnumber: :obj:`int`. Optional
            Version number of the AInalysis. Default is 1.

        overwrite: :obj:`bool`. Optional
            If the location already exists and contains a configuration.yaml
            file, all AInalysis related files are overwritten if this setting
            is set to True. If set to False and the location exists, an
            :exc:`~phenoai.exceptions.MakerError` is raised. Default is
            `False`. """
        # Clean location from closing '/' if provided
        if location[-1] == "/":
            location = location[:-1]
        # Check if location already exists
        if os.path.isdir(location):
            # Raise error if overwrite == False and the location contains a
            # valid AInalysis
            if overwrite is False and os.path.exists(location +
                                                     "/configuration.yaml"):
                logger.error(("Location '{}' already stores an AInalysis "
                              "(overwrite is set to False).").format(location))
                raise exceptions.MakerError(
                    ("Location '{}' already stores an AInalysis (overwrite is "
                     "set to False).").format(location))
        # Make location if needed
        else:
            logger.debug("Location '{}' is made".format(location))
            os.mkdir(location)

        # Create internal variables
        self.estimator = None
        self.aboutmaker = AboutMaker()
        self.location = location
        self.data = {}

        # Set flags dictionary
        self.flags = {
            "application_box": False,
            "estimator": False,
            "estimator_type": False,
            "estimator_configuration": False
        }

        # Create ConfigurationMaker
        self.configuration = ConfigurationMaker()

        # Set default_id in ConfigurationMaker
        self.configure("defaultid", default_id)
        self.set_version(versionnumber)
        self.functions = None

    # Load existing AInalysis
    def load(self,
             location,
             load_data=True,
             load_estimator=False,
             load_functions=True):
        """ Load a secundary AInaysis as template for the new one

        This function allows the user to select an existing AInalysis and load
        its configuration, data, estimator and functions into the maker
        instance. It was written especially for the creation of new versions of
        the same AInalysis, but can be used in broader context.

        Parameters
        ----------
        location: :obj:`str` Path to the AInalysis to be loaded

        load_data: :obj:`bool`. Optional
            Indicates if data should be loaded from the AInalysis. If set to
            `True`, all data will be loaded and copied to the new AInalysis
            folder (unless overwritten by use of the add_data method). Default
            is `True`

        load_estimator: :obj:`bool`. Optional
            Indicates if the estimator of the
            existing AInalysis should be loaded. Default is `False`

        load_functions: :obj:`bool`. Optional
            Indicates if the functions.py file of the existing AInalysis should
            be copied. If set to `False` a new functions.py template will be
            created in the AInalysis folder. Default is `True`"""
        # Clean location indication
        if location[-1] == '/':
            location = location[:-1]
        # Load AInalysis into AInalysis object to read it out afterwards
        a = AInalysis(location, load_estimator)
        # Copy configuration from AInalysis
        self.configuration.configuration = a.configuration.configuration
        # Copy data
        if load_data and os.path.exists(location + "/data"):
            for filename in os.listdir(location + "/data"):
                if filename.endswith(".npy"):
                    dataname = '.'.join(filename.split('.')[:-1])
                    self.data[dataname] = np.load(location + '/data/' +
                                                  filename)
        # Copy estimator
        if load_estimator:
            self.estimator = a.estimator.est
            self.flags["estimator"] = True
            if "type" in self.configuration.configuration:
                self.flags["estimator_type"] = True
                self.flags["estimator_configuration"] = True
        # Set flags
        if "parameters" in self.configuration.configuration:
            self.flags["application_box"] = True
        # Copy content of functions.py
        if load_functions:
            with open(location + "/functions.py", 'r') as funcfile:
                self.functions = funcfile.read()

    # Provide about information
    def set_about(self, name, description):
        """ Sets about information for the about.html file

        With this function the meta information about the AInalysis can be set.
        It is not interpreted by the Maker instance in any way, it is purely
        meant for interpretation of the AInalysis by the user.

        Parameters
        ----------
        name: :obj:`str`
            Name of the AInalysis

        description: :obj:`str`
            Description of the AInalysis"""
        self.aboutmaker.set_name(name)
        self.aboutmaker.set_description(description)

    def add_author(self, name, email=None):
        """ Adds an author by name and email to the about.html file

        Only authors of the AInalysis should be added in this way. Authors of
        the original data can be linked via the .add_paper method.

        Parameters
        ----------
        name: :obj:`str`
            Full name of the author

        email: :obj:`str`. Optional
        The emailaddress of the author. If set to
            `None`, no email will be displayed. Default is `None`. """
        self.aboutmaker.add_author(name, email)

    def add_paper(self, paper_id, paper_url):
        """ Adds a reference to the about.html file

        This method can be used to reference papers which supplied the required
        data for example.

        Parameters
        ----------
        paper_id: :obj:`str`
            Name of the paper or ID (e.g. arXiv number or DOI)

        paper_url: :obj:`str`
            URL via which the paper can be accessed. """
        self.aboutmaker.add_paper(paper_id, paper_url)

    # Set accepted dependency versions
    def set_dependency_version(self, dependency, version, add=True):
        """ Sets/adds the supported version for a dependency

        Parameters
        ----------
        dependency: :obj:`str`
            Name of the dependency. Supported: phenoai,
            sklearn, tensorflow, keras. An :exc:`phenoai.exceptions.MakerError`
            is raised if a different dependency name was provided.

        version: :obj:`str`, :obj:`list(str)`
            Supported version for the
            provided dependency. Multiple versions van be provided as a list.

        add: :obj:`bool`. Optional
            If set to `True`, the provided version(s)
            for the provided dependency is(are) added to the list of already
            present versions for said dependency. If set to `False` the current
            list is replaced by the provided version(s). Default is `True`. """
        if dependency == "phenoai":
            if add and isinstance(self.configuration["phenoaiversion"], list):
                if isinstance(version, list):
                    self.configuration["phenoaiversion"].extend(version)
                else:
                    self.configuration["phenoaiversion"].append(version)
            elif add:
                if isinstance(version, list):
                    version.append(self.configuration["phenoaiversion"])
                    self.configuration["phenoaiversion"] = version
                else:
                    self.configuration["phenoaiversion"] = [
                        self.configuration["phenoaiversion"], version
                    ]
            else:
                self.configuration["phenoaiversion"] = version
        elif dependency in ["sklearn", "tensorflow", "keras"]:
            if dependency not in self.configuration["libraries"]:
                self.configuration["libraries"][dependency] = version
            else:
                if (add and isinstance(
                        self.configuration["libraries"][dependency], list)):
                    if isinstance(version, list):
                        self.configuration["libraries"][dependency].extend(
                            version)
                    else:
                        self.configuration["libraries"][dependency].append(
                            version)
                elif add:
                    if isinstance(version, list):
                        version.append(
                            self.configuration["libraries"][dependency])
                        self.configuration["libraries"][dependency] = version
                    else:
                        self.configuration["libraries"][dependency] = [
                            self.configuration["libraries"][dependency],
                            version
                        ]
        else:
            logger.error(("Dependency '{}' unknown, can only set dependency "
                          "for ['phenoai', 'keras', 'sklearn', "
                          "'tensorflow']").format(dependency))
            raise exceptions.MakerError(
                ("Dependency '{}' unknown, can only set dependency for "
                 "packages in the following list ['phenoai', 'keras', "
                 "'sklearn', 'tensorflow']").format(dependency))

    # Version number setter
    def set_version(self, versionnumber):
        """ Define the version number of the AInalysis

        If the supplied version number is not an integer and could not be cast
        to one, an :exc:`phenoai.exceptions.MakerError` is raised.

        Parameters
        ----------
        versionnumber: :obj:`int`
            Version number of the AInalysis """
        if not isinstance(versionnumber, int):
            try:
                versionnumber = int(versionnumber)
            except Exception:
                logger.error("Version number should be an integer.")
                raise exceptions.MakerError(("Version number should be an"
                                             "integer."))
        self.configure("ainalysisversion", versionnumber)

    def set_estimator(self, estimator, estimator_type, output, classes=None):
        """ Sets the estimator and settings of the estimator to be used in the
        AInalysis.

        Parameters
        ----------
        estimator: sklearn estimator or keras model
            Estimator object to be stored in the AInalysis for usage.

        estimator_type: :obj:`str`
            Indicates if the estimator is to be used as
            a classifier or a regressor. Is internally handled via the
            .set_estimator_type() method. Supported are "classifier" and
            "regressor". A :exc:`phenoai.exceptions.MakerError` is raised if an
            unknown estimator_type is provided.

        output: :obj:`str`
            String explaining what the output represents

        classes: :obj:`dict`. Optional
            Dictionary specifying what the output
            classes represent. Should only be defined if the estimator is a
            classifier. If the estimator is an estimator, this dictionary
            should follow format {class: name, class: name, ...}. Default is
            `Nonw`. """
        # Check which package the estimator belongs to
        m = estimator.__module__
        if "sklearn" in m:
            # Set Estimator class in configuration
            self.configure("class", "sklearnestimator")
            e = estimators.SklearnEstimator()
            libs = e.libraries
        elif "keras" in m:
            # Set Estimator class in configuration
            self.configure("class", "kerasestimator")
            e = estimators.KerasEstimator()
            libs = e.libraries
        else:
            # Raise exception
            logger.error("Package for estimator could not be identified")
            raise exceptions.MakerError(("Package for estimator could not "
                                         "be identified"))
        # Set estimator package versions
        for l in libs:
            self.set_dependency_version(l, libs[l])
        # Store estimator internally and set flag
        self.estimator = estimator
        self.flags["estimator"] = True
        logger.info("Estimator set for AInalysis")

        # Check estimator_type
        if estimator_type not in ("regressor", "classifier"):
            logger.error(("estimator_type should be either 'classifier' or "
                          "'regressor'."))
            raise exceptions.MakerError(("estimator_type should be either "
                                         "'classifier' or 'regressor'."))
        # Set estimator_type
        self.set_estimator_type(estimator_type)

        # Set what the estimator is trying to estimate
        if not (isinstance(output, str)):
            logger.error("Estimator output should be a string.")
            raise exceptions.MakerError("Estimator output should be a string.")
        if not isinstance(classes, dict) and classes is not None:
            logger.error("Classes should be a dictionary or None.")
            raise exceptions.MakerError(("Classes should be a dictionary or "
                                         "None."))
        self.configure("output", output)
        if classes is not None:
            c = {}
            for k, v in classes.items():
                try:
                    c[int(k)] = v
                except Exception:
                    logger.error("Classes should be integers.")
                    raise exceptions.MakerError("Classes should be integers.")
            self.configure("classes", classes)

    def set_estimator_type(self, estimator_type):
        """ Defines the estimator type in the configuration of the AInalysis.

        In calling this method, the flags `estimator_type` (for regressors and
        classifiers) and `estimator_configuration` (for regressors only) are
        set to `True`.

        Parameters
        ----------
        estimator_type: :obj:`str`
            Defines if the estimator of the AInalysis is
            a classifier or a regressor. Supported are "classifier" and
            "regressor". A :exc:`phenoai.exceptions.MakerError` is raised if an
            unknown estimator_type is provided. """
        # Check if estimator type is defined correctly
        if estimator_type == "classifier":
            # Estimator is a classifier
            self.flags["estimator_type"] = True
        elif estimator_type == "regressor":
            # Estimator is a regressor
            self.flags["estimator_type"] = True
            self.flags["estimator_configuration"] = True
        else:
            # Raise exception because type is unknown
            logger.error(("Estimator type '{}' unknown, must be 'classifier' "
                          "or 'regressor'.").format(estimator_type))
            raise exceptions.MakerError(
                ("Estimator type '{}' unknown, must be 'classifier' or "
                 "'regressor'.").format(estimator_type))
        # Set estimator type in configuration
        self.configure("type", estimator_type)
        logger.info("Estimator type set for AInalysis")

    def set_classifier_settings(self,
                                calibrated=False,
                                do_calibrate=False,
                                calibration_truth=None,
                                calibration_pred=None,
                                calibration_nbins=100):
        """ Defines the classifier classes and calibration settings for the
        estimator if it is a classifier

        If calibration has to be done by PhenoAI (as defined when
        `do_calibration` == True), the needed arrays for this calibration are
        created from the calibration_truth, calibration_prediction and
        calibration_nbins via the
        :meth:`~phenoai.maker.generate_calibration_arrays` function in this
        module.

        Parameters
        ----------
        calibrated: :obj:`bool`. Optional
            Boolean indicating if the classifier
            is calibrated, i.e. if the output can be interpreted as a proper
            probability. Default is `False`.

        do_calibrate: :obj:`bool`. Optional
            Boolean indicating if the
            classifier output has to be calibrated by PhenoAI after prediction.
            This setting is ignored if `calibrated` was set to `True`.
            Calibration can only take place for classifiers creating
            predictions on two classes. Default is `False`.

        calibration_truth: :obj:`None`, :obj:`numpy.ndarray`. Optional
            Defines true labels used in calibration. Should have same length as
            `calibration_prediction` and has to be set as :obj:`numpy.ndarray`
            if 'do_calibrate' is `True`. This setting is ignored if
            `do_calibrate` is set to `False`. Default is `None`.

        calibration_prediction: :obj:`None`, :obj:`numpy.ndarray`. Optional
            Predictions belonging to the true labels ('calibration_truth') used
            in calibration. Should have same length as `calibration_truth` and
            has to be set as numpy.ndarray of `do_calibrate` is `True`. This
            setting is ignored if `do_calibrate` is set to False. Default is
            `None`.

        calibration_nbins: :obj:`int`. Optional
            Number of bins to create
            calibrations for (i.e. number of unique probabilities to be
            created). This setting is ignored if `do_calibrate` is set to
            False. Default is 100. """

        # Check if classifier is calibrated
        if not calibrated:
            self.configure("classifier.calibrated", False)
            # Check if output has to be calibrated by PhenoAI
            if do_calibrate:
                self.configure("classifier.calibrate", True)
                # Create calibration arrays
                logger.info("Create calibration arrays")
                bins, values = generate_calibration_arrays(
                    calibration_truth, calibration_pred, calibration_nbins)
                # Store calibrate information
                self.configure("classifier.calibrate.bins", bins.tolist())
                self.configure("classifier.calibrate.values", values.tolist())
            else:
                self.configure("classifier.calibrate", False)
        else:
            self.configure("classifier.calibrated", True)
            self.configure("classifier.calibrate", False)
        self.flags["estimator_configuration"] = True
        logger.info("Classifier settings set for AInalysis")

    # Data
    def set_application_box(self, data, names, units):
        """ Defines the box within which the training data was sampled and
        therefore within which the estimator is expected to work

        If this method is validly called an execution succeeded, the internal
        `application_box` flag is set to `True`.

        Parameters
        ----------
        data: :obj:`numpy.ndarray`
            Numpy.ndarray of shape (nDatapoints, nParameters) containing the
            training data.

        names: :obj:`list(str)`
            List of the parameter names. Length of this
            list should match the number of parameters defined by `data` (=
            nParameters).

        units: :obj:`list(str)`
            List of units for the parameters defined in
            `names`. Length of this list should match the number of parameters
            defined by `data` (= nParameters). """

        # Check if data is a numpy array
        if not isinstance(data, np.ndarray):
            logger.error(("Data for application box definition should be "
                          "numpy.ndarray of shape (nDatapoints, nFeatures)."))
            raise exceptions.MakerError(("Data for application box "
                                         "definition should be numpy.ndarray "
                                         "of shape (nDatapoints, nFeatures)."))
        # Check if names is a list
        if not isinstance(names, list):
            logger.error(("Names should be a list naming the features of "
                          "the data array."))
            raise exceptions.MakerError(("Names should be a list naming the "
                                         "features of the data array."))
        # Check if names fits data shapewise
        if len(data[0]) != len(names):
            logger.error(("Number of features in the data array should match "
                          "the number of names in the names array."))
            raise exceptions.MakerError(("Number of features in data array "
                                         "should match number of names in "
                                         "names array."))
        # Create parameters variable
        mins = np.amin(data, axis=0)
        maxs = np.amax(data, axis=0)
        parameters = [[names[i], units[i], mins[i], maxs[i]]
                      for i in range(len(names))]
        # Store parameters in configuration
        self.configure("parameters", parameters)
        self.flags["application_box"] = True
        logger.info("Application box for AInalysis is defined")

    def add_data(self, x, y, name):
        """ Adds data to the AInalysis to be stored in the data subfolder of
        the AInalysis.

        Parameters
        ----------
        x: :obj:`numpy.ndarray`
            Numpy.ndarray of shape (nDatapoints, nParameters) containing the
            data.

        y: :obj:`numpy.ndarray`
            Numpy.ndarray of shape (nDatapoints, ) containing the true labeling
            of the data provided in 'x'.

        name: :obj:`str`
            Name of the data, e.g. 'training', 'testing' or 'validation'. Data
            will be stored as [name]_data and [name]_labeling."""
        self.data[name + "_data"] = x
        self.data[name + "_labeling"] = y
        logger.info("Dataset '{}' is added".format(name))

    # Filereader
    def set_filereader(self, filereader, formats=None):
        """ Defines the method through which files are read by the AInalysis.

        This method can only be called after the
        :meth:`phenoai.maker.AInalysisMaker.set_application_box` method is
        successfully called.

        Parameters
        ----------
        filereader: :obj:`bool`, :obj:`str`, :obj:`list(str)`
            Defines the method through which files are read by the AInalysis.
            If set as a boolean, False will disable filereading by the
            AInalysis, True will outsource the file reading to the 'read'
            function in the functions.py file of the AInalysis. This can also
            be done by setting this argument to "function". Alternatively this
            argument can also be set to a list of shape [BLOCK, SWITCH]*N,
            defining the reader interface for .slha files. The BLOCK should be
            a string and SWITCH should be an integer or a list of integers
            (for matrices defined in .slha files). N is the number of
            parameters accepted by the estimator and should match the number of
            parameters defined via the
            :meth:`phenoai.maker.AInalysisMaker.set_application_box` method.

        formats: :obj:`str`, :obj:`list(str)`. Optional Defines which file
            formats can be read by the filereader. Setting it to `None`
            indicates no filereader is supplied. Default is `None`."""
        # Check if application box is already defined
        if self.configuration["parameters"] is None:
            logger.error(("File reader can only be defined after defining the "
                          "application box via .set_application_box()"))
            raise exceptions.MakerError(("File reader can only be defined "
                                         "after defining the application box "
                                         "via .set_application_box()"))
        # Check if filereader is boolean
        if isinstance(filereader, bool):
            # If True, user has to define a function
            if filereader:
                self.configure("filereader", "function")
            # Otherwise no filereader is defined
            else:
                self.configure("filereader", False)
        # Check if filereader is a string and if it equals "function", if so
        # filereader by function is defined
        elif isinstance(filereader, str) and filereader == "function":
            self.configure("filereader", "function")
        # Check if filereader is a list
        elif isinstance(filereader, list):
            # Loop over all list elements
            listformaterror = False
            # Verify for each element in the filereader list if the format is
            # correct
            for item in filereader:
                if not isinstance(item[0], str):
                    listformaterror = True
                if not (isinstance(item[1], (int, list, tuple))):
                    listformaterror = True
                if not isinstance(item[1], int) and len(item[1]) != 2:
                    listformaterror = True
            if listformaterror:
                logger.error(("List definitions of filereader should have "
                              "format [BLOCK, SWITCH]*N, where BLOCK is a "
                              "string, SWITCH an integer, list or tuple of "
                              "length 2 and N the number of features in the "
                              "data."))
                raise exceptions.MakerError(("List definitions of filereader "
                                             "should have format "
                                             "[BLOCK, SWITCH]*N, where BLOCK "
                                             "is a string, SWITCH an integer, "
                                             "list or tuple of length 2 and N "
                                             "the number of features in the "
                                             "data."))
            # Check if length of list is equal to number of features in data
            if len(filereader) != len(self.configuration["parameters"]):
                logger.error(("Length of the filereader list should match "
                              "the number of features in the application "
                              "box."))
                raise exceptions.MakerError(("Length of the filereader list "
                                             "should match the number of "
                                             "features in the application "
                                             "box."))
            self.configure("filereader", filereader)
        else:
            logger.error(("Filereader formats should be defined as a string "
                          "or a list of strings, where each string defines a "
                          "file extension."))
            raise exceptions.MakerError(("Filereader formats should be "
                                         "defined as a string or a list of "
                                         "strings, where each string defines "
                                         "a file extension."))
        # Define file format
        if (not isinstance(formats, str) and not isinstance(formats, list)
                and formats is not None):
            logger.error(("Filereader formats should be defined as a string "
                          "or a list of strings, where each string defines a "
                          "file extension."))
            raise exceptions.MakerError(("Filereader formats should be "
                                         "defined as a string or a list of "
                                         "strings, where each string defines "
                                         "a file extension."))
        if isinstance(formats, list):
            for f in formats:
                if not isinstance(f, str):
                    logger.error(("Filereader formats should be defined as a "
                                  "string or a list of strings, where each "
                                  "string defines a file extension."))
                    raise exceptions.MakerError(("Filereader formats should "
                                                 "be defined as a string or a "
                                                 "list of strings, where each "
                                                 "string defines a file "
                                                 "extension."))
        self.configure("filereader.formats", formats)
        logger.info("Filereader is defined")

    # Mapping
    def set_mapping(self, mapping=False):
        """ Defines if the AInalysis should allow mapping and if so, what the
        mapping border should be.

        Parameters
        ----------
        mapping: :obj:`bool`, :obj:`str`, :obj:`float`. Optional
            Sets the mapping capabilities of the AInalysis. If set to False, no
            mapping will take place. If set to True, all mapping will be done
            to the border to the application box. Can also be set to a floating
            point number between 0.0 and 0.5, where 0.0 indicates mapping to
            the border of the application box and 0.5 indicates mapping to the
            center of the application box. If set to 'function' (string), the
            `map` function in the functions.py file will be used for mapping.
            Default is `False`."""
        if isinstance(mapping, bool):
            self.configure("mapping", mapping)
        elif isinstance(mapping, float) and mapping <= 0.5 and mapping >= 0.0:
            self.configure("mapping", mapping)
        elif mapping == "function":
            self.configure("mapping", mapping)
        else:
            raise exceptions.MakerError(("Mapping should be a boolean, "
                                         "'function' (str) or a float between "
                                         "0.0 and 1.0"))
        logger.info("Mapping is set to '{}'".format(mapping))

    def configure(self, parameter, value):
        """ Sets configuration parameters

        Redirects input arguments to the
        :meth:`phenoai.maker.ConfigurationMaker.set` method of the
        :obj:`~phenoai.maker.ConfigurationMaker` instance in the configuration
        property of this object.

        Parameters
        ----------
        parameter: :obj:`str`
            Name of the parameter to be set in the configuration.

        value: any Value of the parameter to be set in the configuration."""
        self.configuration.set(parameter, value)

    def validate_configuration(self):
        """ Validate the configuration

        Calls the :meth:`phenoai.ainalyses.AInalysisConfiguration.validate`
        method of the ConfigurationMaker instance in the configuration property
        of this object.

        Returns
        -------
        valid: :obj:`bool`
            Boolean value indicating if the configuration was
            good as-is. If any value in the configuration file has to be
            altered or new ones had to be added, this value will be `False`.
            Else it will be `True`. """
        logger.info("Validate configuration")
        v = self.configuration.validate()
        logger.info("Configuration validated")
        return v

    def make(self):
        """ Creates the AInalysis

        Creats the AInalysis at the location provided in construction of this
        object. Will raise an :exc:`phenoai.exceptions.MakerError` if not all
        flags are True."""

        logger.info("Create AInalysis")

        # Check if about page can be made
        if not self.aboutmaker.is_configured():
            logger.error(("Cannot make AInalysis, because not all meta "
                          "information has been provided (see errors above)."))
            raise exceptions.MakerError(("Cannot make AInalysis, because not "
                                         "all meta information has been "
                                         "provided (see errors above)."))

        # Check if all flags are True
        for f in self.flags:
            if not self.flags[f]:
                raise exceptions.MakerError(("Could not make the AInalysis, "
                                             "the '{}' flag is not set to "
                                             "True.").format(f))

        # Estimator
        # Store sklearn estimator
        if self.configuration["class"] == "sklearnestimator":
            with open(self.location + "/estimator.pkl", "wb") as f:
                pkl.dump(self.estimator, f)
        # Store keras estimator
        elif self.configuration["class"] == "kerasestimator":
            self.estimator.save(self.location + "/estimator.hdf5")
        logger.debug("Estimator stored")

        # If data is defined, make data folder
        if self.data and not os.path.exists(self.location + "/data"):
            os.mkdir(self.location + "/data")
            # Create data .npy files
            for d in self.data:
                np.save(self.location + "/data/{}.npy".format(d), self.data[d])
            logger.debug("Datasets are stored")

        # Create functions.py
        with open(self.location + "/functions.py", "w") as f:
            if self.functions is None:
                functions_template = get_template_file('functions.py')
                f.write(functions_template)
            else:
                f.write(self.functions)
        logger.debug("functions.py file is created")

        # Create configuration.yaml
        self.configuration.save(self.location + "/configuration.yaml")
        logger.debug("Configuration is stored in configuration.yaml file")

        # Create about page
        self.aboutmaker.make(self.configuration, self.location)

        # Create checksums
        update_checksums(self.location)
        logger.debug("Checksums are created")

        # Closing statements
        logger.info("AInalysis is successfully created")
        logger.warning(("Don't forget to alter the functions.py file to "
                        "specify a file reader function / mapping function or "
                        "to perform data transformations before and after "
                        "predictions!"))
        logger.warning(("If the functions.py file is altered, call the "
                        "update_checksums([ainalysisfolder]) function of this "
                        "module to update the checksums file."))


class AboutMaker:
    """ The AboutMaker is able to create about.html files that summarize
    AInalyses in a user readable format.

    An AboutMaker instance is automatically created and managed by the
    :obj:`phenoai.maker.AInalysisMaker` and any function of the
    :obj:`~phenoai.maker.AboutMaker` has an interface in the
    :obj:`~phenoai.maker.AInalysisMaker`. In normal circumstances, you
    therefore should not have to use instances of this specific class directly.

    Attributes
    ----------
    authors: :obj:`list(str)`
        List of author names

    configuration: :obj:`dict`
        Configuration dictionary as made by a ConfigurationMaker instance or as
        loaded by an AInalysisConfiguration instance.

    contact: :obj:`list(str / None)`
        List of emailaddresses corresponding to the list of authors. If an
        author has no emailaddress associated with it, the entry will be
        `None` instead.

    description: :obj:`str`
        Description of the AInalysis

    location: :obj:`str`
        Location where the about.html page will be stored.

    name: :obj:`str`
        Name of the AInalysis, will become the title of the web page

    page: :obj:`str`
        Code of the page as constructed so far

    papers: :obj:`list(str)`
        List of names/IDs of papers that need to be referenced on the
        about.html page

    paper_urls: :obj:`list(str)`
        List of URLs corresponding to the list of papers. URLs direct the user
        to the webpage where the associated paper can be found. """

    def __init__(self):
        self.name = None
        self.description = None
        self.authors = []
        self.contact = []
        self.papers = []
        self.paper_urls = []

        self.configuration = None
        self.location = None

        self.page = ""

    def add_author(self, name, email=None):
        """ Adds an author by name and email to the about.html file

        Only authors of the AInalysis should be added in this way. Authors of
        the original data can be linked via the .add_paper method.

        Parameters
        ----------
        name: :obj:`str`
            Full name of the author

        email: :obj:`str`. Optional
            The emailaddress of the author. If set to `None`, no email will be
            displayed. Default is `None` """
        self.authors.append(name)
        self.contact.append(email)

    def add_paper(self, paper_id, paper_url):
        """ Adds a reference to the about.html file

        This method can be used to reference papers which supplied the required
        data for example. If the `paper_url` variable does not start with
        'http', the text 'http://' is added in front of this variable before
        storing it in the :attr:`phenoai.maker.AboutMaker.paper_urls` property
        of this instance.

        Parameters
        ----------
        paper_id: :obj:`str`
            Name of the paper or ID (e.g. arxiv number or DOI)
        paper_url: :obj:`str`
            URL via which the paper can be accessed. """
        self.papers.append(paper_id)
        if paper_url[:4] != "http":
            paper_url = "http://" + paper_url
        self.paper_urls.append(paper_url)

    def set_name(self, name):
        """ Sets the name of the AInalysis

        Parameters
        ----------
        name: :obj:`str`
            Name of the AInalysis """
        self.name = name

    def set_description(self, description):
        """ Sets the description of the AInalysis

        Parameters
        ----------
        description: :obj:`str`
            Description of the AInalysis """
        self.description = description

    def is_configured(self):
        """ Checks if the AboutMaker is fully configured and is able to
        produce the about.html file

        Checks that are performed are:
        - There has to be at least 1 author
        - At least one author has to ahve an associated emailaddress
        - The AInalysis should have a name
        - The AInalysis should have a description

        If all these checks are passed, `True` is returned. In any other case
        `False` is returned.

        Returns
        -------
        configured: :obj:`bool`
            `True` if all tests as mentioned above are passed, `False`
            otherwise."""
        if len(self.authors) == 0:
            logger.error("No authors are specified for the AInalysis.")
            return False
        n = 0
        for c in self.contact:
            if c is not None:
                n += 1
        if n == 0:
            logger.error(("No contact information was provided."))
            return False
        if self.name is None:
            logger.error("The AInalysis has no name.")
            return False
        if self.description is None:
            logger.warning("No description was provided.")
        return True

    def make_begin(self):
        """ Creates the header and static top of the webpage and stores it in
        the page property of the :obj:`phenoai.maker.AboutMaker` instance. Any
        content stored in this property before this function is called is
        deleted in the proces."""
        begin = get_template_file('maker.header.html')
        style = get_template_file('maker.style.html')
        begin.format(name=self.name, style=style)
        self.page += begin

    def make_header(self):
        """ Creates the non-static top of the webpage (up to the description)
        and adds it to the page property of the :obj:`phenoai.maker.AboutMaker`
        instance. """
        authors = ''
        contacts = 0
        for author, email in zip(self.authors, self.contact):
            if email is not None:
                authors += '{} <a href="mailto:{}">{}</a><br />'.format(
                    author, email, email)
                contacts += 1
            else:
                authors += "{}<br />".format(author)
        if authors == '':
            logger.error("No author information was provided.")
            raise exceptions.MakerError("No author information was provided.")
        if contacts == 0:
            logger.warning(("No contact information was supplied for the "
                            "AInalysis description, it is recommended to "
                            "supply this."))

        now = datetime.datetime.now()
        self.page += ('<h2>PhenoAI AInalysis</h2><h1>{}</h1><h2>version {} '
                      '({})</h2><p id="authors">{}</p><p id="description">{}'
                      '</p>\n').format(self.name,
                                       self.configuration["ainalysisversion"],
                                       now.strftime("%Y-%m-%d %H:%M"), authors,
                                       self.description)

    def make_body(self):
        """ Creates the code for the non-static body part of the webpage
        (everything between the description and the footer) and adds this code
        to the page property of the :obj:`phenoai.maker.AboutMaker` instance.

        If the associated AInalysis contains a classifier that is calibrated by
        PhenoAI, a calibration plot will be created and stored as
        calibration_curve.png at the location defined in the location property
        of the :obj:`~phenoai.maker.AboutMaker` instance."""

        # Meta information
        phenoaidb = self.configuration["unique_db_id"]
        if phenoaidb is not None:
            phenoaidb = '<i>No</i>'
        self.page += '<h3>Meta information</h3>\n'
        self.make_cell('Default ainalysis ID', self.configuration["defaultid"],
                       ("The default AInalysis ID defines how the AInalysis "
                        "is named by phenoai.core.PhenoAI objects when no "
                        "AInalysis name is provided. This is also the name "
                        "that will be used by AInalysisResults objects to "
                        "uniquely identify the AInalysis from which the "
                        "results originate."))
        self.make_cell('In PhenoAI Database', phenoaidb,
                       ("This flag indicates if this AInalysis can be found "
                        "in the PhenoAI AInalysis database. If this is the "
                        "case, PhenoAI will automatically query the server if "
                        "there is an update available when the AInalysis is "
                        "loaded and the user will be notified if this is "
                        "indeed the case. The AInalysis is never "
                        "automatically updated."))

        # Estimator information
        # Package
        if self.configuration["class"] == "sklearnestimator":
            packagedef = 'scikit-learn (<a href='\
                '"http://www.scikit-learn.org/">website</a>)'
        elif self.configuration["class"] == "kerasestimator":
            packagedef = 'keras (<a href="http://www.keras.io">website</a>)'
        # Output
        output = self.configuration["output"]
        if self.configuration["type"] == "classifier":
            for c, desc in self.configuration["classes"].items():
                output += ('<p class="subvalue"><span class="classint">{}'
                           '</span>: <span class="classinfo">{}</span>'
                           '</p>').format(c, desc)
        self.page += '<h3>Estimator information</h3>\n'
        self.make_cell('Packages', packagedef,
                       ("The package in which the trained machine learning "
                        "algorithm is defined. Can currently be Keras or "
                        "scikit-learn."))
        self.make_cell('Estimator type', self.configuration["type"],
                       ("Indicates if the output of the estimator in the "
                        "AInalysis is meant to be interpreted as discrete "
                        "(classifier) or as contiuous (regressor). If the "
                        "estimator is a classifier, details about the "
                        "classifier are given below in the block 'Classifier "
                        "details'."))
        self.make_cell('Output', output,
                       ("Indicates if the output of the estimator in the "
                        "AInalysis is meant to be interpreted as discrete "
                        "(classifier) or as contiuous (regressor). If the "
                        "estimator is a classifier, details about the "
                        "classifier are given below in the block 'Classifier "
                        "details'."))
        if self.configuration["type"] == "classifier":
            self.page += '<h4>Calibration</h4>\n'
            self.make_cell(
                'Calibrated',
                utils.bool_to_text(
                    self.configuration["classifier.calibrated"]),
                ("Whether or not the estimator has calibrated output, "
                 "i.e. the continuous output can be interpreted as a "
                 "probability."))
            if not self.configuration["classifier.calibrated"]:
                self.make_cell(
                    'Let PhenoAI calibrate',
                    utils.bool_to_text(
                        self.configuration["classifier.calibrate"]),
                    ("Indicates if PhenoAI will do some calibration "
                     "itself based on information provided at creation of "
                     "the AInalysis."))
                if self.configuration["classifier.calibrate"]:
                    plt.plot(self.configuration["classifier.calibrate.bins"],
                             self.configuration["classifier.calibrate.values"],
                             color='k',
                             linewidth=2)
                    plt.axhline(0.5, linestyle='--', color='k')
                    plt.axhline(0.68, linestyle='--', color='k')
                    plt.axhline(0.95, linestyle='--', color='k')
                    plt.grid()
                    plt.xlabel("Classifier output")
                    plt.ylabel("Confidence in classification")
                    plt.savefig("{}/calibration_curve.png".format(
                        self.location))
                    self.make_cell('Calibration curve',
                                   ('<img src="calibration_curve.png" '
                                    'alt="Calibration curve" />'),
                                   ('Curve indicating how estimator output '
                                    'will be mapped. Value to which is mapped '
                                    'indicates the probability the provided '
                                    'classification is correct.'))

        # Dependencies and validated versions
        libraries = ""
        for l in self.configuration["libraries"]:
            libraries += "<strong>{}</strong>: ".format(l)
            libraries += ', '.join(self.configuration["libraries"][l])
            libraries += '<br />'
        phenoai = ""
        for v in self.configuration["phenoaiversion"]:
            if phenoai == "":
                phenoai = str(v)
            else:
                phenoai += ", " + str(v)
        self.page += '<h3>Dependencies and validated versions</h3>\n'
        self.make_cell('PhenoAI', phenoai,
                       ("The version numbers of PhenoAI for which this "
                        "AInalysis is tested and validated. If the version "
                        "number of your PhenoAI package is not in this list "
                        "you might encounter unexpected behaviour or errors."))
        self.make_cell('Dependencies', libraries,
                       ("The versions of dependency libraries for which this "
                        "AInalysis is tested and validated. The libraries "
                        "listed here have to be installed. Installing "
                        "different versions of the libraries than listed here "
                        "might yield unexpected behaviour or errors."))

        # Extra configuration
        # File reading
        define_fileformats = False
        if self.configuration["filereader"] == "function":
            filereader = "Yes, via function read( data ) in functions.py"
            define_fileformats = True
        elif isinstance(self.configuration["filereader"], list):
            filereader = "<p>Yes, via .slha interface:</p><br />"
            for i, p in enumerate(self.configuration["parameters"]):
                block = self.configuration["filereader"][i][0]
                switch = self.configuration["filereader"][i][1]
                filereader += ('<div class="filereader_line"><div class="'
                               'filereader_num">{}.</div><div class="'
                               'filereader_name">{}</div><div class="'
                               'filereader_block"><span>BLOCK</span> {}</div>'
                               '<div class="filereader_switch"><span>SWITCH'
                               '</span> {}</div></div>').format(
                                   i, p[0], block, switch)
        else:
            filereader = "No"
        # Mapping
        if self.configuration["mapping"] == "function":
            mapping = ("Yes, via function mapping( data ) function in "
                       "functions.py")
        elif (isinstance(self.configuration["mapping"], float)
              and not isinstance(self.configuration["mapping"], bool)):
            mapping = ("Yes, relocate points to {}*range the the inside of "
                       "the boundary if originally outside of the "
                       "boundary").format(self.configuration["mapping"])
        else:
            mapping = "No"

        # Parameters
        parameters = ''
        for n, i in enumerate(self.configuration["parameters"]):
            parameter = get_template_file('maker.parameter.html')
            parameter = parameter.format(
                num=n,
                name=i[0],
                unit=i[1],
                min=i[2],
                max=i[3]
            )
            parameters += parameter
        self.page += '<h3>Parameters and training ranges (in order)</h3>\n'
        self.page += ('<div id="parameters" class="color">\n{}<br />'
                      '</div>').format(parameters)
        self.make_cell('Mapping', mapping,
                       ("Sets if data points outside of the training box (see "
                        "below) will be moved to the inside of the training "
                        "box and if so how this replacing is done exactly."))

        self.page += '<h3>Extra configuration</h3>\n'
        self.make_cell('File reading', filereader,
                       ("Defines if the AInalysis has a definition on how to "
                        "read files. It does not define uniquely which files "
                        "can be read."))
        if define_fileformats:
            formats = self.configuration["filereader.formats"]
            if isinstance(formats, list):
                formats = ', '.join(formats)
            self.make_cell('File formats', formats,
                           ("Indicates which file type can be read by the "
                            "file reader. The file format is not thoroughly "
                            "validated, only the extensions are checked. If "
                            "the provided file does not match any of the "
                            "extensions provided here, a warning is given, "
                            "but normal procedure continues."))

    def make_cell(self, name, content, description):
        """ Creates the code for a single row in the about.html page and adds
        this code to the page property of the :obj:`phenoai.maker.AboutMaker`
        instance

        Parameters
        ----------
        name: :obj:`str`
            Name of the property as it will be displayed

        content: any object that can be displayed as :obj:`str`
            Property that will be displayed

        description: :obj:`str`
            Description of the property written in such a way that it makes
            clear what the property exactly does. """
        cell = get_template_file('maker.cell.html')
        cell = cell.format(name=name, content=content, description=description)
        self.page += cell

    def make_footer(self):
        """ Creates the footer for the about.html page and adds this code to
        the page property of the :obj:`phenoai.maker.AboutMaker` instance. """
        footer = get_template_file('maker.footer.html')
        footer = footer.format(
            version=__version__,
            datetime=datetime.datetime.now()
        )
        self.page += footer

    def make(self, configuration, location):
        """ Create the about.html page

        This method starts the construction of the about.html page based on the
        provided configuration dictionary and stores the code (once it is
        generated) in an about.html file at the provided location.

        Parameters
        ----------
        configuration: :obj:`dict`
            Configuration dictionary as made by a
            :obj:`phenoai.maker.ConfigurationMaker` instance or as loaded by an
            `phenoai.ainalyses.AInalysisConfiguration` instance. location:
            :obj:`str` Location where the about.html page will be stored."""
        self.configuration = configuration
        if location[-1] == '/':
            location = location[:-1]
        self.location = location

        self.make_begin()
        self.page += "\n\n<!-- HEADER STARTS HERE -->\n\n"
        self.make_header()
        self.page += "\n\n<!-- HEADER STOPS HERE -->\n\n"
        self.page += "\n\n<!-- CONFIG CONTENT STARTS HERE -->\n\n"
        self.make_body()
        self.page += "\n\n<!-- CONFIG CONTENT STOPS HERE -->\n\n"
        self.make_footer()

        # Store
        with open('{}/about.html'.format(self.location), 'w') as about:
            about.write(self.page)


class ConfigurationMaker(AInalysisConfiguration):
    """ The ConfigurationMaker class is used in the
    :obj:`phenoai.maker.AInalysisMakerz to create configuration files from
    scratch. It uses the :obj:`phenoai.ainalyses.AInalysisConfiguration`
    class as partent class. In normal circumstances the user should not be
    needing to create call instances of this class directly. """

    def __init__(self):
        self.reset()

    def reset(self):
        """ Sets the configuration to its default values:

        - unique_db_id: `None`
        - default_id: `None`
        - ainalysisversion: `1`
        - phenoaiversion: *automatically determined from package installation*
        - libraries: empty dictionary
        - output: `None`
        - filereader: `False`
        - mapping: `False`
        - parameters: `None` """
        # Set defaults for configuration
        self.configuration = {}
        self.set("unique_db_id", None)
        self.set("default_id", None)
        self.set("ainalysisversion", 1)
        self.set("phenoaiversion", [__version__])
        self.set("libraries", {})
        self.set("output", None)
        self.set("filereader", False)
        self.set("mapping", False)
        self.set("parameters", None)

    def reset_classifier_block(self):
        """ Sets the classifier.* block in the configuration to its default
        values.

        - classifier.classes: `None`
        - classifier.calibrated: `False`
        - classifier.calibrate: `False`"""
        self.set("classifier.classes", None)
        self.set("classifier.calibrated", False)
        self.set("classifier.calibrate", False)

    def set(self, parameter, value):
        """ Sets a parameter in the configuration to a user-defined value.

        Parameters
        ----------
        parameter: :obj:`str`
            Name of the parameter to be set.

        value: any
            Value of the parameter to be set."""
        self.configuration[parameter] = value

    def get_parameter_entry(self, parameter):
        """ Creates the configuration.yaml entry for a parameter.

        Creates a string of a parameter indicated by the user. This method is
        used to store the parameters in the configuration.yaml file in the
        :meth:`phenoai.maker.ConfigurationMaker.save` method.

        Parameters
        ----------
        parameter: :obj:`str`
            Name of the parameter to create the string of."""

        if parameter not in self.configuration:
            return ""
        string = "{}: ".format(parameter)
        value = self.configuration[parameter]
        if (not isinstance(value, list) and not isinstance(value, np.ndarray)
                and not isinstance(value, dict)):
            if value is not None:
                string += str(value)
        elif isinstance(value, dict):
            for k, val in value.items():
                if isinstance(val, list):
                    lijst = "["
                    for w in val:
                        lijst += str(w)
                        if w != val[-1]:
                            lijst += ", "
                    val = lijst + "]"
                string += "\n    {}: {}".format(k, val)
        else:
            string += "["
            if isinstance(value, np.ndarray):
                value = value.tolist()
            if not isinstance(value[0], list):
                for i, val in enumerate(value):
                    string += str(val)
                    if i != len(value) - 1:
                        string += ", "
            else:
                indent = len(string)
                for i, val in enumerate(value):
                    string += "["
                    for j, valval in enumerate(val):
                        string += str(valval)
                        if j != len(val) - 1:
                            string += ", "
                    string += "]"
                    if i != len(value) - 1:
                        string += ",\n"
                        string += " " * indent
            string += "]"
        return string

    def validate(self, validate_checksum=False):
        """ Validate the configuration

        Calls the :obj:`phenoai.ainalyses.AInalysisConfiguration.validate`
        parent method of this class.

        Parameters
        ----------
        validate_checksum : :obj:`bool`. Optional
            Boolean indicating if the created checksum should be validated as
            well. Default is `False`.

        Returns
        -------
        valid: :obj:`bool`
            Boolean value indicating if the configuration was good as-is. If
            any value in the configuration file has to be altered or new ones
            had to be added, this value will be `False`. Else it will be
            `True`. """
        return super(ConfigurationMaker, self).validate(validate_checksum)

    def save(self, path):
        """ Save the configuration in a .yaml file at the indicated path.

        Parameters
        ----------
        path: :obj:`str` Path the path to where the configuration should be
            stored. This should include the file itself."""
        # Define parameter order (with blank lines)
        order = [[
            "unique_db_id", "defaultid", "ainalysisversion", "phenoaiversion",
            "type", "class", "libraries"
        ], ["output", "classes"],
                 [
                     "classifier.calibrated", "classifier.calibrate",
                     "classifier.calibrate.bins", "classifier.calibrate.values"
                 ], ["filereader", "filereader.formats"], ["mapping"],
                 ["parameters"]]
        # Open configuration file for writing
        with open(path, "w") as f:
            # Loop over all blocks
            for block in order:
                written = 0
                # Loop over all items
                for item in block:
                    if item in self.configuration:
                        f.write(self.get_parameter_entry(item) + "\n")
                        written += 1
                if written != 0:
                    f.write("\n")


def generate_calibration_arrays(truth, prediction, nbins=100):
    """ Creates arrays needed for calibration by PhenoAI of two-class
    classifiers.

    This method creates calibration values for predictions made by two-class
    classifiers. To do this, it creates two histograms with nbins, one for each
    of the truth classes and calculates for each of the bins the ratio of the
    majority class in that bin with the total data amount in that bin (sum of
    two histograms). This value is then a probability that the prediction for
    predictions in that bin is then correct.

    The nbins argument of this function can be quite sensitive if the amount of
    data is not large enough. It is advised to test the output of this function
    and see if the truth - probability curve is reasonably smooth.

    Parameters
    ----------
    truth : :obj:`numpy.ndarray`
        Defines true labels used in calibration. Should have same length as
        'prediction'.

    prediction: :obj:`numpy.ndarray`
        Predictions belonging to the true labels ('truth') used in calibration.
        Should have the same length as 'truth'.

    nbins: :obj:`int`. Optional
        Number of bins to create calibrations for (i.e. number of unique
        probabilities to be created). Default is 100.

    Returns
    -------
    centers: :obj:`numpy.ndarray`
        Numpy array containing the centers of the histogram bins (see above
        for explanation).

    propabilities: :obj:`numpy.ndarray`
        Calculated probabilities that the predicted class is correct (see
        above for explanation)."""
    # Check if truth is nparray (+ reshape)
    if not isinstance(truth, np.ndarray) and not isinstance(truth, list):
        raise Exception(("Truth array for calibration should be a"
                         "numpy.ndarray or a list"))
    if isinstance(truth, list):
        truth = np.array(truth)
    truth = truth.reshape(-1, 1)

    # Check if prediction is nparray (+ reshape)
    if (not isinstance(prediction, np.ndarray)
            and not isinstance(prediction, list)):
        raise truth(("Truth array for calibration should be a numpy.ndarray "
                     "or a list"))
    if isinstance(prediction, list):
        prediction = np.array(prediction)
    prediction = prediction.reshape(-1, 1)

    # Check if truth and pred have same shape
    if len(prediction) != len(truth):
        raise exceptions.MakerError(("Truth and prediction array for "
                                     "calibration should have the same "
                                     "length."))

    # Check if truth is binary
    if len(np.unique(truth)) != 2:
        raise exceptions.MakerError(("Calibration arrays can only be made "
                                     "for binary classification problems."))

    # Check if calibration_nbins is an integer
    if not isinstance(nbins, int):
        raise exceptions.MakerError(("Number of calibration bins should be "
                                     "an integer."))

    # Create histograms for calibration
    bins = np.linspace(min(np.amin(truth), np.amin(prediction)),
                       max(np.amax(truth), np.amax(prediction)), nbins + 1)
    mins = np.array([
        prediction[i] for i in range(len(prediction))
        if truth[i] == np.amin(truth)
    ])
    maxs = np.array([
        prediction[i] for i in range(len(prediction))
        if truth[i] == np.amax(truth)
    ])
    vmins, _ = np.histogram(mins, bins)
    vmaxs, _ = np.histogram(maxs, bins)
    # Define values and bin centers
    probabilities = np.maximum(vmins, vmaxs) / (vmins + vmaxs)
    nans = np.isnan(probabilities)
    if nans.any():
        probabilities[nans] = 0.5
        logger.warning(("Calibration yielded NaN values. These are "
                        "substituted for 0.5 in order to guarantee the "
                        "workings of PhenoAI."))
    centers = bins[:-1] + (bins[1] - bins[0]) / 2.0
    # Return centers and values
    return (centers, probabilities)


def update_checksums(location):
    """ Updates the checksums of an AInalysis

    Parameters
    ----------
    location: :obj:`str`
        Path to the AInalysis folder. """
    csums = utils.calculate_ainalysis_checksums(location)
    with open(location + "/checksums.sfv", "w") as f:
        for cname in csums:
            f.write("{:<24}{}\n".format(cname, csums[cname]))


def get_template_file(filename):
    """ Gets the content of one of the template files in the PhenoAI package

    Parameters
    ----------
    filename: str
        Name of the template file to be read

    Returns
    -------
    template: str
        Contents of the requested file"""
    path = '/'.join(('templates', filename))
    template = pkg_resources.resource_string('phenoai', path)
    template = template.decode("utf-8")
    return template
