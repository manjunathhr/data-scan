#!/usr/bin/python2.7

import sys
import paramiko
import traceback

pIp = 0
puname = ""
pkey = ""
sip = 0
suname = ""
skey = ""


def getKeyVal(vName, vVal):
    if vVal and vVal != 0:
        return ''.join((vVal.strip()))
    else:
        print("Error, Reading Config file and  [%s] parameter is Empty" % (vName))
        sys.exit(1)


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
        sys.exit(43)



def initSSH(ssh):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    return ssh


def getPortalParams():
    global pIp
    global puname
    global pkey
    pIp = readConfPara("PORTAL_IP")
    puname = readConfPara("PORTAL_UNAME")
    pkey = readConfPara("PORTAL_KEY")


def getPrtSshConn():
    global pIp
    global puname
    global pkey
    ssh1 = ""
    ssh = ""
    try:
        ssh = initSSH(ssh1)
        getPortalParams()
        print("ip, uname, key :", pIp, puname, pkey )
        key = paramiko.RSAKey.from_private_key_file(pkey)
        ssh.connect(pIp, username=puname, pkey=key)
        print("DML Portal SSH connection Success")
        return ssh
    except Exception as e:
        print("Error : Unable to do DML Portal SSH connection !")
        print("*** Caught exception: %s: %s" % (e.__class__, e))
        traceback.print_exc()
        sys.exit(40)


def getSrvParams():
    global sip
    global suname
    global skey
    sip = readConfPara("DML_SERVER_IP")
    suname = readConfPara("DML_SERVER_UNAME")
    skey = readConfPara("DML_SERVER_KEY")


def getDmlSrvSshConn():
    ssh1 = ""
    ssh = ""
    try:
        ssh = initSSH(ssh1)
        getSrvParams()
        key = paramiko.RSAKey.from_private_key_file(skey)
        ssh.connect(sip, username=suname, pkey=key)
        print("DML Server SSH connection Success")
        return ssh
    except Exception as e:
        print("Error : Unable to do DML Server SSH connection !")
        print("*** Caught exception: %s: %s" % (e.__class__, e))
        traceback.print_exc()
        sys.exit(40)

