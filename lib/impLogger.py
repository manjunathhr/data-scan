#!/usr/bin/python2.7

# import os
import logging
import traceback

###########################################################
#### LOG FILE INIT
###########################################################


def get_function_name():
    return traceback.extract_stack(None, 2)[0][2]


def initLogger(lfname):
    # home=os.environ['QA_CLI_TEST_HOME']
    # logfilename = 'test.log'

    lg = logging.getLogger('imp_dml')
    lg.setLevel(logging.DEBUG)

    # add a file handler
    fhd = logging.FileHandler('{lfname}'.format(**locals()))
    # create a formatter and set the formatter for the handler.
    frmt = logging.Formatter("[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
            "%d-%m-y% %H:%M:%S")
    fhd.setFormatter(frmt)
    # add the Handler to the lg
    lg.addHandler(fhd)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # ch.setFormatter(frmt)
    # add ch to logger
    lg.addHandler(ch)

