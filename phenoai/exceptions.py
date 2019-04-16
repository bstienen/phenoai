""" This module implements all custom exceptions that can be raised by the
PhenoAI package. """


class FileIOException(Exception):
    """ Exception class of which instances can be raised by functions in the
    :mod:`phenoai.io` module. """
    pass


class ConfigurationException(Exception):
    """ Exception class of which instances can be raised by
    :class:`phenoai.containers.Configuration` derived classes. """
    pass


class AInalysisException(Exception):
    """ Exception class of which instances can be raised by the
    :class:`phenoai.ainalyses.AInalysis` class. """
    pass


class PhenoAIException(Exception):
    """ Exception class of which instances can be raised by the
    :class:`phenoai.core.PhenoAI` class. """
    pass


class ResultsException(Exception):
    """ Exceptions class of which instances can be raised by the
    :class:`phenoai.containers.PhenoAIResults` and
    :class:`phenoai.containers.AInalysisResults` classes. """
    pass


class ServerException(Exception):
    """ Exception class of which instances can be raised by the
    :class:`phenoai.core.PhenoAI` class when running as a server. """
    pass


class ClientException(Exception):
    """ Exception class of which instances can be raised by the
    :mod:`phenoai.client` module. """
    pass


class MakerError(Exception):
    """ Exception class of which instances can be raised by the
    :mod:`phenoai.maker` module. """
