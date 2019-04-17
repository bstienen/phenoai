"""
Example 07: Output to screen and file
=====================================
Text output of PhenoAI to screen and file is managed by the logger module. The
functions in het module that manage the output are called internally by PhenoAI
and are not intended to be called by the user. Other functions however configure
the handling of the output and *are* specifically meant to be used by the user.

This example showcases the possibilities.
"""

# Import the logger module 

from phenoai import logger

# Send the output to the screen
# lvl indicates the minimum level output should have to be printed. The higher the
# level, the higher its importance. Conventions follow those of the native logging
# module of python:
#   10    DEBUG
#   20    INFO
#   30    WARNING
#   40    ERROR
#   50    CRITICAL
# The setting below indicates that all messages with an importance of INFO or
# higher will be printed

logger.to_stream(lvl=20)

# Send output to file. The level of this output channel may differ from the lvl
# for the stream channel. Only a single filechannel can exist at a time.

logger.to_file("loggertest.out", lvl=0)

# Output a couple of messages

logger.debug("debug message")
logger.info("yo")
logger.warning("warning message")
logger.error("this is an error")
logger.critical("HELP!")

# Colour the output messages for the stream channel. The file channel is
# unaffected by this setting.
# This setting could also be put into the to_stream function via
#     logger.to_stream(lvl=20, colour=True)

logger.colour_stream(True)

# Again print some messages

logger.debug("debug message")
logger.info("yo")
logger.warning("warning message")
logger.error("this is an error")
logger.critical("HELP!")

# Mute all output.

logger.mute()

# Again print some messages, that won't be visible now without defined channels

logger.debug("debug message")
logger.info("yo")
logger.warning("warning message")
logger.error("this is an error")
logger.critical("HELP!")

# Unmute all output and redefine stream level to only show critical errors

logger.unmute()
logger.to_stream(lvl=50)

# Again print some messages, that won't be visible now without defined channels

logger.debug("debug message")
logger.info("yo")
logger.warning("warning message")
logger.error("this is an error")
logger.critical("HELP!")