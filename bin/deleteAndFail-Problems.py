#!/usr/bin/python2.7

###############################################################################
#   SYSTEM MODULES INCLUDED
###############################################################################

import os
import sys
import shutil

WPATH = "/var/www/dml/"
PPATH = "/var/www/dml/datadirs/"
WDIR = "/opt/dml/"
LOGPATH = "/var/log/dml/"
LIBPATH = WDIR + 'lib/'

###############################################################################
#    DATASTRUCTURE
###############################################################################

ssh = ""
lgr = ""

###############################################################################
#    FUNCTIONS
###############################################################################


def delOnWorker(dname):
    global WPATH
    ## Delete on worker, local directory
    try:
        os.chdir(WPATH)
        strInfo = "Deleting Dir : " + dname
        lgr.info(strInfo)
        shutil.rmtree(dname)
    except OSError as e:
        strErr =  "Error: in file : " + e.filename + " error code : " + e.strerror
        lgr.error(strErr)
        #return False
    return True

def delOnPortal(dname):
    global ssh
    global PPATH
    ssh = getPrtSshConn()
    ## Delete on Portal, over ssh
    npath = PPATH + dname + "/"
    cmd = "rm -rf " + npath
    
    strinfo = "PATH : " + npath
    lgr.info(strinfo)
 
    print(cmd)
    strInfo = "Executing : " + cmd
    lgr.info(strInfo)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    if stdout.channel.recv_exit_status() == 1:
        strErr = stderr.read()
        lgr.error(strErr)
        return False
    if stdout.channel.recv_exit_status() == 0:
        strInfo = stdout.readlines()
        lgr.info(strInfo)
        return True
    ssh.close()


def delboth(dname):
    pret = delOnPortal(dname)
    wret = delOnWorker(dname)
    #if pret and wret is True:
    #    return True
    #else:
    #    return False
    return True

###############################################################################
#           MAIN FUNCTION
###############################################################################



if __name__ == '__main__':
    sys.path.append(LIBPATH)
    from getOpt import *
    from sshconn import *
    from toLogger import *
   
    shamethod, dname = checkArgs(sys.argv[1:])
    lgrname = LOGPATH + "/DeleteandFailPrb.log"
    initLogger(lgrname)
    lgr = logging.getLogger('del_to')
    ret = delboth(dname)
    if ret is True:
        print("DeleteAndFail-Problems SuccessFully From DML Worker")
        sys.exit(0)
    else:
        sys.exit(1)
