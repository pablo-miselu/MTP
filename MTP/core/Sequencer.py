# Copyright 2013 Pablo De La Garza, Miselu Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

from MTP.core.ConfigurationManager import ConfigurationManager
from MTP.core.LimitManager import LimitManager
from MTP.sfcs.DatabaseApi import DatabaseApi
from MTP.sfcs.RouteController import RouteController


import pUtils

import json
import os
import sys
import traceback
import socket
import re

from time import sleep

class Sequencer:
    """
    | It handles the sequencing of the tests, it is virtually the top level of a test run execution.
    | On init it will start the test execution.
    
    Args:
    
    * siteID (str): Unique identifier for the site
    * configData (dict): Containing the test station configuration data
    * limitDict (dict): Contains the test limits
    * dbConfig (dict): Contains the parameter to connect to the database
    * rcData (tuple): Contains the configurations required by the *RouteController* (see :ref:`label_RouteController`)
    * guiApi (obj): A guiApi type of object (see :ref:`label_MtpGui`) 
    * (see :ref:`label_config`)
    """
    def __init__(self,siteID,configData,limitDict,dbConfig,rcData,guiApi = None):
    
        ###   Start of init of object variables   ###
        self.j = 0
        self.i = 0
        self.lastTestEntered = ''
        
        
        self.siteID = siteID
        self.configData = configData
        self.limitDict = limitDict
        self.dbConfig = dbConfig
        self.rcData = rcData
        self.guiApi = guiApi
        
        self.configurationManager = ConfigurationManager(self.configData,self.guiApi)
        self.limitManager = LimitManager(limitDict) 
        self.dbApi = DatabaseApi(dbConfig)
        self.routeController = RouteController(self.rcData,self.dbApi)  
           
        self.stationID = socket.gethostname()
        self.testSuiteID = self.configurationManager.getTestSuiteID()
        self.testSequenceID =  self.configurationManager.getTestSequenceID()
        self.testStationRootFolder = self.configurationManager.getTestStationRootFolder()
        self.isAutomaticSNdialog = self.configurationManager.getIsAutomaticSNdialog()
        self.isSkipBeginningRCcheck = self.configurationManager.getIsSkipBeginningRCcheck()
        self.isMemoryOnly = self.configurationManager.getIsMemoryOnly()
        self.isStopOnFail = self.configurationManager.getIsStopOnFail()
        self.wholeCycles = self.configurationManager.getWholeCycles()
        self.isRouteControllerEnable = self.configurationManager.getIsRouteControlEnable()
        self.isDatabaseEnable = self.configurationManager.getIsDatabaseEnable()
        
        #Init clean reusable variables from guiApi (e.g. queues)
        self.guiApi.sendMessage({'command':'init'})
        #Wait so that the gui receives and handles the message
        sleep(1)
        
        ###   End of init of object variables   ###
        
        
        dependencyDict = {}
        ###   Start of automatic SN's handle   ###
        if self.isAutomaticSNdialog:
            
            uutSNregex = self.routeController.getUutSNregex(self.testSequenceID)
            tt = None
            while tt==None:
                self.guiApi.sendMessage({'command':'pDialog','msg':'SN for UUT','inputHeight':30})
                t = self.guiApi.waitForDialogReturn()
              
                tt = re.match(uutSNregex,t[1])
            self.configurationManager.setSN(t[1])
          
            
            if self.routeController.isStartNode(self.testSequenceID):
                processDependencyList = self.routeController.getDependencyList(self.testSequenceID)
                for processDependency in processDependencyList:
                    tt = None
                    while tt==None:
                        self.guiApi.sendMessage({'command':'pDialog','msg':'SN for ' + processDependency['name'],'inputHeight':30})
                        t = self.guiApi.waitForDialogReturn()
                        tt = re.match(processDependency['SNregex'],t[1])
                    dependencyDict[processDependency['name']] = t[1]
                self.configurationManager.setDependencyDict(dependencyDict)
            
        ###   End of automatic SN's handle   ###
        
        
        for commName, comm in self.configurationManager.configData['communicators'].items():
            if 'isDefault' in comm and comm['isDefault']:
                guiApi.sendMessage({'command':'addConsole',
                                    'consoleID':commName,
                                    'title':commName,
                                  })
                defaultCommName = commName
                break
        
        t = self.configurationManager.configData['communicators'].keys()
        t.sort()
        
        for commName in t:
            if commName==defaultCommName: continue
            guiApi.sendMessage({'command':'addConsole',
                                'consoleID':commName,
                                'title':commName,
                              })
            
                
        for self.j in range(self.wholeCycles):

            try:
    
                self.i = 0
                self.commDict = {} #Initializes just in case something crashes when initializing the drivers
                self.testSuite = None #Initializes just in case something crashes before getting to it
                self.cycleTestResult = True
                self.startTimestamp = pUtils.getTimeStamp()
                self.crashLogFullPath = os.path.join(os.environ['MTP_TESTSTATION'],'crashLogs','crashLog_'+self.startTimestamp+'.log')
                self.limitManager.clearTestMeasurementList()
                
              
                if self.isMemoryOnly==False:
                    self.testRunFolder = self.configurationManager.initTestRunFolder(self.startTimestamp)
                
                if self.isRouteControllerEnable and (not self.isSkipBeginningRCcheck):

                    SN = self.configurationManager.getSN()                   
                    if self.routeController.isOkToTest(SN,self.testSequenceID,dependencyDict)!=True:
                        self.guiApi.sendMessage({'command':'pDialog',
                                                 'msg':'This unit is not routed to this station. Or a subcomponent has not been tested'
                                                })
                        self.guiApi.waitForDialogReturn()
                        self.lastTestEntered = 'RoutingException'
                        raise Exception ('RoutingException')
               
                try:
                    self.commDict = self.configurationManager.initCommunicators()
                except Exception,e:
                    print 'Failed communicator init'
                    self.commDict = self.configurationManager.getCommDict()
                    self.lastTestEntered = 'CommunicatorsInit'
                    print 'commDict='+str(self.commDict)
                    raise Exception('Failed communicator init:'+str(e))
                
                exec('from MTP.testSuites.'+self.testSuiteID+' import '+self.testSuiteID)
                exec('self.testSuite = '+self.testSuiteID+'(self.configurationManager,self.limitManager)')
 
                for test in self.configData['testSequence']:
                    
                    self.lastTestEntered = test['testName']
                    
                    testResult = None
                    for self.i in range(test['cycles']):
                    
                        self.commDict['default'].log('Start of '+test['testName']+' '+str(self.j)+','+str(self.i),0)
                        
                        testStartTimestamp = pUtils.getTimeStamp()
                        exec('measurementDict = self.testSuite.'+test['testName']+'()')
                        testEndTimestamp = pUtils.getTimeStamp()
                        
                        testResult = self.limitManager.checkLimits(test['testName']+'_'+str(self.i),measurementDict,testStartTimestamp,testEndTimestamp)
                        
                        if testResult == False:
                            self.cycleTestResult = False
                        
                        self.commDict['default'].log('Result of '+test['testName']+' '+str(self.j)+','+str(self.i)+' '+('PASS' if testResult else 'FAIL'),0 )
                        
                        if self.isStopOnFail and testResult==False:
                          break
                    
                    if testResult!=None:
                        if self.isStopOnFail and testResult==False:
                            break

                self.testSuite.cleanup()
                
                
                ####HERE error if test fail could be written to summary screen
                #ttt_s = pUtils.quickFileRead(self.testRunFolder+'/db/TestMeasurement.csv')
                ##'\n'.join(self.limitManager.testMeasurementList)
                #self.commDict['default'].log(ttt_s,0)
                
    
            except Exception, e:
                
                self.cycleTestResult = False
                
                s = (
                     '\n***   From the main "try"   ***'+
                     '\nSequencer, (j,i)='+str(self.j)+','+str(self.i)+
                     '\nlastTestEntered='+self.lastTestEntered+
                     '\nexceptionMessage='+e.message+
                     '\ntraceback='+ traceback.format_exc()+
                     '\n*******************************'
                    )
                
                if 'default' in self.commDict:
                    self.commDict['default'].log(s,1)
                else:
                    
                    ss = '###   The following messages will NOT be logged   ###\n'
                    ss+= s
                    ss+= '\n#####################################################\n'
                    print ss
                    pUtils.quickFileWrite(self.crashLogFullPath,ss,'at')
                
                
            finally:
                
                
                self.filePointerDictionary = {}
                
                ###  End all threads from Communicator instances   ###
                for commName,comm in self.commDict.iteritems():
                    if commName=='default': continue
                    print 'Signaling END to Communicator:'+commName
                    comm.signalEndPollingThread()
                for commName,comm in self.commDict.iteritems():
                    if commName=='default': continue
                    print 'Waiting for communicator to END:'+commName
                    comm.waitForPollinThreadToEnd()
                    print '   ...DONE'
                    comm.flushLogFileBuffer()
                    self.filePointerDictionary['logFile_'+commName] = 'log/'+commName+'.log'
              
                try:
                    self.endTimestamp = pUtils.getTimeStamp()
                    
                    SN = self.configurationManager.getSN()
                    self.testRunSummary = [SN,self.siteID,self.stationID,self.testSequenceID,self.startTimestamp,self.endTimestamp,self.lastTestEntered,self.cycleTestResult]
                    self.testMeasurementList = self.limitManager.testMeasurementList
                    if self.testSuite:
                        self.stringDictionary = self.testSuite.stringDictionary
                        self.numericDictionary = self.testSuite.numericDictionary
                        self.filePointerDictionary.update(self.testSuite.filePointerDictionary)
                    else:
                        self.stringDictionary = {}
                        self.numericDictionary = {}
                    self.dependencyDict = self.configurationManager.getDependencyDict()
                    
                    self.fileDictionary = {}
                    for pointerID, fileRelativePath in self.filePointerDictionary.iteritems():
                        fileFullPath = os.path.join(self.testRunFolder,fileRelativePath)
                        fileData = pUtils.quickFileRead(fileFullPath,'rb')
                        self.fileDictionary[pointerID] = pUtils.pPack(fileData)
                    
                    if self.isMemoryOnly==False:
                        ### Write data file
                        self.writeTestRunDataFiles()

                    
                    if self.isDatabaseEnable:
                        
                        #Send to database
                        self.dbApi.submitTestRunData(self.testRunSummary,
                                                self.testMeasurementList,
                                                self.stringDictionary,
                                                self.numericDictionary,
                                                self.fileDictionary,
                                                self.dependencyDict)
                        print 'Data submitted to the database'
                        
                        #RouteControl
                        if self.isRouteControllerEnable!=False:
                            if self.routeController.updateRouteControl_auto(SN,self.testSequenceID,self.cycleTestResult,self.dependencyDict)!=True:
                                if self.cycleTestResult:
                                    self.guiApi.sendMessage({'command':'pDialog','msg':'Route Control Exception (end check)'})
                                    self.guiApi.waitForDialogReturn()
                                    return
                    else:
                        print 'Warning: Database is turned off'
                    
                    

                except Exception,e:
                    
                    
                    s = (
                     '\nSequencer, (j,i)='+str(self.j)+','+str(self.i)+
                     '\nlastTestEntered='+self.lastTestEntered+
                     '\nexception='+str(e)+
                     '\ntraceback='+ '\n'.join(traceback.format_tb(sys.exc_info()[2]) )
                    )
                    ss = '###   Data was not sent to database   ###\n'
                    ss+= s
                    ss+= '\n#########################################\n'
                    
                    print ss
                    pUtils.quickFileWrite(self.crashLogFullPath,ss,'at')

                    self.guiApi.sendMessage({'command':'pDialog','imageFileName': 'fail.png'})
                    self.guiApi.waitForDialogReturn()
                    
                else:
                    if self.j == (self.wholeCycles-1):
                        self.guiApi.sendMessage({'command':'pDialog',
                                                 'buttonTextList':['OK','TestRunFolder'],
                                                 'imageFileName': 'pass.png' if self.cycleTestResult else 'fail.png'})
                        if self.guiApi.waitForDialogReturn()[0]=='TestRunFolder':
                            pUtils.runProgram('nautilus '+self.testRunFolder,shell=True)
                
    def writeTestRunDataFiles(self):
        """
        | Writes all the test run data to drive.
        
        Args:
            None
        
        Returns:
            None
        """
        
        path = os.path.join(self.testRunFolder,'db')

        pUtils.quickFileWrite(os.path.join(path,'TestRun.csv'),
                              ','.join([str(item) for item in self.testRunSummary]))
        
        pUtils.quickFileWrite(os.path.join(path,'TestMeasurement.csv'),
                              '\n'.join([','.join([str(item) for item in entry]) for entry in self.testMeasurementList]))
        
        pUtils.quickFileWrite(os.path.join(path,'StringDictionary.json'),
                              json.dumps(self.stringDictionary))
        
        pUtils.quickFileWrite(os.path.join(path,'DoubleDictionary.json'),
                              json.dumps(self.numericDictionary))
        
        pUtils.quickFileWrite(os.path.join(path,'FileDictionary.json'),
                              json.dumps(self.fileDictionary))
                
        pUtils.quickFileWrite(os.path.join(path,'DependencyDictionary.json'),
                              json.dumps(self.dependencyDict))
        
        
