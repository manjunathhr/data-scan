#!/usr/bin/python2.7

import sys
import getopt


def usage():
    print 'script_name.py -p <mpath> -c <mchecksum>'
    sys.exit()


def checkArgs(argv):
    method = ''
    mchecksum = ''
    try:
        opts, args = getopt.getopt(argv, "hm:c:", ["method=", "mchecksum="])
        if len(opts) != 2:
            print("count ", len(opts))
            usage()
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-m", "--manifest method"):
            method = arg
        elif opt in ("-c", "--manifest checksum"):
            mchecksum = arg
    if method.strip() == '' or mchecksum.strip() == '':
        usage()
    return method, mchecksum

