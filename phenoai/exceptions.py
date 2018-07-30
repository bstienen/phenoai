""" This module implements all custom exceptions that can be raised by the PhenoAI package. """

class FileIOException(Exception):
	""" Exception class of which instances can be raised by functions in the io module. """
	pass
class ConfigurationException(Exception):
	""" Exception class of which instances can be raised by classes.Configuration derived classes. """
	pass
class AInalysisException(Exception):
	""" Exception class of which instances can be raised by the ainalyses.AInalysis class. """
	pass
class PhenoAIException(Exception):
	""" Exception class of which instances can be raised by the phenoai.phenoai class. """
	pass
class ResultsException(Exception):
	""" Exceptions class of which instances can be raised by the phenoai.PhenoAIResults and ainalyses.AInalysisResults classes. """
	pass
class ServerException(Exception):
	""" Exception class of which instances can be raised by the phenoai.phenoaiServer class. """
	pass
class ClientException(Exception):
	""" Exception class of which instances can be raised by the client module. """
	pass
class MakerError(Exception):
	""" Exception class of which instances can be raised by the maker module. """