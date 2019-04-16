""" The classes module implements classes from which other classes in the
phenoai package are derived. Currently these classes are
:class:`~phenoai.containers.Estimator` and
:class:`~phenoai.containers.Configuration`. """

from copy import deepcopy
import os.path

import numpy as np

from phenoai import exceptions
from phenoai import io
from phenoai import logger
from phenoai import utils


class Estimator:
    """ The basic interface methods for estimator classes in the estimators
    module.

    Attributes
    ----------
    est: `estimator`
        The estimator to which Estimator derived classes provide an interface.
        Type of this variable is determined by the derived class.
    path: :obj:`str`
        Path to the stored estimator. """

    def __init__(self, path=None, load=False):
        """ Initialises the Estimator object.

        Parameters
        ----------
        path: :obj:`str`
            Path to the location of the stored estimator.
        load: :obj:`bool`, optional
            Defines if the estimator has to be loaded on initialisation of the
            interface class. Default is `False`. """
        if path is not None:
            if not os.path.isdir(path):
                raise FileNotFoundError(("Estimator could not be found at "
                                         "path '{}'.").format(path))
            self.est = None
            if path[-1] == "/":
                path = path[:-1]
            self.path = path
            if load:
                self.load()

    def clear(self):
        """ Removes the loaded estimator from memory.

        This saves memory, but does mean that the estimator has to be reloaded
        as soon as a new prediction with it has to be made."""
        self.est = None

    def is_loaded(self):
        """ Checks if the estimator is loaded in the
        :attr:`~phenoai.containers.Estimator.estimator` attribute.

        Returns
        -------
        is_loaded: :obj:`bool`
            `True` if estimator is currently loaded, `False` otherwise."""
        return (self.est is not None)

    def load(self):
        """ This method is only implemented in derived classes. If called on
        an Estimator instance a :exc:`phenoai.exceptions.AInalysisException`
        is raised. """
        raise exceptions.AInalysisException(
            ("Cannot call validate method on Estimator instance. Only "
             "available in instances of classes derived from the Estimator "
             "class."))


class Configuration:
    """ The basic interface to configuration classes.

    This base class defines all loading, resetting and printing functions for
    configuration classes throughout the package (currently only
    :class:`phenoai.ainalyses.AInalysisConfiguration`). Handles only
    configuration files following the .yaml format, see http://www.yaml.org for
    syntax and conventions.

    Attributes
    ----------
    configuration: :obj:`dict`
        Content of the configuration. Contains an empty dictionary if
        configuration is not loaded. By default set to an empty dictionary.
    folder: :obj:`str`
        AInalysis folder. Is deduced from provided path of the AInalysis
        configuration. Default is `None`.
    path: :obj:`str`
        Location where the .yaml configuration is stored. Default is `None`.
    validated: :obj:`bool`
        Boolean indicating if the configuration stored in the configuration
        property has been validated by the validate method in the derived
        class. Default is `False`. """

    def __init__(self, path=None, entries=None):
        """ Initialises the Configuration object.

        Constructor parameters
        ----------------------
        path: :obj:`str`, optional
            Location where the .yaml configuration file is stored. Default is
            `None`.
        entries: :obj:`dict`, `None`, optional
            Dictionary containing the contents of a loaded configuration .yaml
            file. Will be used as the configuration if `path` is set to `None`.
            If set to `None` the configuration will default to an empty
            dictionary. Default is `None`. """
        self.configuration = {}
        self.path = None
        self.folder = None
        if path is not None:
            self.load(path)
        elif entries is not None and isinstance(entries, dict):
            self.configuration = entries
        self.validated = False

    def __getitem__(self, key):
        return self.configuration[key]

    def __setitem__(self, key, value):
        self.configuration[key] = value

    def get(self, key=None):
        """ Returns the configuration in dictionary form or an entry of the
        configuration

        Parameters
        ----------
        key: :obj:`str`, optional.
            Key of the dictionary entry that has to be returned. If no key or
            `None` was provided the entire dictionary is returned. Default is
            `None`.

        Returns
        -------
        configvalue: :obj:`dict`, dictionary entry.
            If key was provided as input argument the entry of the
            configuration with that key is returned. If no key or `None` was
            provided, the entire configuration directionary is returned."""
        if key is None:
            return self.configuration
        return self.configuration[key]

    def show(self, printdict=None):
        """ Prints the entire configuration via the :func:`print` command.

        Parameters
        ----------
        printdict: :obj:`dict`, optional
            The dictionary that has to be printed by the :func:`print` command.
            If no dictionary or `None` is provided the self.configuration
            property will be used instead. Default is `None`."""
        if printdict is None:
            printdict = self.configuration
        maxkeylength = 0
        for k in printdict.keys():
            if not isinstance(k, str):
                printdict[str(k)] = printdict[k]
                del (printdict[k])
                k = str(k)
            if len(k) > maxkeylength:
                maxkeylength = len(k)
        for key, value in sorted(printdict.items()):
            if isinstance(value, dict):
                self.show(printdict[key])
            elif isinstance(value, list):
                if len(value) == 1:
                    print("{} list of length {}: [{}]".format(
                        key.ljust(maxkeylength + 6), len(value), value[0]))
                elif len(value) <= 5:
                    print(value)
                    liststr = utils.multi_join(value)
                    print("{} list of length {}: [{}]".format(
                        key.ljust(maxkeylength + 6), len(value), liststr))
                else:
                    print("{} list of length {}: [{}, {}, ... {}, {}]".format(
                        key.ljust(maxkeylength + 6), len(value), value[0],
                        value[1], value[-2], value[-1]))
            else:
                print(key.ljust(maxkeylength + 6) + str(value))

    def load(self, path):
        """ Loads the configuration indicated by the provided path.

        The loaded configuration is stored as a dictionary in the configuration
        property of the object. The provided path is stored in the path
        property. Configuration files have to follow the .yaml format (see
        http://www.yaml.org/).

        Parameters
        ----------
        path: :obj:`str`
            Path the the the configuration .yaml file."""
        self.configuration = io.read_yaml(path)
        self.path = path
        pathparts = path.split('/')
        folderparts = pathparts[:-1]
        self.folder = "/".join(folderparts)


class AInalysisResults:
    """ Container for and interface to results of an AInalysis instance.

    The :obj:`~phenoai.containers.AInalysisResults` class functions as a
    container for results produced by an AInalysis instance and provides
    methods to access these results efficiently.

    Attributes
    ----------
    result_id: :obj:`str`
        ID of the result object. Equal to the AInalysisID of the AInalysis that
        produced the results stored in this instance.
    configuration: :class:`phenoai.ainalyses.AInalysisConfiguration`
        Configuration of the AInalysis that produced the results stored in this
        instance.
    data: :obj:`numpy.ndarray`
        Data that has been subjected to prediction (after possible mapping).
    data_ids: :obj:`list(str)`
        List of unique IDs (`str`) via which data points can be identified. If
        set, data points and their classifications and predictions can be read
        from the :obj:`~phenoai.containers.AInalysisResults` object by
        referencing their ID. If not set (i.e. ids is set to `None`) this
        functionality is not available.
    mapped: :obj:`list`, :obj:`bool`
        `False` if no mapping has taken place. If mapping has taken place, this
        property stores a list of booleans indicating on a per datapoint basis
        if that specific datapoint has been mapped or not. In that case the
        data stored in the data property of this
        :obj:`~phenoai.containers.AInalysisResults` instance is this mapped
        data.
    predictions: numpy.ndarray
        Results of the prediction method of the estimator stored in the
        AInalysis object with the data stored in the data property of this
        :obj:`~phenoai.containers.AInalysisResults` instance. """

    def __init__(self,
                 result_id,
                 configuration,
                 data,
                 data_ids=None,
                 mapped=False,
                 predictions=None):
        """ Initialises the AInalysisResults object

        Parameters
        ----------
        result_id: :obj:`str`
            ID of the result object. Equal to the AInalysisID of the AInalysis
            that produced the results stored in this instance.
        configuration: :class:`phenoai.ainalyses.AInalysisConfiguration`
            Configuration of the AInalysis that produced the results stored in
            this instance.
        data: :obj:`numpy.ndarray`
            Data that has been subjected to prediction (after possible
            mapping).
        data_ids: :obj:`list(str)`, optional
            List if unique IDs (strings) by which data points can be
            identified. If set, data points and their classifications and
            predictions can be read from the
            :obj:`~phenoai.containers.AInalysisResults` object by referencing
            their ID. If not set (i.e. ids is set to `None`) this functionality
            is not available. Default is `None`.
        mapped: :obj:`bool`, optional.
            Boolean indicating if the data has been mapped before prediction.
            If True, the data stored in the data property of this
            :obj:`~phenoai.containers.AInalysisResults` instance is this mapped
            data. Default is `False`.
        predictions: :obj:`numpy.ndarray`, optional
            Results of the prediction method of the estimator stored in the
            AInalysis object with the data stored in the data property of this
            :obj:`~phenoai.containers.AInalysisResults` instance. Default is
            `None`. """
        self.result_id = result_id
        self.data = data
        self.data_ids = data_ids
        self.mapped = mapped
        self.configuration = Configuration(entries=configuration.configuration)
        self.predictions = predictions

    def get(self, array, reference=None):
        """ Returns the content of the array at location of the reference

        Selects and returns the rows from the provided array which are
        referenced by the reference argument of this function.

        Parameters
        ----------
        array: :obj:`numpy.ndarray`
            Numpy array from which rows have to be selected
        reference: :obj:`int`, :obj:`str`, :obj:`numpy.ndarray`,
            :obj:`list(int)`, :obj:`list(str)`. Optional
            If this reference is an :obj:`int`, that row of the array with that
            integer as row number will be returned. If the reference is a
            :obj:`str`, the rownumber of the entry in the
            :attr:`~phenoai.containers.AInalysisResults.data_ids` attribute
            equal to this reference will be used instead. The reference
            variable can also be a :obj:`list` or :obj:`numpy.ndarray` of
            :obj:`int` and/or :obj:`str`. In that case a :obj:`numpy.ndarray`
            with the selected entries will be returned. Default is `None`.

        Returns
        -------
        selection: :obj:`numpy.ndarray`
            Selected row(s) from array corresponding to the provided
            reference(s). """

        if reference is None:
            return array
        if isinstance(reference, int):
            return array[reference]
        if isinstance(reference, str):
            for i, did in enumerate(self.data_ids):
                if reference == did:
                    return array[i]
        elif isinstance(reference, (np.ndarray, list)):
            if len(array.shape) == 1:
                a = len(array)
            else:
                a = len(array[0])
            selection = np.zeros((len(reference), a))
            for i, ref in enumerate(reference):
                selection[i, :] = self.get(array, ref)
            return selection
        raise exceptions.ResultsException(("Unknown reference format for get: "
                                           "{}.").format(type(reference)))

    def get_ids(self):
        """ Returns data ids

        Returns
        -------
        ids: :obj:`numpy.ndarray`
            All IDs for the data in this
            :obj:`~phenoai.containers.AInalysisResults` object"""
        return self.data_ids

    def get_data(self, i=None):
        """ Returns data (rows) used for prediction

        Parameters
        ----------
        i: :obj:`int`, :obj:`str, :obj:`list(int)`, :obj:`list(str)`, optional
            Reference used for selecting rows in the data array. See the
            documentation for the get method for allowed values and
            consequences. Default is `None`.

        Returns
        -------
        data: :obj:`numpy.ndarray`
            Selected rows from the data array."""
        return self.get(self.data, i)

    def get_classifications(self, i=None, calibrated=True):
        """ Returns the classification results based on the predictions stored
        in the predictions property.

        Uses the information stored in the
        :attr:`~phenoai.containers.AInalysisResults.configuration` property to
        classify the results in the predictions property. These classifications
        are then returned. If the results are not interpretable as
        classifications (e.g. because the AInalysis implemented a regressor
        instead of a classifier) `None` is returned.

        Classification names or indicators or extracted from the `output` entry
        in the configuration.

        Parameters
        ----------
        i: :obj:`int`, :obj:`numpy.ndarray`. Optional
            Reference used for generating classifications from the predictions
            array. See the documentation for the get method for allowed values
            and consequences. Default is `None`.
        calibrated: :obj:`bool`. Optional
            Boolean indicating if prediction results have to be calibrated. See
            documentation for the
            :meth:`~phenoai.containers.AInalysisResults.get_predictions` method
            for requirements. Default is `True`.

        Returns
        -------
        classifications: `numpy.ndarray`
            Requested classifications. """
        if not self.configuration["type"] == "classifier":
            return None
        # Select data
        predictions = self.get_predictions(i, calibrated)
        # Get maxima
        if len(predictions.shape) == 1:
            maxs = np.argmax(predictions, axis=0)
        else:
            maxs = np.argmax(predictions, axis=1)
        # Return classifications
        return self.configuration["classes"][maxs]

    def get_predictions(self, i=None, calibrated=True):
        """ Returns the predictions stored in
        :attr:`~phenoai.containers.AInalysisResults.predictions` property.

        Returns the prediction results stored in the
        :attr:`~phenoai.containers.AInalysisResults.predictions` property of
        this object. By setting the `calibrated` argument to `True` (default),
        the prediction results will first be calibrated before returning, if
        all of the following requirements are met:

        - the estimator is a classifier;
        - the estimator is not already calibrated;
        - the configuration validly defines a method to calibrate the results.

        If any of these requirements is violated, the bare prediction results
        are returned. If `calibrated` is set to `False`, the raw prediction
        results will be returned either way.

        Parameters
        ----------
        i: :obj:`int`, :obj:`numpy.ndarray`, optional
            Reference used for selecting rows in the predictions array. See the
            documentation for the get method for allowed values and
            consequences. Default is `None`.
        calibrated: :obj:`bool`, optional
            Boolean indicating if prediction results have to be calibrated. See
            documentation for this method for requirements. Default is `True`.

        Returns
        -------
        predictions: :obj:`numpy.ndarray`
            Requested (calibrated) predictions. """

        # Get predictions
        preds = self.get(self.predictions, i)
        # Check requirements for calibration
        if calibrated:
            if self.configuration["type"] == 'classifier':
                if not self.configuration["classifier.calibrated"]:
                    if self.configuration["classifier.calibrate"]:
                        # Get calibration configuration
                        bins = self.configuration["classifier.calibrate.bins"]
                        values = self.configuration[
                            "classifier.calibrate.bins"]
                        # Perform calibration
                        predscal = np.zeros(len(preds))
                        for j, prediction in enumerate(preds):
                            b = np.argmin(np.abs(bins - prediction))
                            predscal[j] = values[b]
                        return predscal
        return preds

    def is_outlier(self, i=None, use_map_target_area=False):
        """ Returns information about whether or not data used in prediction
        lies outside of region sampled with training data.

        Checks for all data selected via reference variable :obj:`i` if it is
        outside of the region from which training data was sampled for the
        training of the estimator of the AInalysis that created this
        :obj:`~phenoai.containers.AInalysisResults` object. By setting the
        :obj:`use_map_target_area` argument to `True` the reference area will
        be taken as the target area for the mapping procedure (if any is
        defined via a floating point number in the AInalysis configuration).
        Returns a numpy.ndarray containing booleans indicating if the data
        points are outside of the sample region (`True`) or not (`False`).

        Note that if mapping took place before prediction (checkable via the
        is_mapped method) all values returned will be False.

        Parameters
        ----------
        i: :obj:`int`, :obj:`numpy.ndarray`, optional
            Reference used for selecting data for which the outsiderness has to
            be determined. See the documentation for the get method for allowed
            values and consequences. Default is `None`.
        use_map_target_area: :obj:`bool`, optional
            Use the mapping target area as reference area instead of the area
            from which training data was sampled. If set to `True` but the
            mapping was not configured via a floating point value in the
            AInalysis configuration, the method will continue as if this value
            was set to `False`. Default is `False`.

        Returns
        -------
        outsider: :obj:`numpy.ndarray(bool)`
            Numpy array containing booleans. `True` if data point is an
            outsider, `False` otherwise."""

        if (not isinstance(self.configuration["mapping"], float)
                and use_map_target_area):
            raise exceptions.ResultsException(
                "No mapping target area defined in AInalysis configuration.")
        selection_mins = self.get(self.data, i)
        selection_maxs = deepcopy(selection_mins)
        for j in range(len(self.configuration["parameters"])):
            i_min = self.configuration["parameters"][i][2]
            i_max = self.configuration["parameters"][i][3]
            if use_map_target_area:
                r = (self.configuration["parameters"][i][3] -
                     self.configuration["parameters"][i][2])
                i_min += r * self.configuration["mapping"]
                i_max -= r * self.configuration["mapping"]
            selection_mins[j] -= i_min
            selection_maxs[j] -= i_max
        outofrange = (selection_mins[selection_mins < 0] * 1.0 +
                      selection_maxs[selection_maxs > 0] * 1.0)
        return np.sum(outofrange) == 1.0

    def is_mapped(self, i=None):
        """ Returns information about whether or not provided data was mapped
        before prediction took place.

        Parameters
        ----------
        i: :obj:`int`, :obj:`numpy.ndarray`, optional
            Reference used for selecting data of which mapping information is
            requested. See the documentation for the get method for allowed
            values and consequences. Default is `None`.

        Returns
        -------
        mapped_global: :obj:`bool`
            Boolean indicating if mapping procedure has been called at all. Can
            indicate that `map_data` was set to `False` by the user (or left at
            this default value) at running the AInalysis or that the AInalysis
            does not support data mapping.
        mapped: :obj:`numpy.ndarray(bool)`, :obj:`None`
            If `mapped_global` is `True` this variable will contain a numpy
            array filled with :obj:`bool`s indicating per data point indicated
            via reference variable :obj:`i` if it was mapped. This variable
            will contain `None` if `mapped_global` was `False`. """
        if ((isinstance(self.mapped, bool) and self.mapped is False)
                or self.mapped is None):
            return (False, None)
        selection = self.get(self.mapped, i)
        return (True, selection)

    def num(self):
        """ Returns the length of the data (i.e. the number of data points)
        stored in the :obj:`~phenoai.containers.AInalysisResults` instance.

        Returns
        -------
        L: :obj:`int`
            Number of data points (and hence the number of predictions) stored
            in the :obj:`~phenoai.containers.AInalysisResults` instance. """
        return len(self.data)

    def __len__(self):
        return self.num()

    def summary(self):
        """ Prints a summary of the contents of this object """
        logger.debug("Print report for AInalysisResults")
        print("---------------------------")
        print("| AInalysisResults report |")
        print("---------------------------")
        print("ID: {}".format(self.result_id))
        print("Length: {}".format(self.num()))
        # Information on data
        contains_data = self.get_data() is not None
        print("Contains data: {}".format(contains_data))
        if contains_data:
            print("  Data shape: {}".format(self.get_data().shape))
            print("  Access via .get_data( args )")
        # Information on Data ids
        contains_data_ids = self.get_ids() is not None
        print("Contains data IDs: {}".format(contains_data_ids))
        if contains_data_ids:
            print("  Data IDs length: {}".format(len(self.get_ids())))
            print("  Get full list via .get_ids()")
            print("  Use as argument in .get_*() methods")
        # Information on data mapping
        data_is_mapped = self.is_mapped()[0]
        print("Data is mapped: {}".format(data_is_mapped))
        if data_is_mapped:
            if isinstance(self.is_mapped()[1], list):
                print("  Data IDs length: {}".format(len(self.is_mapped()[1])))
            elif isinstance(self.is_mapped()[1], np.ndarray):
                print("  Data IDs shape: {}".format(self.is_mapped()[1].shape))
            print("  Access via .is_mapped( args )")
        # Information on Data ids
        contains_predictions = self.get_predictions() is not None
        print("Contains predictions: {}".format(contains_predictions))
        if contains_predictions:
            print("  Predictions shape: {}".format(
                self.get_predictions().shape))
            print("  Access via .get_predictions( args )")


class PhenoAIResults:
    """ Container class for :obj:`phenoai.containers.AInalysisResults`.

    This class functions as a container class for
    :obj:`~phenoai.containers.AInalysisResults` from multiple AInalyses.
    Methods are implemented to aid accessing these instances.

    Attributes
    ----------
    results: :obj:`list`
        List of :obj:`~phenoai.containers.AInalysisResults`. """

    def __init__(self):
        self.results = []

    def add(self, result):
        """ Appends an :obj:`~phenoai.containers.AInalysisResults` instance to
        the container.

        An error is raised if the result that is to be appended has an
        AInalysisID that is already present in the stored
        :obj:`~phenoai.containers.AInalysisResults` instances.

        Parameters
        ----------
        result: :obj:`phenoai.containers.AInalysisResults`
            :obj:`~phenoai.containers.AInalysisResults` that has to be added to
            the container. """
        if self.get(result.result_id) is not None:
            raise exceptions.ResultsException(
                ("Already an AInalysisResults instance stored with "
                 "AInalysisID '{}'").format(result.result_id))
        self.results.append(result)

    def num(self):
        """ Returns the number of stored AInalysisResults in this container.

        Returns
        -------
        n: :obj:`int`
            Number of :obj:`~phenoai.containers.AInalysisResults` stored in
            this container. """
        return len(self.results)

    def __len__(self):
        return self.num()

    def get(self, result_id):
        """ Returns the AInalysis with a given AInalysisID.

        Looks in stored results if there is an
        :obj:`~phenoai.containers.AInalysisResults` instance with provided ID
        as ResultID. If found, this instance is returned. If none is found, the
        provided id is checked if it is an integer in range `0 ...
        len(results)-1`. If so, the result with that internal index is returned
        (corresponding to the ID from
        :meth:`~phenoai.containers.AInalysisResult.get_ids` at that index). If
        no such result could be returned, `None` is returned instead.

        Parameters
        ----------
        result_id: :obj:`str`
            The Result ID of the :obj:`~phenoai.containers.AInalysisResults`
            that has to be returned.

        Returns
        -------
        result: :obj:`phenoai.containers.AInalysisResults`, `None`
            :obj:`~phenoai.containers.AInalysisResults` instance with the
            requested AInalysisID. If no such instance was found, `None` is
            returned. """
        for i in range(len(self.results)):
            if self.results[i].result_id == result_id:
                return self.results[i]
        if (isinstance(result_id, int) and result_id >= 0
                and result_id < len(self.results)):
            return self.results[result_id]
        return None

    def __getitem__(self, result_id):
        return self.get(result_id)

    def get_ids(self):
        """ Returns a list of the ResultIDs of all stored
        :obj:`~phenoai.containers.AInalysisResults` instances.

        Returns
        -------
        ids: :obj:`list`
            List of all ResultIDs fo all stored
            :obj:`~phenoai.containers.AInalysisResults` instances. """
        ids = []
        for i in range(len(self.results)):
            ids.append(self.results[i].result_id)
        return ids

    def summary(self):
        """ Prints a summary of the contents of this object """
        logger.debug("Print report for AInalysisResults")
        print("===========================")
        print("||  PhenoAIResults report  ||")
        print("===========================")
        print("Contains {} AInalysisResults object(s)".format(self.num()))
        print("AInalysisResult IDs:")
        for i in range(self.num()):
            print("  - {} (length: {})".format(
                self.get_ids()[i],
                self.get(self.get_ids()[i]).num()))
        print("Access AInalysisResults objects by id via PhenoAIResults[ id ]")
