# Copyright (c) 2021, Technische UniversitÃ¤t Kaiserslautern (TUK) & National University of Sciences and Technology (NUST).
# All rights reserved.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os,sys
import json

import logging
import logging.config
from pathlib import Path
from logging.handlers import RotatingFileHandler
#from concurrent_log_handler import ConcurrentRotatingFileHandler  #pip install concurrent-log-handler


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

# upgrade to:    "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",

#0v3# JC  Jan 15, 2023  Possible utf-8 needed for hebrew etc.
#0v2# JC  Sep  5, 2023  custom dev logger
#0v1# JC  Sep  2, 2023  Init


class UnicodeSafeRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding='utf-8',delay=False):
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)

    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            if self.encoding != 'utf-8':
                self.setFormatter(logging.Formatter(self.formatter._fmt, datefmt=self.formatter.datefmt, style=self.formatter.default_format_style))
                self.stream = self._open()
                self.encoding = 'utf-8'
                super().emit(record)
            else:
                # If utf-8 encoding still fails, replace or ignore problematic characters
                record.msg = record.msg.encode('utf-8', errors='replace').decode('utf-8')
                super().emit(record)

class CustomLogger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET, dev_logger=None):
        super(CustomLogger, self).__init__(name, level)
        self.dev_logger = dev_logger

    def dev(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self.dev_logger._log(logging.INFO, msg, args, **kwargs)

#ORG#        "datetime": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
#EXTRA        "datetime": { "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "datefmt": "%b %d, %Y %H:%M:%S" }

config="""
{
    "version": 1, 
    "disable_existing_loggers": false, 
    "formatters": {
        "simple": {"format": "%(message)s"}, 
        "datetime": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    }, 
    "handlers": {
        "console": {
            "class": "logging.StreamHandler", 
            "level": "DEBUG", 
            "formatter": "simple", 
            "stream": "ext://sys.stdout"
            }, 
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler", 
            "level": "INFO", 
            "formatter": "datetime", 
            "filename": "info.log", 
            "maxBytes": 100485760, 
            "backupCount": 20, "encoding": "utf8"
        }
    }, 
    "root": {
        "level": "INFO", 
        "handlers": [
            "console", 
            "info_file_handler"
        ]
    }
}

"""
logger_config=json.loads(config)


def setup_logging(save_dir='', log_config='logger/logger_config.json', default_level=logging.INFO, suppress_stdout=False):
    global logger_config

    # Register the custom logger class
    logging.setLoggerClass(CustomLogger)

    if not save_dir:
        save_dir = Path(LOCAL_PATH + "w_datasets/logs")

    log_config = Path(log_config)

    if logger_config:
        config = logger_config
        # Modify logging paths based on run config
        for _, handler in config['handlers'].items():
            if 'filename' in handler:
                handler['filename'] = str(save_dir / handler['filename'])

        logging.config.dictConfig(config)

    elif log_config.is_file():
        # Ensure you have this utility function to read the JSON
        from utils import read_json
        config = read_json(log_config)
        # Modify logging paths based on run config
        for _, handler in config['handlers'].items():
            if 'filename' in handler:
                handler['filename'] = str(save_dir / handler['filename'])

        logging.config.dictConfig(config)

    else:
        print("Warning: logging configuration file is not found in {}.".format(log_config))
        logging.basicConfig(level=default_level)

    # Setup dev logger (specifically for the dev method)
    dev_logger = logging.getLogger('dev')
    dev_logger.propagate = False  # To prevent double logging

    ## Add unicode safe to catch errors
    dev_handler = UnicodeSafeRotatingFileHandler(filename=str(save_dir / "dev.log"), maxBytes=100485760, backupCount=20, encoding="utf8")
#Dec 2023    dev_handler = RotatingFileHandler(filename=str(save_dir / "dev.log"), maxBytes=100485760, backupCount=20, encoding="utf8")

#    dev_handler = ConcurrentRotatingFileHandler(filename=str(save_dir / "dev.log"), maxBytes=10485760, backupCount=20, encoding="utf8")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s')

    dev_handler.setFormatter(formatter)
    dev_logger.addHandler(dev_handler)
    dev_logger.setLevel(logging.INFO)

    # Instantiate the 'dev' logger
    dev_logger = logging.getLogger('dev')

    # Retrieve main logger (with enhanced capabilities)
    main_logger = logging.getLogger('main')
    

    if suppress_stdout:
        #** for threaded
        ###############3  suppress outputs
        # Disable propagation to avoid logs being handled by the root logger
        main_logger.propagate = False

        # Remove all handlers that might output to console
        for handler in main_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                main_logger.removeHandler(handler)
        ###############3

            
    main_logger.dev_logger = dev_logger

    return main_logger
