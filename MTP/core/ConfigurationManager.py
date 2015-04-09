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

import uuid
import os

import pUtils

class ConfigurationManager:
    """
    | It revceives and stores the testStationConfig data.
    | Initializes the communicators (see :ref:`label_Communicator`) and stores its handles for later retrieval.
    | It also stores and retrieve some "dynamic data" to be use during the test run.
    | this object is passed around trhough most modules, from the *Sequencer* (see :ref:`label_Sequencer`) at the *almost* top, to the drivers (see :ref:`label_drivers`) at the bottom.

    On init:
    
    .. code-block:: python
    
        self.configData = configData
        self.guiApi = guiApi
        self.testStationRootFullPath = os.environ['MTP_TESTSTATION']
        
        ###   Dynamic Data   ###
        self.dependencyDict = {}
        self.commDict = {}
        self.testRunFolderFullPath = ''
        self.SN = 'placeholder_SN'
        
    Args:
    
    * configData (dict):
    * guiApi (obj): An instance of a guiApi type of object (see :ref:`label_MtpGui`) 
    """


    def __init__(self,configData,guiApi=None):
        self.configData = configData
        self.guiApi = guiApi
        self.testStationRootFullPath = os.environ['MTP_TESTSTATION']
       
        self.testRunID = str(uuid.uuid4())
        
        ###   Dynamic Data   ###
        self.dependencyDict = {}
        self.commDict = {}
        self.testRunFolderFullPath = ''
        self.SN = 'placeholder_SN'


    def initCommunicators(self):
        """
        | Instantiates the communicators specified in the configuration (see :ref:`label_config`).
            
        Args:
            None
            
        Returns:
            A dictionary containing all the communicators instantiated
        """

        self.commDict = {}
        for ID in self.configData['communicators']:
            
            commClassName = self.configData['communicators'][ID]['commClassName']
            
            exec('from MTP.core.communicator.'+commClassName+' import '+commClassName)
            exec('self.commDict[ID] = '+commClassName+'(ID,self)')
            
            if ('isDefault' in self.configData['communicators'][ID] and
                self.configData['communicators'][ID]['isDefault']):
                self.commDict['default'] = self.commDict[ID]
                
        return self.commDict
     
    
    def startCommunicatorsByConfig(self):
        """
        | Starts the communicators. Before calling this function *initCommunicators*  must be called first.
            
        Args:
            None
            
        Returns:
            None
        """

        for ID in self.commDict:
            if ID=='default': continue
            
            isStartOnInit = self.configData['communicators'][ID].get('isStartOnInit',True)
            if isStartOnInit:
                self.commDict[ID].start()
                

    def initTestRunFolder(self,startTimestamp):
        """
        | Creates the directory to be used for the test run.
        | It uses the value of self.SN .
        | It uses the value of self.testRunID
        | The full path remains stored as an object variable.
        
        
        Args:
            
        * startTimestamp (str): The timestamp from the start of the test
        
        Returns:
            A string with the full path to the folder for the test run
        """

        if self.getIsMemoryOnly():
            raise Exception('Attempting to create TestRunFolder while isMemoryOnly flag is set')
        
        testSequenceID = self.configData['testSequenceID']
        self.testRunFolderName = testSequenceID+'_'+startTimestamp+'_'+self.SN+'_'+self.testRunID
        print 'testRunFolderName='+self.testRunFolderName
        self.testRunFolderFullPath = os.path.join(self.getTestStationRootFolder(),'TestRunDataStorage',self.testRunFolderName)
        
        pUtils.createDirectory(self.testRunFolderFullPath)
        
        return self.testRunFolderFullPath
   


    def setSN(self,SN):
        """
        Sets the serial number
        """
        self.SN = SN
    

    def setDependencyDict(self,dependencyDict):
        """
        Sets the dictionary of dependencies (see :ref:`label_RouteController`)
        """
        self.dependencyDict = dependencyDict



    def getCommDict(self):
        """
        | Gets the dictionary containing all the communicators previously instantiated with *initCommunicators*
        """
        return self.commDict

    
    def getTestRunID(self):
        """
        Gets a string with the testRunID
        """
        return self.testRunID
    
    def getTestRunFolder(self):
        """
        | Gets a string with the full path to the folder for the test run, previously created with *initTestRunFolder*
        """
        return self.testRunFolderFullPath


    def getGuiApi(self):
        """
        Gets the guiApi object (see :ref:`label_MtpGui`)
        """
        return self.guiApi
   
   
    def getSN(self):
        """
        Gets the string with the serial number
        """
        return self.SN
   
    
    def getDependencyDict(self):
        """
        Gets the dictionary of dependencies (see :ref:`label_RouteController`)
        """
        return self.dependencyDict    
    

    def getTestStationRootFolder(self):
        """
        | Gets a string with the full path to the *testStationRootFolder*.
        | This is the same as the environment variable MTP_TESTSTATION (see :ref:`label_gettingStarted`).
        """    
        return self.testStationRootFullPath 
 

    def getTestSequenceID(self):
        """
        | Gets the test sequence ID.
        | Unique string that identifies the configuration set in use.
        """
        return self.configData['testSequenceID']    
    
    
    def getTestSuiteID(self):
        """
        | Gets the test suite ID.
        | Name of the class to instantiate that contains the tests.
        """
        return self.configData['testSuiteID']
    
    def getTestSequence(self):
        """
        | Gets the list of tests to run.
        """
        return self.configData['testSequence']
    
    def getDriverName(self,commInstanceID):
        """
        | Gets the class name of the driver to use by the communicator identified by *commInstanceID*.
        """
        return self.configData['communicators'][commInstanceID]['driverName']
    
    def getDriverConfigParams(self,commInstanceID):
        """
        | Gets the dictionary of parameters required by the driver to be used by the communicator identified by *commInstanceID*.
        """
        return self.configData['communicators'][commInstanceID]['driverConfigParams']
   
    def getReadRetryInterval(self,commInstanceID):
        """
        | Gets the *readRetryInterval*  parameter for the communicator identified by *commInstanceID*.
        """
        return self.configData['communicators'][commInstanceID]['readRetryInterval']
   
    def getPollingThreadInterval(self,commInstanceID):
        """
        | Gets the *pollingThreadInterval*  parameter for the communicator identified by *commInstanceID*.
        """
        return self.configData['communicators'][commInstanceID]['pollingThreadInterval']    
    
    ###   Flags   ###
    def getFlags(self):
        """
        | Gets the dictionary of flags.
        """
        return self.configData['flags']
    
    def getWholeCycles(self):
        """
        | Gets the value of the flag *wholeCycles*.
        | An int that indicates how many time to execute the whole test sequence.
        """
        return self.getFlags().get('wholeCycles',1)
    
    def getIsStopOnFail(self):
        """
        | Gets the value of the flag *isStopOnFail*.
        | A bool that if true, the test run will end early when one test fails.
        """
        return self.getFlags().get('isStopOnFail',True)
    
    def getIsAutomaticSNdialog(self):
        """
        | Gets the *isAutomaticSNdialog* flag.
        | A bool that if true indicates to automatically pop up SN dialog(s) to collect the SN of the UUT and of any
        | dependency.
        | If *isAutomaticSNdialog* is false, then the platform will expect the test code to provide
        | the SN. (i.e. the test code reads the SN electronically from the
        | UUT and passes it to the platform by using *setSN*) 
        """
        return self.getFlags().get('isAutomaticSNdialog',True)
    
    def getIsSkipBeginningRCcheck(self):
        """
        | Gets the *isSkipBeginningRCcheck* flag.
        | A bool that if true indicates to skip the route control check at the beginning of the test run.
        | This is needed in cases where route control is wanted, but not all the SN's required for the check at available beforehand.
        | In this scenario the test code will electronically collect and provide the SN's. At the end of the test run the routing will be checked.
        """
        return self.getFlags().get('isSkipBeginningRCcheck',True)
    
    def getLogFileBufferSize(self):
        """
        | Gets the value of the flag *logFileBufferSize*.
        | An int that defines at which size should the log file buffer be flushed (see :ref:`label_Communicator`).
        """
        return self.getFlags().get('logFileBufferSize',1024)
        
    def getIsMemoryOnly(self):
        """
        | Gets the value of the flag *isMemoryOnly*.
        | A bool that defines whether or not write the test run data to disk.
        """
        return self.getFlags().get('isMemoryOnly',False)
        
    def getIsRouteControlEnable(self):
        """
        | Gets the value of the flag *isRouteControlEnable*.
        | A bool that enables/disable the use of RouteControl (see :ref:`label_RouteController`).
        """
        return self.getFlags().get('isRouteControlEnable',False)
    
    def getIsDatabaseEnable(self):
        """
        | Gets the value of the flag *isDatabaseEnable*.
        | A bool that enables/disable the use of the database
        """
        return self.getFlags().get('isDatabaseEnable',True)
    
    def getCustomResultWindow(self):
        """
        | Gets the value of the flag *customResultWindow*.
        | A string with the name ofthe function to call at the end of the test to present results.
        """
        return self.getFlags().get('customResultWindow',None)
    
    def getLogLevel(self):
        """
        | Gets the value of the flag *getLogLevel*.
        | An int that controls the verbosity. From 0 to 3. (-1 disables all log messages)
        """
        return self.getFlags().get('logLevel',0)
    
    
    #############
    
   
   
   
    