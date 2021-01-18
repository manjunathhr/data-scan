#!/usr/bin/python2.7

import sys

PORTAL_PATH = "/var/www/dml/datadirs/"
shamethod = ""
ssh = ""
WDIR = "/opt/dml/"
LIBPATH = WDIR + 'lib/'
LOGPATH = "/var/log/dml/"


def createDir(dname):
    global PORTAL_PATH
    global ssh
    
    ret = ""
    npath = PORTAL_PATH + dname + "/"
    ssh = getPrtSshConn()
    sftp = ssh.open_sftp()
    try:
        print("path : ", npath)
        ret = sftp.mkdir(npath)
        #dmluser uid is 1001
        #apache group id 48
        sftp.chown(npath, 1001, 48)
        sftp.chmod(npath, 0754)
    except IOError:
        print("Error, Cannot Create dir [%s], Errorcode [%s]" % (dname, ret))
        sys.exit(3)
    sftp.close()
    ssh.close()
    return True


###############################################################################
#           MAIN FUNCTION
###############################################################################
if __name__ == '__main__':
   
    sys.path.append(LIBPATH)
    from getOpt import *
    from sshconn import *
    
    shamethod, dname = checkArgs(sys.argv[1:])
    ret = createDir(dname)
    if ret is True:
        print("Directory Created SuccessFully From DML Worker")
        sys.exit(0)
    else:
        sys.exit(1)
