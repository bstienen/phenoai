""" A simple interface to quickly set up and use a Logger instance from the logging module.

This module implements methods to quickly set up a Logger instance with multiple different logging channels. Currently implemented are a stream logger and a file logger.

	import logger
	logger.init(do_stream=True, logpath="output.log")"""

import logging
from logging import Filter
#from logging.handlers import SMTPHandler

__loggername__ = "bsmai_logger"
__streamchannel__ = None
__filechannel__ = None
__streamchannel_defaultlvl__ = logging.INFO
__filechannel_defaultlvl__ = logging.INFO

__colouredstream__ = True
__indentlevel__ = 0
__indentunit__ = "  "


class ColourFilter(Filter):
	""" Adds colour to the output of the stream logging channel if the COLOUR_OUTPUT configuration variable is set to True. """
	def filter(self, record):
		if bool(__colouredstream__):
			if record.levelno == logging.DEBUG:
				record.levellabel = " \033[94mDEBUG\033[0m  "
				record.filteredmessage = record.msg
			elif record.levelno == logging.INFO:
				record.levellabel = "  INFO  "
				record.filteredmessage = record.msg
			elif record.levelno == logging.WARNING:
				record.levellabel = "\033[93mWARNING\033[0m "
				record.filteredmessage = record.msg
			elif record.levelno == logging.ERROR:
				record.levellabel = " \033[91mERROR\033[0m  "
				record.filteredmessage = record.msg
			elif record.levelno == logging.CRITICAL:
				record.levellabel = "\033[1m\033[91mCRITICAL\033[0m\033[0m"
				record.filteredmessage = "\033[91m{}\033[0m".format(record.msg)
		else:
			record.levellabel = "{:^8}".format(record.levelname)
			record.filteredmessage = record.msg
		return record
class IndentFilter(Filter):
	""" Adds indent to the message output of the logging channel. """
	def filter(self, record):
		# Add indenting
		record.msg = "{}{}".format(__indentunit__*__indentlevel__, record.msg)
		return record

def to_stream(lvl=None, colour=True):
	""" Initializes a stream log to the terminal or console
	
	Parameters
	----------
	lvl : integer (default: None)
		Minimum level of the messages to be shown by stream. Uses level integers as defined in the logging package. Will be ignored if do_stream is False. If None, default level will be used as defined in DEFAULT_STREAM_LOGGING_LEVEL in this module.
	colour: boolean (default: True)
		Boolean indicating if stream should use colouring. """
	global __streamchannel__
	add = (__streamchannel__ == None)
	logger = logging.getLogger(__loggername__)
	logger.setLevel(logging.DEBUG)
	if add:
		__streamchannel__ = logging.StreamHandler()
		__streamchannel__.addFilter(IndentFilter())
		__streamchannel__.addFilter(ColourFilter())
	if lvl == None:
		__streamchannel__.setLevel(__streamchannel_defaultlvl__)
	else:
		__streamchannel__.setLevel(lvl)
	if add:
		formatter = logging.Formatter("{asctime:<23} | {levellabel} | {filteredmessage}", style="{")
		__streamchannel__.setFormatter(formatter)
		logger.addHandler(__streamchannel__)

def to_file(logpath, lvl=None):
	""" Initializes a log channel to a file

	Parameters
	----------
	logpath : string
		Location where to log to. File will be created if not already existing.
	lvl : integer (default: None)
		Minimum level of the messages to be stored in the logfile set by logpath. Uses level integers as defined in the logging package. Will be ignored if logpath is None. If not ignored and None, default level will be used as defined in DEFAULT_FILE_LOGGING_LEVEL in this module.
	"""
	global __filechannel__
	add = (__filechannel__ == None)
	logger = logging.getLogger(__loggername__)
	if add:
		__filechannel__ = logging.FileHandler(logpath)
		__filechannel__.addFilter(IndentFilter())
	if lvl == None:
		__filechannel__.setLevel(__filechannel_defaultlvl__)
	else:
		__filechannel__.setLevel(lvl)
	if add:
		formatter = logging.Formatter("{asctime:<23} | {levelname:^8} | {message}", style="{")
		__filechannel__.setFormatter(formatter)
		logger.addHandler(__filechannel__)

def remove_file_channel():
	""" Removes file logging channel from list of logging channels (if one was defined) """
	global __filechannel__
	if not isinstance(__filechannel__, type(None)):
		logger = logging.getLogger(__loggername__)
		logger.removeHandler(__filechannel__)
		__filechannel__ = None

def remove_stream_channel():
	""" Removes stream channel from list of logging channels (if one was defined) """
	global __streamchannel__
	if not isinstance(__streamchannel__, type(None)):
		logger = logging.getLogger(__loggername__)
		logger.removeHandler(__streamchannel__)
		__streamchannel__ = None

def mute(lvl=logging.CRITICAL):
	""" Mutes the output of all logging channels (even those that have nothing to do with PhenoAI) below a specified level.

	Parameters
	----------
	lvl : integer (default: logging.CRITICAL)
		Logging level below which all messages will be muted
	"""
	logging.disable(lvl)
def unmute():
	""" Unmutes the logging module as done through the mute function in this module. """
	logging.disable(logging.NOTSET)
def set_indent(lvl):
	""" Changes the indenting level of the output

	Parameters
	----------
	lvl: integer or string
		Indent level. Can be integer (indicating absolute integer level) or "+" or "-", indicating a relative increase or decrease of indent level with 1. """
	global __indentlevel__
	if isinstance(lvl, int):
		__indentlevel__ = lvl
	elif isinstance(lvl, str):
		if lvl == "+":
			__indentlevel__ += 1
		elif lvl == "-":
			__indentlevel__ -= 1
		else:
			raise Exception("Indent level not recognized")
	elif not isinstance(lvl, type(None)):
		raise Exception("Indent level not recognized")
def colour_stream(colour=True):
	""" Let stream logger use coloured output

	Parameters
	----------
	colour: boolean (default=True)
		Boolean indicating if stream logging should be coloured. """
	global __colouredstream__
	__colouredstream__ = bool(colour)

def debug(message, indent=None):
	""" Send a message to the logger channels with level label logging.DEBUG """
	set_indent(indent)
	logging.getLogger(__loggername__).debug(message)
def info(message, indent=None):
	""" Send a message to the logger channels with level label logging.INFO """
	set_indent(indent)
	logging.getLogger(__loggername__).info(message)
def warning(message, indent=None):
	""" Send a message to the logger channels with level label logging.WARNING """
	set_indent(indent)
	logging.getLogger(__loggername__).warning(message)
def error(message, indent=None):
	""" Send a message to the logger channels with level label logging.ERROR """
	set_indent(indent)
	logging.getLogger(__loggername__).error(message)
def critical(exception, indent=None):
	""" Send a message to the logger channels with level label logging.CRITICAL """
	set_indent(indent)
	logging.getLogger(__loggername__).critical(exception)

if __streamchannel__ == None:
	to_stream()
