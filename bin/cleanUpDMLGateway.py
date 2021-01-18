#!/usr/bin/python2.7

###############################################################################
#   SYSTEM MODULES INCLUDED
###############################################################################

import os
import sys
import shutil

###############################################################################
#   DATASTRUCTRE
###############################################################################

WORKER_ROOT_PATH = "/var/www/dml/"
PORTAL_ROOT_PATH = "/var/www/dml/datadirs/"
WDIR = "/opt/dml/"
LOGPATH = "/var/log/dml/"
LIBPATH = WDIR + 'lib/'

ssh = ""

###############################################################################
#           MAIN FUNCTION
###############################################################################


if __name__ == '__main__':
    
    sys.path.append(LIBPATH)
    from getOpt import *
    from sshconn import *

    shamethod, dname = checkArgs(sys.argv[1:])
    ssh = getPrtSshConn()

    # Delete on worker, local directory
    try:
        os.chdir(WORKER_ROOT_PATH)
        shutil.rmtree(dname)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

    # Delete on Portal, over ssh
    npath = PORTAL_ROOT_PATH + dname + "/"
    cmd = "rm -rf " + npath
    print(cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)

    if stdout.channel.recv_exit_status() == 1:
        strErr = stderr.read()
        print(strErr)
        ret = False
    if stdout.channel.recv_exit_status() == 0:
        cmdOutputList = stdout.readlines()
        print(cmdOutputList)
        ret = True
    ssh.close()
    
    if ret is True:
        print("Cleanup Gateway SuccessFully From DML Worker")
        sys.exit(0)
    else:
        sys.exit(1)
