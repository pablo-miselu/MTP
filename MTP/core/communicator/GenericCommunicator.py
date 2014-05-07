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

import sys
import pUtils
import time
from time import sleep
import re
import os

import threading
from MTP.core.PollingThread import PollingThread

class GenericCommunicator(object):
    """
    Suitable to handle most of text based communications. For an overview of the tasks that a communicator is meant to handle see :ref:`label_Communicator`.
    
    On init:
    
    * Initialices buffers and other object variables
    * Creates locks for the variables shared amongst threads
    
    Args:
        * commInstanceID (str): The ID of this communicator instance
        * configurationManager (variable): Two options for this parameter:
            * A MTP.core.ConfigurationManager.ConfigurationManager object
                or
            * A dictionary with all the parameters required, this is to facilitate the use of a communicator on "not so standard" uses of it (e.g. independant command line tools)
    """

    def __init__(self,commInstanceID,configurationManager):
      
        self.parseBuffer = ''
        self.logFileBuffer = ''
   
        self.commInstanceID = commInstanceID
        
        ###   Start of handling of different instance types for configurationManager   ###
        if isinstance(configurationManager,dict):
        
            self.guiApi = None
            self.logFileBufferSize = configurationManager['logFileBufferSize']
            self.isMemoryOnly = configurationManager['isMemoryOnly']
            self.isPrintToConsole = configurationManager['isPrintToConsole']
            self.testRunFolder = configurationManager['testRunFolder']            
            
            driverName = configurationManager['driverName']
            driverConfigParams = configurationManager['driverConfigParams']
            pollingThreadInterval = configurationManager['pollingThreadInterval']
            
            if logLevel in configurationManager:
                self.loLevel = configurationManager['logLevel']
            else:
                self.logLevel = 3        
        
        else:
            
            self.configurationManager = configurationManager
            self.guiApi = self.configurationManager.getGuiApi()
            self.logFileBufferSize = self.configurationManager.getLogFileBufferSize()
            self.isMemoryOnly = self.configurationManager.getIsMemoryOnly()
            self.testRunFolder = self.configurationManager.getTestRunFolder()
            self.logLevel = self.configurationManager.getLogLevel()
            driverName = self.configurationManager.getDriverName(commInstanceID)
            driverConfigParams = self.configurationManager.getDriverConfigParams(commInstanceID)
            
            pollingThreadInterval = .05
            #pollingThreadInterval = self.configurationManager.geInterval(commInstanceID)
            #self.isPrintToConsole = self.configurationManager.getIsPrintToConsole(commInstanceID)
            
        ###   End of handling of different instance types for configurationMAnager   ###    

        exec('from MTP.drivers.%s import %s' % (driverName,driverName))
        exec('self.driver = '+driverName+'(**driverConfigParams)')

        self.logFileBufferLock = threading.Lock()
        self.parseBufferLock = threading.Lock()
        self.pollingThreadLock = threading.Lock()
            
        self.launchPollingThread(pollingThreadInterval)
        

    def log (self,msg,logLevel):
        """
        Inserts msg and logLevel into a preformatted log message and sends it to the gui and logFile buffers.
        
        Args:
        
        * msg (str): The string/message to log
        * logLevel (int): Starting from 0 specifies the type of messaging for ease of filtering.
            
        Returns:
            None
        """
        
        if self.logLevel>=logLevel:    
            logMessage = self.formatLogMessage(msg,logLevel)
            self.updateLogFileBuffer(logMessage)
            self.updateConsoleBuffer(logMessage)
            if self.guiApi:
                self.guiApi.sendMessage({'command':'processEvents'})
        
    
    def communicate(self,msg,regex,timeout):
        """
        | Clears the parsing buffer.
        | Sends *msg*.
        | Waits until either the parsing buffer has a match of *regex* or until *timeout* seconds have passed.
        | If there was a match it returns it.
        | If there was no match an Exception is raised.
        
        Args:
        
        * msg (str): The string/message to send
        * regex (str): A regex, same syntax as the standard python *re* module uses
        * timeout (float): Timeout in seconds
            
        Returns:
            A *re.MatchObject* instance
        """
        
        self.flushParseBuffer()
        self.transmit(msg)
        return self.receive(regex,timeout)
        
    
    def transmit(self,msg):
        """
        | Logs msg in both text and hex representations.
        | Sends *msg*.
        
        Args:
        
        * msg (str): The string/message to send
            
        Returns:
            None
        """
        
        msgHex = ' '.join([('%0.2X'%byte) for byte in bytearray(msg)])
        self.log('Transmitting. Text=[ '+msg+' ] Hex=[ '+msgHex+' ]',0)
        self.driver.transmit(msg)
    
   
    def receive(self,regex,timeout,interval=1):
        """
        | Waits until either the parsing buffer has a match of *regex* or until *timeout* seconds have passed.
        | If there was a match it returns it.
        | If there was no match an Exception is raised.
        
        Args:
        
        * regex (str): A regex, same syntax as the standard python *re* module uses
        * timeout (float): Timeout in seconds
        * interval (float): Time in seconds to sleep between checks to the buffer
        
        Returns:
            A *re.MatchObject* instance
        """
        
        timeAnchor = time.time()
        r = re.compile(regex)
        while(time.time()-timeAnchor<timeout):
            with self.parseBufferLock:
                t = r.search(self.parseBuffer)
            
                if t!=None:
                    self.parseBuffer = self.parseBuffer[t.end():]        
                    return t
            sleep(interval)
            
        raise Exception('Communicator: Did not receive expected answer within timeout.regex='+str(regex))
    
        
    def close(self):
        """
        | Closes the connection.
        |  Stops the polling thread.
        |  Flushes the log buffer.
        
        Args:
            None
            
        Returns:
            None
        """
        self.endPollingThread()
        self.flushLogFileBuffer()
        
    
    def formatLogMessage(self,msg,logLevel):
        """
        | Formats *msg* and *logLevel* into a string of the form *LogMessageStart <logLevel> <timeStamp> Msg:<msg> LogMessageEnd*.
        | Appends a newline at the end.
        
        Args:
        
        * msg (str): The string/message to send
        * logLevel (int): Starting from 0 specifies the type of messaging for ease of filtering.
            
        Returns:
            The formatted string
        """
        
        return 'LogMessageStart '+str(logLevel)+' '+pUtils.getTimeStamp()+' Msg:'+msg+' LogMessageEnd\n'
    
    
    def updateLogFileBuffer(self,data,forceFlush=False):
        """
        | Updates the log file buffer by appending the contents of *data* to it.
        | If the buffer is bigger than the configured value for it (see :ref:`label_config`) or *forceFlush* is set to true, the buffer is flushed.
        | By flushing the buffer is meant to update the logFile file and clear the buffer.
        
        Args:
            data (str): Data to append to the buffer
            forceFlush (bool): If true the buffer is flush regardless.
            
        Returns:
            None
        """
        
        
        
        with self.logFileBufferLock:
            
            self.logFileBuffer += str(data)
            
            if self.isMemoryOnly==False:
        
                if len(self.logFileBuffer)>self.logFileBufferSize or forceFlush==True:
                    
                    logFileFolderFullPath = os.path.join(self.testRunFolder,'log')
                    if not os.path.exists(logFileFolderFullPath):
                        pUtils.createDirectory(logFileFolderFullPath)
                    
                    logFileFullPath = os.path.join(logFileFolderFullPath,self.commInstanceID+'.log')
                    pUtils.quickFileWrite(logFileFullPath,self.logFileBuffer,'at')
                    self.logFileBuffer = ''
    
            
    def updateParseBuffer(self,data):
        """
        | Updates the internal buffer using for parsing by appending the contents of *data* to it.
        
        Args:
            data (str): Data to append to the buffer
            
        Returns:
            None
        """
        
        with self.parseBufferLock:
            self.parseBuffer += data
    
    
    def updateConsoleBuffer(self,data):
        """
        | Updates the buffer used for console display.
        | The update is done indirectly by passing the data through the *guiApi* object in use.
        
        Args:
            data (str): Data to append to the buffer
            
        Returns:
            None
        """
        
        if self.guiApi: 
            self.guiApi.sendMessage({'command':'consoleWrite',
                                    'consoleID':self.commInstanceID,
                                    'text':data,
                                    })
        
        elif self.isPrintToConsole:
            sys.stdout.write(data)


    def flushLogFileBuffer(self):
        """
        | Flushes the log file buffer.
        | By flushing the buffer is meant to update the logFile file and clear the buffer.
        
        Args:
            None
            
        Returns:
            None
        """
        self.updateLogFileBuffer('',True)
        
        
    def flushParseBuffer(self):
        """
        | Flushes the internal buffer used for parsing.
        | By flushing the buffer is meant to clear/empty it.
        
        Args:
            None
            
        Returns:
            None
        """
        with self.parseBufferLock:
            self.parseBuffer = ''
    
    
    def pollingFunction(self):
        """
        | Reads from the specific instantiated driver (see :ref:`label_drivers`).
        | Updates all buffers with the new data.
        |
        | This function is meant to be called by (and only by) the *pollingThread*.
        
        Args:
            None
            
        Returns:
            None
        """
        
        with self.pollingThreadLock:
            data = self.driver.receive(999)
            self.updateParseBuffer(data)
            self.updateConsoleBuffer(data)
            self.updateLogFileBuffer(data)
        
        
    def launchPollingThread(self,interval=1):
        """
        | Instantiates and start a pollingThread (see :ref:`label_PollingThread`).
        
        Args:
            None
            
        Returns:
            None
        """
        self.log('Launching Communicator pollingThread',1)
        self.pollingThread = PollingThread(self.pollingFunction,interval)
        self.pollingThread.start()
        
            
    def endPollingThread(self):
        """
        | Signals the polling thread to finish (see :ref:`label_PollingThread`).
        | Waits for the polling thread to finish (see :ref:`label_PollingThread`).
        
        Args:
            None
            
        Returns:
            None
        """
        self.pollingThread.endThread()
        self.pollingThread.join()
        self.driver.close()
    
    
    def signalEndPollingThread(self):
        """
        | Signals the polling thread to finish (see :ref:`label_PollingThread`).
        
        Args:
            None
            
        Returns:
            None
        """
        self.pollingThread.endThread()
        
        
    def waitForPollinThreadToEnd(self):
        """
        | Waits for the polling thread to finish (see :ref:`label_PollingThread`).
        | Before calling this method *signalEndPollingThread* should be called. 
        
        Args:
            None
            
        Returns:
            None
        """
        
        self.pollingThread.join()
        self.driver.close()
