#!/usr/bin/python2.7

###############################################################################
#       MODULES INCLUDED
###############################################################################

import sys
import hashlib
import requests
import traceback
import datetime
import json
import time
import os
import io
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


WDIR = "/opt/dml/"
LIBPATH = WDIR + "lib/"
LOGPATH = "/var/log/dml/" 


###############################################################################
#   DATASTRUCTURE
###############################################################################

# Read the response by readchunkhttp
response = ""

# For Manifest
ssh = ""
mcheckSum = ""
scanLoc = ""
downLoc = ""

# Final file checksum
checksum1 = ""

# Logger handler
lgr = ""

# checkusum for chunks for each file
fchcksum = []

# To store all data_ids informations of all files of a manifest
dataIdDict = {}
key = 0

# To store name files and checksum from each Manifest
filesToUpload = {}

# To store scanned File details, fname, fcksum, fcksumlist
scantocopy = {}

# Config params
configDict = {}
SIZE = 1*1024*1024
SLEEP_TIME = 10

###############################################################################
#       FUNCTION DEFENITIONS
###############################################################################


def splitbychar(line):
    tidx = line.find(":")
    type = line[0:tidx]
    cdx = line.find(" ", tidx)
    chsum = line[tidx+1:cdx]
    fdx = line.find(" ", cdx)
    fname = line[fdx+2:len(line)-1]
    return type, chsum, fname


def errLog(strerr, func, e):
    lgr.error(strerr)
    strErr = "Error Caught An Exception in Function [ " + func + " ]"
    lgr.error(strErr)
    strErr = str(e.__class__) + str(e)
    lgr.error(strErr)
    strErr = traceback.print_exc()
    lgr.error(strErr)


def readManifest(fname):
    global filesToUpload
    filesToUpload.clear()
    idx = 0
    print("0.Before read request : ")
    resp = readRequest(fname)
    fd = io.StringIO(resp.text)
    try:
        for line in fd:
            if line[0:3] != "sha":
                continue
            item = {}
            item['hashtype'], item['checkSum'], item['file'] = splitbychar(line)
            filesToUpload[idx] = item
            # files to scan to be added
            idx += 1
        fd.close()
    except Exception as e:
        strErr = "2.Error In Reading manifest.txt File  [" + fname + "]"
        errLog(strErr, get_function_name(), e)
        delOnWorker(mcheckSum)
        sys.exit(4)


def readRequest(fileName):
    global configDict
    global response
    fname = configDict["PORT_URL"] + scanLoc + '/' + fileName
    print("Scan File path ", fname)
    response = requests.get(fname, stream=True, verify=False)
    print("Request Response Code : ", response.status_code, response)
    if response.status_code == 200:
        return response
    else:
        print("Error to Read File %s Error code %s" %(fileName, response))
        delOnWorker(mcheckSum)
        sys.exit(6)


def readChunkHttp(resp):
    global configDict
    global SIZE
    for data in resp.iter_content(SIZE):
        ar = datetime.datetime.now()
        if not data:
            break
        br = datetime.datetime.now()
        strInfo = "\n1.Time to Read Chunk Size of [ " + str((SIZE/(1024*1024))) + " ] MBs"
        strInfo += " Between DML Worker to Portal Serv in " + str((br-ar).seconds) + " seconds"
        lgr.info(strInfo)
        yield data


def downloadManifest(fname, chksum):
    global configDict
    global SIZE
    global downLoc
    url = configDict["PORT_URL"] + scanLoc + fname
    dhash = hashlib.sha256()
    r = requests.get(url, stream=True, verify=False)
    if response.status_code != 200:
        print("Error to Read File %s Error code %s" %(fileName, response))
        os.removedirs(downLoc)
        sys.exit(7)
    fpath = downLoc + fname
    dfchcksum = ""
    with open(fpath, 'wb') as fd:
        for chunk in r.iter_content(SIZE):
            a = datetime.datetime.now()
            dhash.update(chunk)
            dchecksum1 = dhash.hexdigest()
            if dchecksum1 == chksum:
                fd.write(chunk)
            else:
                strErr = "8.Error manifest.txt CheckSum Didn't Match [ " + str(dfchcksum)
                strErr += " ] Given Checksum [ " + chksum + " ]"
                errLog(strErr, get_function_name(), e)
                os.removedirs(downLoc)
                sys.exit(3)
            b = datetime.datetime.now()
            strInfo = "Time To Read manifest.txt file FROM DML PORTAL TO WORKER "
            strInfo += str((b-a).seconds) + "  seconds"
            lgr.info(strInfo)
    strInfo = "Copied manifest.txt File\n"
    lgr.info(strInfo)


def downLoadAllFiles():
    global configDict
    global scantocopy
    global SIZE
    dfchcksum = []
    strInfo = "\n\n\t II.Copying Files from PORTAL to WORKER Server "
    lgr.info(strInfo)
    for x, iList in scantocopy.iteritems():
        strInfo = "\n\tCopying File " + str(x+1) + ". [ " + iList[0] + " ]"
        lgr.info(strInfo)
        #url = configDict["PORT_URL"] + configDict["PORTAL_SCAN_LOCATION"] + "/" + iList[0]
        url = configDict["PORT_URL"] + scanLoc + iList[0]
        fchksum = iList[1]
        lchksum = iList[2]
        del dfchcksum[:]
        dhash = hashlib.sha256()
        r = requests.get(url, stream=True, verify=False)
        # Need validate r respoze
        i = 0
        #fpath = configDict["WORKER_DOWNLOAD_LOCATION"] + iList[0]
        fpath = downLoc + iList[0]
        strInfo = "ALL Chunk Checksum's : [ " + str(lchksum) + " ]"
        lgr.info(strInfo)
        with open(fpath, 'wb') as fd:
            for chunk in r.iter_content(SIZE):
                a = datetime.datetime.now()
                dhash.update(chunk)
                # Before write compare each chunk checksum
                ichksum = dhash.hexdigest()
                if ichksum in lchksum:
                    fd.write(chunk)
                    dfchcksum.append(ichksum)
                    b = datetime.datetime.now()
                else:
                    strErr = "10.Error Chunk Checksum didn't Matched with Previous"
                    lgr.error(get_function_name() + strErr)
                    strErr = "Copy Checksum : [ " + ichksum + " ]"
                    lgr.error(strErr)
                    strErr = "Scan Checksum : [ " + str(lchksum) + " ]"
                    lgr.error(strErr)
                    fd.close()
                    os.remove(fpath)
                    delOnWorker(mcheckSum)
                    return False

                strInfo = "Time To Read Each Chunk FROM DML PORTAL TO WORKER "
                strInfo += str((b-a).seconds) + "  seconds"
                lgr.info(strInfo)
                i = i+1
            dchecksum1 = dhash.hexdigest()
            # verify the checksum
            if dchecksum1 == fchksum:
                continue
            else:
                strErr = "11.Error For the File " + iList[0] + "the checksum didn't Match"
                lgr.critical(get_function_name() + strErr)
                strErr = "scanned Checksum :  " + iList[1]
                lgr.critical(strErr)
                strErr = "Copying Checksum : " + dchecksum1
                lgr.critical(strErr)
                sys.exit(3)
            strInfo = "Number of Chunks [" + str(i) + "]"
            lgr.info(strInfo)
            strInfo = "List of CheckSum in DML Worker [" + str(dfchcksum) + "]"
            lgr.info(strInfo)
    strInfo = "Successful DML Delivery"
    lgr.info(strInfo)


def addToDataIdDict(item):
    global dataIdDict
    global key
    dataIdDict[key] = item
    key += 1


def scanPrgrs(dataid, chkNum):
    global dataIdDict
    global SLEEP_TIME
    tup1 = tuple()
    # Waiting time for scan
    strInfo = "\nSleeping for " + str(SLEEP_TIME) + " Seconds data_id[ "
    strInfo += dataid + " ] Chunk Id : " + str(chkNum)
    lgr.info(strInfo)
    time.sleep(SLEEP_TIME)
    scan = True
    noTreats = False
    while scan:
        jobj = readDataId(dataid)
        # Need to validate jobj
        # print("data type of jobj : ", type(jobj))
        # print("ret jobj  : ", jobj)
        ret1, per = isScan100Per(jobj)
        if ret1 is True:
            tup1 = readObject(jobj)
            addToDataIdDict(str(tup1))
            # print( data_id, fname, fsize, verdict, total_time, scan_all_result, result, prgper)
            # print("tup1 = ", str(tup1))
            if int(tup1[3]) == 0 and tup1[5] == 'No Threat Detected' and tup1[6] == 'Allowed':
                noTreats = True
                # May not req
                # data_id.append(tup1[0])
                # call get ids
                scan = False
                break
            # 'Exceeded Archive File Number'
            # if int(tup1[1]) == 0 and tup1[3] == 'No Threat Detected' and tup1[4] == 'Allowed':
            # ('2a14ec3a40a34e77adfa5289ff39dccc', '0', 59456, 'Exceeded Archive File Number', 'Blocked', 100)
            else:
                noTreats = False
                strErr = "6.Error Number of Threats found : " + str(tup1[1])
                strErr += str(tup1[1]) + str(tup1[3]) + str(tup1[4])
                lgr.error(get_function_name() + strErr)
                break
        elif ret1 is False:
            strInfo = "Scan Needed More time, " + str(per) + " % is Compeleted"
            lgr.info(strInfo)
            time.sleep(SLEEP_TIME/2)
    return noTreats


def printAllDataIdResults():
    global dataIdDict
    # strInfo = "\ndata_id, verdict, total_time, scan_all_result, result, prgper"
    strInfo = "\ndata_id, fname, fsize, verdict, total_time, scan_all_result, result, prgper"
    lgr.info(strInfo)
    for key, val in dataIdDict.iteritems():
        strInfo = str(key) + "." + str(val)
        lgr.info(strInfo)


def sendChkToMCore(chunk, index, offset, fname):
    headers = {}
    headers['filename'] = fname
    headers['Content-Type'] = 'text/plain'
    try:
        headers['Content-length'] = str(len(chunk))
        headers['file-size'] = str(len(chunk))
        r = requests.post(configDict["SCAN_URL"], data=chunk, headers=headers)
        data = r.json()
    # Catch all Errors
    except Exception as e:
        strErr = "7.Error In Request Post from DML WORK to METADEFENDER CORE  [" + fname + "]"
        errLog(strErr, get_function_name(), e)
        sys.exit(0)
    finally:
        return data["data_id"]


def sendAllChunks(filePath, fileName):
    global fchcksum
    global checksum1
    global SIZE
    chunk = ""
    ret = False
    del fchcksum[:]
    try:
        hash = hashlib.sha256()
        index = 0
        offset = 0
        numCh = 0
        dId = sendChkToMCore(chunk, index, offset, fileName)
        print("1.Before read request : ")
        resp = readRequest(fileName)
        for chunk in readChunkHttp(resp):
            offset = index + len(str(chunk))
            index = offset
            hash.update(chunk)
            ar = datetime.datetime.now()
            # Sending to METADEFENDER CORE Server for a chunk Scanning
            dId = sendChkToMCore(chunk, index, offset, fileName)
            br = datetime.datetime.now()
            strInfo = "2.Time to Read Chunk of Size [ " + str(SIZE/(1024*1024)) + " ] MBs "
            strInfo += "Between The DML Worker and Metadefender Core Server in "
            strInfo += str((br-ar).seconds) + " Seconds"
            lgr.info(strInfo)
            # Read the data_id reponse
            numCh += 1
            notreats = scanPrgrs(dId, numCh)
            if notreats is True:
                fchcksum.append(hash.hexdigest())
                ret = True
            else:
                strCri = "\n\n 6.FILE GOT THREATS   [" + fileName + " ] \n\n"
                lgr.critical(get_function_name() + strCri)
                delOnWorker(mcheckSum)
                ret = False
                break
        checksum1 = hash.hexdigest()
        strInfo = "Full Checksum : " + str(checksum1)
        lgr.info(strInfo)
        strInfo = "\nTOTAL Number of Chunks in The File [ " + fileName + " ] is ["
        strInfo += str(numCh) + "]"
        lgr.info(strInfo)
        strInfo = "List of CheckSum in MCore Server [" + str(fchcksum) + "]"
        lgr.info(strInfo)
    except Exception as e:
        strErr = "7.Error In Reading Chunks from DML HTTPS PORTAL [" + str(fileName) + "]"
        errLog(strErr, get_function_name(), e)
        ret = False
        checksum1 = ""
        sys.exit(7)
    finally:
        return ret, str(checksum1)


def readDataId(dataId):
    dname = ""
    try:
        dname = configDict["SCAN_URL"] + '/' + dataId
        r = requests.get(dname)
        # Validate Response
        # strInfo = str(r)
        # lgr.info(strInfo)
        data = r.json()
        dataJson = json.dumps(data, indent=2, sort_keys=True)
    except Exception as e:
        strErr = "10.Error In HTTP Requests Get  dname : " + dname
        errLog(strErr, get_function_name(), e)
    finally:
        return dataJson


def scanFiles(dpath):
    global lgr
    global filesToUpload
    global downLoc
    ind = 0
    ret = ""
    readManifest("manifest.txt")
    # Looping through all Files in a Manifest
    for x in filesToUpload:
        onefile = filesToUpload[x]
        fname = onefile['file']
        ckSum = str(onefile['checkSum'])
        ta = datetime.datetime.now()
        fpath = dpath + str(onefile['file'])
        strInfo = "\nScanning the File  [ " + str(x) + "." + fname + " ]"
        lgr.info(strInfo)
        ret, checksum1 = sendAllChunks(fpath, fname)
        if ret is True:
            tb = datetime.datetime.now()
            strInfo = "\nTotal Time in seconds " + str(((tb-ta).seconds))
            strInfo += " or In minutes [ " + str(((tb-ta).seconds/60))
            strInfo += " ] for the file [ " + onefile['file'] + " ]"
            lgr.info(strInfo)
            if checksum1 == ckSum:
                strInfo = "\nCheckSum Matched with Original, File will be Added to be Copy"
                lgr.info(strInfo)
                # strInfo = "Manifest CheckSum [" + ckSum + "]"
                # lgr.info(strInfo)
                # strInfo = "New CheckSum Calculted [" + checksum1 + "]"
                # lgr.info(strInfo)
                tmp = list(fchcksum)
                scantocopy[ind] = [fname, checksum1, tmp]
                ind += 1
                del fchcksum[:]
            else:
                strErr = "9.Error CheckSum Doesn't Match with Original [ "
                strErr += ckSum + "] New [" + checksum1
                lgr.error(get_function_name() + strErr)
        	delOnWorker(mcheckSum)
    return ret


def scanCopyManifest(mpath, mcheckSum):
    fpath = mpath + "manifest.txt"
    ret, newChecksum = sendAllChunks(fpath, "manifest.txt")
    if ret is False:
        lgr.critical("4.Error Scan Failed Found Threats in manifest.txt")
        sys.exit(2)
    if (mcheckSum != newChecksum):
        lgr.critical("5.*** manifest.txt CheckSum didn't Match ***")
        lgr.info("Checksum : " + str(mcheckSum) + " New CheckSum : " + str(newChecksum))
        sys.exit(2)
    else:
        downloadManifest("manifest.txt", mcheckSum)
        lgr.info("verified manifest.txt File Successfully")
        return ret


def delOnWorker(dname):
    # Delete on worker, local directory
    try:
        os.chdir("/var/www/scanned/")
        strInfo = "Deleting Dir : " + dname
        lgr.info(strInfo)
        shutil.rmtree(dname)
        return True
    except OSError as e:
        strErr = "Error: in file : " + e.filename + " error code : " + e.strerror
        lgr.error(strErr)
        return False


##############################################################################
#
# Read the Conf file
#
##############################################################################
def assignValues(line):
    vName, vVal = line.split('=')
    if vVal and vVal.split() != 0:
        key = ''.join(vName.strip())
        configDict[key] = ''.join(vVal.strip())
    else:
        strErr = "Error Reading config.conf file [ " + key + "] parameter is Empty"
        lgr.error(strErr)
        sys.exit(1)


def readConf():
    global configDict
    global SIZE
    global SLEEP_TIME
    fname = "/opt/dml/etc/config.conf"
    configDict.clear()
    with open(fname) as fd:
        for line in fd:
            line = line.strip()
            if line.strip() == '' or line[0] == '\n' or line[0] == '\t':
                continue
            if line[0] == '#':
                continue
            assignValues(line)
    size = configDict["SIZE"]
    SIZE = int(size) * SIZE
    SLEEP_TIME = int(configDict["SCAN_WAIT_TIME"])

###############################################################################
#           MAIN FUNCTION
###############################################################################
if __name__ == '__main__':
    
    sys.path.append(LIBPATH)
    from readOpsJson import *
    from dmlLogger import *
    from getOpt import *

    method, mcheckSum = checkArgs(sys.argv[1:])
    lname = LOGPATH + "/" + mcheckSum + ".log"
    initLogger(lname)
    lgr = logging.getLogger('dml_wkr')
    scantocopy.clear()
    dataIdDict.clear()
    # Main Starts
    readConf()
    strInfo = "\n\tI.Scan the Files For Virus in Metadefender Core Server"
    lgr.info(strInfo)
    scanLoc = str(configDict["PORTAL_SCAN_LOCATION"]) + mcheckSum + '/'
    downLoc = str(configDict["WORKER_DOWNLOAD_LOCATION"]) + mcheckSum + '/'
    os.mkdir(downLoc)
    os.chmod(downLoc, 0767)
    mret = scanCopyManifest(scanLoc, mcheckSum)
    if mret is True:
        iret = scanFiles(scanLoc)
        if iret is True:
            downLoadAllFiles()
            printAllDataIdResults()
        else:
            lgr.critical("12.Error Scan Files Failed Found Threats")
            os.removedirs(downLoc)
            sys.exit(1)
    else:
        lgr.critical("13.Error manifest scan Failed Found Threats")
        sys.exit(1)
    # Successful Exit
    sys.exit(0)

