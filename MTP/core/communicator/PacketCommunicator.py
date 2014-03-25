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

from MTP.core.communicator.GenericCommunicator import GenericCommunicator
from MTP.core.PollingThread import PollingThread


MIDI_MISELU_MFG_ID = '\x00\x02\x00'
MIDI_MISELU_MIDI_PROCESSOR = '\x00'

class C24_MidiCommunicator(GenericCommunicator):
    """
    A specialized midi communicator for the C24
    
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
        self.rawBuffer = ''
        self.packetBuffer = []
        self.rawBufferLock = threading.Lock()  
        self.packetBufferLock = threading.Lock()  
        super(C24_MidiCommunicator, self).__init__(commInstanceID,configurationManager)
      
      
    def pollingFunction(self):
        """
        | Reads from the specific instantiated driver (see :ref:`label_drivers`).
        | Updates all buffers with the new data.
        | Parses rawBuffer and places hte packets into packetBuffer.
        |
        | This function is meant to be called by (and only by) the *pollingThread*.
        
        Args:
            None
            
        Returns:
            None
        """
        
        #Read
        data = self.driver.receive(999)
        
        #If new data, update buffers
        if len(data)>0:
            self.updateRawBuffer(data)
        
            displayData = ' '.join(['%0.2X'%byte for byte in data]) + '\n'
            self.updateConsoleBuffer(displayData)
            self.updateLogFileBuffer(displayData)
        
        self.parsePackets()
   
   
    def receive(self,regex,timeout,interval=1):
        """
        | Waits until either there is a match of *regex* or until *timeout* seconds have passed.
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
            with self.packetBufferLock:
                
                for i in range(len(self.packetBuffer)):
                    t = r.match(self.packetBuffer[i])    
                    if t!=None:
                        self.packetBuffer.pop(i)
                        return t
            sleep(interval)
            
        raise Exception('Communicator: Did not receive expected answer within timeout')


    def updateRawBuffer(self,data=None,bytesToRemove=None):
        """
        | Updates the internal raw buffer used to stored incoming data.
        
        buffer 
        
        Args:
            * data (str): Data to append to the buffer
            * bytesToRemove (int): Amount of bytes to remove from the beginning
            
        Returns:
            None
        """
        
        with self.rawBufferLock:
            if (data): self.rawBuffer += data
            if (bytesToRemove): self.rawBuffer = self.rawBuffer[bytesToRemove:]
            
            
    def updatePacketBuffer(self,data):
        """
        | Updates the internal packet buffer used to stored incoming data as packets.
        
        buffer 
        
        Args:
            * data (str): Data packet to append to the buffer
            
        Returns:
            None
        """
        
        with self.packetBufferLock:
            if (data): self.packetBuffer.append(data)
            
            
    def flushRawBuffer(self):
        """
        | Flushes the internal raw buffer.
        | By flushing the buffer is meant to clear/empty it.
        
        Args:
            None
            
        Returns:
            None
        """
        with self.rawBufferLock:
            self.rawBuffer = ''
            
            
    def flushPacketBuffer(self):
        """
        | Flushes the internal packet buffer.
        | By flushing the buffer is meant to clear/empty it.
        
        Args:
            None
            
        Returns:
            None
        """
        with self.packetBufferLock:
            self.packetBuffer = ''