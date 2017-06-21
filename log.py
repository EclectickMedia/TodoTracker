import logging
import logging.handlers as handlers

import sys  # for grabbing the program directory
import os  # for splitting sys.argv
PROGRAM_PATH = os.path.split(sys.argv[0])[0]
LOG_PATH = os.path.join(PROGRAM_PATH, 'logs', 'searcher.log')

# BEGIN Logger setup
file_formatter = logging.Formatter(
    '%(asctime)s:'
    '%(filename)-24s:'
    '%(name)-24s:'
    '%(levelname)-10s:'
    '%(funcName)-24s:'
    '%(lineno)-4d:'
    '%(message)s'
)

stream_formatter = logging.Formatter(
    '%(levelname)-10s:'
    '%(name)-20s:'
    '%(message)s'
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.INFO)

searcher_handler = handlers.RotatingFileHandler(LOG_PATH,
                                                maxBytes=500000, backupCount=5)
searcher_handler.setFormatter(file_formatter)
searcher_handler.setLevel(logging.DEBUG)

# builder_handler = handlers.RotatingFileHandler('logs/builder.log',
#                                                maxBytes=500000, backupCount=1)
# builder_handler.setFormatter(file_formatter)
# builder_handler.setLevel(logging.DEBUG)

# tests_handler = handlers.RotatingFileHandler('logs/tests.log',
#                                              maxBytes=500000, backupCount=1)
# tests_handler.setFormatter(file_formatter)
# tests_handler.setLevel(logging.DEBUG)


logger = logging.getLogger('base')
logger.setLevel(logging.DEBUG)
logger.addHandler(searcher_handler)
logger.addHandler(stream_handler)

# builder_logger = logging.getLogger('base.builder')
# builder_logger.addHandler(builder_handler)

# test_logger = logging.getLogger('base.tests')
# test_logger.addHandler(tests_handler)
