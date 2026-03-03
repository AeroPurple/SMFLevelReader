import sys
import os
from os import listdir
from os.path import dirname, basename, splitext, join

def get_application_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

titleScreenWaitTime=0
decorType=0
useANSI=0
configVersion=0
programVersion=2

def convertToConfigData(versionIndex,waitTime,decorType,useANSI):
    return (((versionIndex<<8|waitTime)<<2|decorType)<<1|(useANSI))<<7
    
def configSave(versionIndex,waitTime,decorType,useANSI):
    configData=convertToConfigData(versionIndex,waitTime,decorType,useANSI)
    configData=configData.to_bytes(3,'big')
    configFile=open(os.path.join(get_application_path(), 'Settings.cfg'),mode='wb')
    configFile.write(configData)
    configFile.close()

def configLoad():
    global configVersion
    global titleScreenWaitTime
    global decorType
    global useANSI
    global firstRun
    
    try:
        configFile=open(os.path.join(get_application_path(), 'Settings.cfg'),mode='rb')
    except:
        configSave(programVersion,62,2,1)
        configFile=open(os.path.join(get_application_path(), 'Settings.cfg'),mode='rb')
        firstRun=True
    finally:
        try:
            configData=configFile.read()
            if int((bin(int.from_bytes(configData,'big'))[2:].zfill(16))[:6],2)==1:
                configVersion=1
                configData=bin(int.from_bytes(configData,'big'))[2:].zfill(16)
            else:
                configData=bin(int.from_bytes(configData,'big'))[2:].zfill(24)
                configVersion=int(configData[:6],2)
            if configVersion>2 or configVersion==0:
                print(f"Config version reported as {configVersion}, may be invalid.")
            titleScreenWaitTime=int(configData[6:14],2)
            decorType=int(configData[14:16],2)
            useANSI=int(configData[16:17])
            configFile.close()
        except Exception as e:
            print(e)
            exit(1)
            configSave(programVersion,62,2,1)