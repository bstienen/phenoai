""" Interface to PhenoAI instances running as server

This client module implements the :class:`~phenoai.client.PhenoAIClient` class.
The predict method of this class does not perform any prediction itself, but
sends the provided data to a by the user configured server that is running an
instance of the :class:`phenoai.core.PhenoAI` class in server mode. This server
can be the same machine as the one the :class:`~phenoai.clience.PhenoAIClient`
instance is running on. """

import requests
import json
import numpy as np

from phenoai import exceptions
from phenoai import io


class PhenoAIClient:
    """ Client class to communicate with instances of
    :class:`phenoai.core.PhenoAI` running as a server this (or other) machine.

    The PhenoAIClient implements functionality to communicate with other
    computers on which a :class:`phenoai.core.PhenoAI` instance is running in
    server mode (this computer can be the same as the one the client is running
    on). Communication takes place via HTTP requests, but the interface of this
    class corresponds as much as possible to the one of the
    :class:`~phenoai.core.PhenoAI` class. Before calling the predict method
    however, the user should first set the server via the constructor (or
    afterwards via the set_server method).

    Attributes
    ----------
    address: :obj:`str`
        IP address of the server. 'localhost' is also a valid address.
    ainalysis_ids: :obj:`list(str)`
        List of AInalysis IDs corresponding to the AInalyses to be run at the
        server side. Be aware that only initialized AInalyses will be
        selectable via this list.
    port: :obj:`int`
        Port of the server to which the requests have to be send. """

    def __init__(self, address, port, ainalysis_ids=None):
        """ Initialises the client.

        Parameters
        ----------
        address: :obj:`str`
            IP address of the server. 'localhost' is also a valid address.
        port: :obj:`int`
            Port of the server to which the requests have to be send.
        ainalysis_ids: :obj:`list(str)`, optional.
            List of AInalysis IDs corresponding to the AInalyses to be run at
            the server side. Be aware that only initialized AInalyses will be
            selectable via this list. Default is `None`. """
        self.set_server(address, port)
        self.ainalysis_ids = ainalysis_ids

    def set_server(self, address, port):
        """ Sets the IP address and the port of the server to which the client
        has to send its requests

        Tries to find the server defined via the supplied address and port. If
        no connection can be made via check_connection, a
        :exc:`phenoai.exceptions.ClientException` is raised. If a connection
        could be made the server address and port are saved for all future
        comminucation.

        Parameters
        ----------
        address: :obj:`str`
            IP address of the server. 'localhost' is also a valid address.
        port: :obj:`int`
            Port of the server to which the requests have to be send. """

        # Check if not only one of the two arguments is attempted to be changed
        if (address is None) != (port is None):
            raise exceptions.ClientException(("Server address and port have "
                                              "to be set at the same time"))
        # Check if arguments are not both None. If so, return (nothing has to
        # be changed)
        if address is None:
            return
        # Check if server can be connected
        status = self.check_connection(address, port)
        if not status[0]:
            raise exceptions.ClientException(
                ("Client could not connect to http://{}:{}.\n   {}").format(
                    address, port, status[1]))
        # Set address and port
        self.address = address
        self.port = port

    def check_connection(self, address, port, timeout=5):
        """ Checks if a connection to a server can be made.

        Sends a GET request to the server defined via the address and port
        arguments. If a PhenoAI instance is running on that server that is
        listening to that port, the returned text will be received by this
        function and (`True`, `None`) will be returned. If an error occured in
        the request itself or the processing of this request, (`False`,
        `[errortext]`) will be returned, where `[errortext]` is the description
        of the error raised.

        Parameters
        ----------
        address: :obj:`str`
            IP address of the server. 'localhost' is also a valid address.
        port: :obj:`int`
            Port of the server to which the requests have to be send.
        timeout: :obj:`float`, :obj:None`, optional
            Time to wait for the server to respond. If set to `None`, script
            will wait indefinitely. Default is `5`.

        Returns
        -------
        can_connect: :obj:`bool`
            Boolean indicating if a working connection could be established.
        errortext: :obj:`str`
            If can_connect is `False`, this variable contains the exception
            that caused the connection to fail. If a connection could be
            established, this value is `None`. """

        try:
            if timeout is not None:
                response = requests.get("http://{}:{}".format(address, port))
            else:
                response = requests.get("http://{}:{}".format(address, port))
            response = response.text
            if response[:10] == "phenoai-ok":
                return (True, None)
            if "] Connection refused" in response:
                return (False,
                        ("Connection was refused, is there a PhenoAI"
                         "object running as server on the indicated machine?"))
            return (False, response)
        except Exception as e:
            return (False, str(e))

    def predict(self,
                data,
                map_data=False,
                data_ids=None,
                return_object=True,
                timeout=5):
        """ Queries the server for prediction on provided data.

        Send the provided data to the server set via the set_server method.
        Depening on the value set for the `return_object` argument this
        function will return a copy of the
        :class:`phenoai.containers.PhenoAIResults` object created at the server
        (`True`) or a string representation (`False`). The exact string
        returned depends on the configuration of the
        :class:`~phenoai.core.PhenoAI` object at the server.

        AInalyses used in prediction at the server depend on the values set in
        the `ainalysis_ids` property of this object. Only AInalyses that have
        been added to the :class:`~phenoai.core.PhenoAI` object before
        :meth:`~phenoai.core.PhenoAI.run_as_server` was called are selectable
        through this property.

        In contrast to :class:`~phenoai.core.PhenoAI` objects not running in
        server mode, server :class:`~phenoai.core.PhenoAI` objects can only
        process a single file at a time.

        Parameters
        ----------
        data: :obj:`numpy.ndarray`, :obj:`str`
            Data can be provided as a numpy ndarray, but it can also be the
            location of a single data file (e.g. a .slha file). This file will
            then be read and its complete contents will be sent to the server
            to be read by the file reader interfaces defined for the running
            AInalyses. You can only provide a single file per call.
        map_data: :obj:`bool`, "both", optional
            Boolean indicating if data should be mapped by the AInalyses before
            running a prediction on it. Can also be 'both', indicating that the
            prediction has to be run on the mapped and not-mapped data. Default
            is `False`
        data_ids: :obj:`list`, :obj:`numpy.ndarray`, optional.
            :obj:`List` or :obj:`numpy.ndarray` containing IDs for the provided
            data. Should have same length as data array. Default is `None`.
        return_object: :obj:`boolean`, optional
            Boolean indicating if the function has to return a copy of the
            PhenoAIResults object created at the server (`True`) or a string
            representation of it (`False`). If a string has to be returned, the
            contents of this string is determined by the server configuration
            (see :meth:`phenoai.core.PhenoAI.run_as_server` method). Default is
            `True`.
        timeout: :obj:`float`, `None`, optional
            Time to wait for the server to respond. If set to `None`, script
            will wait indefinitely. Default is `5`.

        Returns
        -------
        results: :obj:`~phenoai.containers.PhenoAIResults`, :obj:`str`
            Prediction results created at the server. Type of this value is
            controlled by the value of the `return_object` argument of this
            method. """

        # Create dictionary for the post request
        postdict = {"mapping": 1.0 * bool(map_data)}
        # Add ainalysis_ids
        if self.ainalysis_ids is None:
            postdict["ainalysis_ids"] = json.dumps("all")
        elif isinstance(self.ainalysis_ids, str):
            postdict["ainalysis_ids"] = json.dumps([self.ainalysis_ids])
        elif isinstance(self.ainalysis_ids, list):
            postdict["ainalysis_ids"] = json.dumps(self.ainalysis_ids)
        elif isinstance(self.ainalysis_ids, (float, int)):
            postdict["ainalysis_ids"] = json.dumps([self.ainalysis_ids])
        else:
            raise exceptions.ClientException(
                ("AInalysis IDs provided in ainalysis_ids is not a string, "
                 "float or int (or list of these elements)"))

        # Split different prediction modes
        if isinstance(data, (list, np.ndarray)):
            # Predict labeling from data array
            postdict["mode"] = "values"
            # Check data_ids argument
            if isinstance(data_ids, np.ndarray):
                data_ids = data_ids.tolist()
            if data_ids is None:
                data_ids = False
            elif not isinstance(data_ids, list) and data_ids is not None:
                raise exceptions.ClientException(
                    ("Data IDs have to be provided as list or np.ndarray."))
            # Convert numpy.ndarray to list
            if isinstance(data, np.ndarray):
                data = data.tolist()
            # Check if list has correct format (all rows of same length)
            for i, point in enumerate(data):
                if i == 0:
                    if not isinstance(point, list):
                        data = [data]
                        break
                    length = len(point)
                else:
                    if len(point) != length:
                        raise exceptions.ClientException(("Shape of provided "
                                                          "data list/array "
                                                          "was inconsistent."))
            # Convert list to json and store in postdict
            postdict["data"] = json.dumps(data)
            postdict["data_ids"] = json.dumps(data_ids)

        elif isinstance(data, str):
            # Predict labeling of file
            postdict["mode"] = "file"
            # Read file to string
            filetext = ''
            with open(data) as f:
                filelines = f.readlines()
                filetext = '\n'.join(filelines)
            if filetext == '':
                raise exceptions.ClientException(
                    "File '{}' does not have any content.".format(data))
            # Convert filecontents to json
            postdict["data"] = filetext
            postdict["data_ids"] = json.dumps([data])

        else:
            # No prediction could be made
            raise exceptions.ClientException(
                ("Provided data has to be a list of lists, numpy.ndarray or "
                 "the location of a data file. Provided was '{}'.").format(
                     type(data)))

        # Determine return type
        if bool(return_object):
            postdict["get_results_as_string"] = 0.0
        else:
            postdict["get_results_as_string"] = 1.0

        return self.communicate(postdict, return_object, timeout)

    def communicate(self, post_dictionary, return_object=True, timeout=5):
        """ Sends a request to the server.

        This method is internally used to make a request to the server. As a
        user you should use :meth:`~phenoai.client.PhenoAIClient.predict`
        instead.

        Parameters
        ----------
        post_dictionary: :obj:`dict`
            Dictionary that has to be send by POST command
        return_object: :obj:`bool`, optional
            Boolean indicating if the function has to return a copy of the
            :class:`phenoai.containers.PhenoAIResults` object created at the
            server (`True`) or a string representation of it (`False`). If a
            string has to be returned, the contents of this string is
            determined by the server configuration (see
            :meth:`phenoai.core.PhenoAI.run_as_server`). Default is `True`
        timeout: :obj:`float`, `None`, optional
            Time to wait for the server to respond. If set to `None`, script
            will wait indefinitely. Default is `5`.

        Returns
        -------
        results: :class:`phenoai.containers.PhenoAIResults`, :obj:`str`
            Prediction results created at the server. Type of this value is
            controlled by the value of the `return_object` argument of this
            method. """

        # Read and decode json
        r = requests.post('http://{}:{}'.format(self.address, self.port),
                          data=post_dictionary,
                          timeout=timeout)
        response = r.json()
        # Check if error occured
        if response['status'] == 'error':
            # Error occured, recreate error
            errors = [(name, cls) for name, cls in exceptions.__dict__.items()
                      if isinstance(cls, type)]
            if errors:
                for e in errors:
                    if e[0] == response['type']:
                        raise e[1]('[@Server] ' + response['message'])
                raise Exception("[{} @Server]: {} ".format(
                    errors[0], response['message']))
            else:
                raise Exception(("[Unknown error @Server]: An unknown error "
                                 "occured at the server"))
        elif response['status'] == 'ok':
            # No error occured: return results
            if return_object:
                results = io.unpickle(response['results'])
            else:
                results = response["results"]
            # Return data
            return results
        else:
            raise exceptions.ClientException(
                ("Response status '{}' was not "
                 "recognized.").format(response['status']))
