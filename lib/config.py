#!/usr/bin/python2.7

import sys

def getKeyVal(vName, vVal):
    if vVal and vVal != 0:
        return ''.join((vVal.strip()))
    else:
        print("Error, Reading Config file and  [%s] parameter is Empty" % (vName))
        sys.exit(41)


def readConfPara(key):
    fname = "/opt/dml/etc/config.conf"
    keyFound = False
    with open(fname) as fd:
        for line in fd:
            line = line.strip()
            if line.strip() == '' or line[0] == '\n' or line[0] == '\t':
                continue
            elif line[0] == '#':
                continue
            else:
                vName, vVal = line.split('=')
                lkey = ''.join((vName.split()))
                if lkey == key:
                    val = getKeyVal(vName, vVal)
                    keyFound = True
                    return val
                else:
                    continue
    if keyFound is False:
        print("Error Could not Find [%s]" % key)
        sys.exit(40)

