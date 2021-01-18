#!/usr/bin/python2.7 

import json


def getVerdict(obj):
    for key, val in obj.iteritems():
        if key == "verdict":
            return str(val)


def getProcessResults(obj):
    for key, val in obj.iteritems():
        if key == "progress_percentage":
            prgper = int(val)
        elif key == "result":
            res = str(val)
        else:
            continue
    return res, prgper


def getFileinfo(obj):
    for key, val in obj.iteritems():
        #print("key %s : Val : [%s]" % (key, val))
        if key == "display_name":
            fname = str(val)
        elif key == "file_size":
            fsize = int(val)
        else:
            continue
    return fname, fsize


def getScanResults(obj):
    for key, val in obj.iteritems():
        if key == "total_time":
            tottim = int(val)
        elif key == "scan_all_result_a":
            scanres = str(val)
        else:
            continue
    return tottim, scanres


def isScan100Per(data):
    # my_json_data var contains a dictionory object
    
    if type(data) != dict:
	jdata = json.loads(data)
    else:
       jdata = data

    for key, value in jdata.iteritems():
        # print("%s : %s \n\n" % (key, value))
        if key == "process_info":
            result, prgper = getProcessResults(value)
            if int(prgper) == 100:
                return True, int(prgper)
            else:
                return False, int(prgper)


def readObject(data):
    if type(data) != dict:
        jdata = json.loads(data)
    else:
        jdata = data

    # my_json_data var contains a dictionory object
    for key, value in jdata.iteritems():
        # print("%s : %s \n\n" % (key, value))
        if key == "vulnerability_info":
            verdict = getVerdict(value)
        elif key == "data_id":
            data_id = str(value)
        elif key == "scan_results":
            total_time, scan_all_result = getScanResults(value)
        elif key == "process_info":
            result, prgper = getProcessResults(value)
        elif key == "file_info":
            fname, fsize = getFileinfo(value)
    # print("data_id, fname, fsize, verdict, total_time, scan_all_result, result, prgper")
    # print( data_id, fname, fsize, verdict, total_time, scan_all_result, result, prgper)
    # return [data_id, verdict, total_time, scan_all_result, result, prgper]
    return ( [data_id, fname, fsize, verdict, total_time, scan_all_result, result, prgper] )


