#!/usr/bin/python2.7

import sys
import io
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mfiles = []
lgr = ""
mchkdir = ""

WDIR = "/opt/dml/"
LOGPATH = "/var/log/dml/"
LIBPATH = WDIR + 'lib/'


def splitbychar(line):
    tidx = line.find(":")
    type = line[0:tidx]
    cdx = line.find(" ", tidx)
    chsum = line[tidx+1:cdx]
    fdx = line.find(" ", cdx)
    fname = line[fdx+1:len(line)-1]
    return str(fname).strip()

def readManifest(dpath):
    fname = dpath + '/' + "manifest.txt"
    resp = requestGetRet(fname)
    fd = io.StringIO(resp.text)
    for line in fd:
        if line[0:6] != "sha256":
            strErr = "Invalid checkSum type " + line[0:6]
            strErr += " Currently is not supporting"
            lgr.error(strErr)
            sys.exit(3)
        name = splitbychar(line)
        mfiles.append(name)
    fd.close()
    mfiles.append("manifest.txt")


def readDir(fpath):
    for file in mfiles:
        npath = fpath + '/' + file
        strinfo = "File : " + file  +  "Size : " 
        res = requestGet(npath)
        if res is not False:
            strinfo += res.headers['Content-Length']
	    lgr.info(strinfo)
        else:
            return False
    return True


def requestGet(fname):
    res = ""
    #lgr.info(strinfo)
    try:
        res = requests.get(fname, stream=True, verify=False)
        if res.status_code == 200:
            return res
        else:
            strErr = "4. Error to Read File " + fname + " Error code " + res
            lgr.error(strErr)
            sys.exit(2)
    except Exception as e:
        if res.status_code == 404:
            strInfo = "1.File Not Found : " + fname + " Error code " + str(res) 
            lgr.info(strInfo)
            return False
        if res.status_code == 403:
            strInfo = "2.You don't have permission to access to Read File :" + fname + " Error code " + str(res) 
            lgr.info(strInfo)
            sys.exit(3)
        else:
            strErr = "3.Error Request Get Unable to Connect PORTAL URL [" + fname + "]"
            print(res)
            lgr.error(strErr)
            sys.exit(2)


def requestGetRet(fname):
    #print("Scan File path ", fname)
    res = requests.get(fname, stream=True, verify=False)
    if res.status_code == 200:
        return res
    if res.status_code == 404:
        strErr = "3.File Not Found : " + fname + " Error code " + str(res)
        lgr.error(strErr) 
        sys.exit(100)
    if res.status_code == 403:
        strInfo = "2.You don't have permission to access to Read File :" + fname + " Error code " + str(res) 
        lgr.info(strInfo)
        sys.exit(3)
    else:
        strErr = "1.ERROR UNABLE To Read File " + fname + " Error code " + str(res)
        return res


###############################################################################
#           MAIN FUNCTION
###############################################################################
if __name__ == '__main__':
    sys.path.append(LIBPATH)
    from getOpt import *
    from dmlLogger import *
    from config import *

    purl = readConfPara("PORT_URL") + "datadirs/"
    shamethod, mchkdir = checkArgs(sys.argv[1:])
    lgrname = LOGPATH + "/" + mchkdir + ".log"
    initLogger(lgrname)
    lgr = logging.getLogger('dml_wkr')
    
    fpath = purl + mchkdir
    readManifest(fpath)
    lgr.info(mfiles)
    ret = readDir(fpath)
    if ret is True:
        # Success Full Exit
        strInfo = "\n\nChecked SuccessFully in Manifest"
        lgr.info(strInfo)
        sys.exit(0)
    else:
        #This Exit with 100, to Loop again as files are still uploading
        strInfo = "\n\nStill Files to Upload Continue to check"
        lgr.info(strInfo)
        sys.exit(100)
