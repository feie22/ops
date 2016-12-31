#encoding=utf-8

import os
import subprocess
from threading import Thread
import logging

isError = False

def hdfsWritable(fPath):
    try:
        if hdfsIsExisted(fPath,False):
            logging.error("the file has already existed! file:" + fPath)
            return False
        mkdirStr = "hadoop fs -mkdir " + fPath
        no = subprocess.call(mkdirStr, stdout=subprocess.PIPE, shell=True)
        if no == 0:
            curPath = os.getcwd()
            tmpFile = curPath + "/tmp.txt"
            #if tmp.txt exist:
            if not os.path.exists(tmpFile):
                with open(tmpFile,"w") as f1:
                    f1.write('tmpfile\n')
                    f1.flush()
            putStr = "hadoop fs -put " + tmpFile + " " + fPath
            reNo = subprocess.call(putStr, stdout=subprocess.PIPE, shell=True)
            if reNo == 0:
                delStr = "hadoop fs -rm -r " + fPath
                subprocess.call(delStr, stdout=subprocess.PIPE, shell=True)
                os.remove(tmpFile)
                return True
            else:
                 logging.error("The file does not have permission to write! path: " + fPath)
                 return False
        else:
            logging.error("can not create the folder! path:" + fPath)
            return False
    except Exception,e:
        raise e

def hdfsIsExisted(fPath="",logType=True):
    try:
        shellStr = "hadoop fs -du -s " + fPath
        reNo = subprocess.call(shellStr, stdout=subprocess.PIPE, shell=True)
        if reNo == 0:
            return True
        else:
            if logType:
                logging.error(fPath + " does not exist!")
            else:
                logging.info(fPath + " does not exist!")
            return False
    except Exception,e:
        raise e

def trainCheck(argDict):
    flag = True
    if not argDict.has_key("data"):
        logging.error("the path of trainingData is empty!");
        flag = False
    if not hdfsIsExisted(argDict.get("data")):
        flag = False
    if (argDict.has_key("test_data")) and (not hdfsIsExisted(argDict.get("test_data"))):
        flag = False
    if (argDict.has_key("eval_data")) and (not hdfsIsExisted(argDict.get("eval_data"))):
        flag = False
    if (argDict.has_key("model_dir")) and (not hdfsWritable(argDict.get("model_dir"))):
        flag = False
    if (argDict.has_key("model_out")) and (not hdfsWritable(argDict.get("model_out"))):
        flag = False
    
    return flag

def predCheck(argDict):
    flag = True
    if not argDict.has_key("model_in"):
        logging.error("the path of modelInData is empty!");
        flag = False
    if not hdfsIsExisted(argDict.get("model_in")):
        flag = False
    if not argDict.has_key("test_data"):
        logging.error("the path of test-data is empty!");
        flag = False
    if not hdfsIsExisted(argDict.get("test_data")):
        flag = False
    if not argDict.has_key("name_pre"):
        logging.error("the path of namePre is empty!");
        flag = False
    if not hdfsWritable(argDict.get("name_pre")):
        flag = False

    return flag

def dumpCheck(argDict):
    flag = True
    if not argDict.has_key("model_in"):
        logging.error("the path of modelInData is empty!");
        flag = False
    if not hdfsIsExisted(argDict.get("model_in")):
        flag = False
    if not argDict.has_key("name_dump"):
        logging.error("the path of nameDump is empty!");
        flag = False
    if not hdfsWritable(argDict.get("name_dump")):
        flag = False
    
    return flag

def getTaskType(cmdArgs):
    task = ""
    for tmp in cmdArgs:
        arg = tmp.lower().strip().split("=")
        if len(arg) != 2: continue
        name = arg[0]
        value = arg[1]
        #task
        if name.find("task") > -1:
            task = value
            break
    if task == "":
        task = "train"
    return task

def hdfsCheck(cmdArgs):
    argDict = {}
    #task type
    task = ""
    try:
        for tmp in cmdArgs:
            arg = tmp.strip().split("=")
            if len(arg) != 2: continue
            name = arg[0].lower()
            value = arg[1]
            #task
            if name.find("task") > -1:
                task = value
                continue
             #test-data
            if name.find("test:data") > -1:
                argDict["test_data"] = value
                continue
            #train-data
            if name.find("data") > -1:
                argDict["data"] = value
                continue
            #eval-data
            if name.find("eval[") > -1:
                argDict["eval_data"] = value
                continue
            #model_in
            if name.find("model_in") > -1:
                argDict["model_in"] = value
                continue
            #model_out
            if name.find("model_out") > -1:
                argDict["model_out"] = value
                continue
            #model_dir
            if name.find("model_dir") > -1:
                argDict["model_dir"] = value
                continue
            #name_dump
            if name.find("name_dump") > -1:
                argDict["name_dump"] = value
                continue
            #name_pre
            if name.find("name_pre") > -1:
                argDict["name_pre"] = value
                continue
        if task == "":
            task = "train"
        logging.info("task=" + task)
        
        reFlag = True
        if task == "train":
            reFlag = trainCheck(argDict)
        elif task == "pred":
            reFlag = predCheck(argDict)
        elif task == "dump":
            reFlag = dumpCheck(argDict)
        else:
            logging.error("unknow task.task-name:" + task);
        
        return reFlag
    except Exception,e:
        logging.error(e.message)        
