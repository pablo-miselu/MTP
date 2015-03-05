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

from MTP.core.Sequencer import Sequencer

import threading
import sys
import json
import os
from time import sleep

import pUtils

class SequencerThread (threading.Thread):
    """
    | The thread that contains a *Sequencer* (see :ref:`label_Sequencer`) instance.
    | It is important to note that currently the platform is designed to run only one *SequencerThread* at the time.
    | However there are building blocks (such as this one) that are ready to have multiple test sequence running on one computer,
    | but that would require changes in other modules.
    
    Args:
    
    * guiApi (obj): A guiApi type object (see :ref:`label_MtpGui`)
    """
    
    def __init__(self,guiApi):
        super(SequencerThread,self).__init__()        
        self.guiApi = guiApi
    
    def run(self):
        """
        | The code for the thread.
        | It takes care of uploading all the configurations, instantiating a *Sequencer* and passing the configuration to it.
        | This way if some dynamic manipulation to the configuration is required, one can create its own *SequencerThread* type object.
        """
        configRoot = os.path.join(os.environ['MTP_TESTSTATION'],'MTP','config')
        
        configWorkspace = sys.argv[2]
        testStationConfigFileFullPath = os.path.join(configRoot,configWorkspace,'testStationConfig',sys.argv[3])
        limitFileFullPath = os.path.join(configRoot,configWorkspace,'limits',sys.argv[4])
        dbConfigFileFullPath = os.path.join(configRoot,configWorkspace,'database',sys.argv[5])
        
        siteID = sys.argv[1]
        configData = json.loads(pUtils.quickFileRead(testStationConfigFileFullPath))
        configData ['testSequenceID'] = sys.argv[3].split('.')[0]
        
        limitDict = json.loads(pUtils.quickFileRead(limitFileFullPath))
        dbConfig =  json.loads(pUtils.quickFileRead(dbConfigFileFullPath))
     
     
        if len(sys.argv)>6: 
            routeControlProcessRoot = os.path.join(configRoot,configWorkspace,'routeControl','processes',sys.argv[6])
            processDict = {}
            routeControlLookUp = {}
            for fileName in os.listdir(routeControlProcessRoot):
                fileFullPath = os.path.join(routeControlProcessRoot,fileName)
                data = json.loads(pUtils.quickFileRead(fileFullPath))
                
                processID = fileName.split('.')[0]
                processDict[processID] = data
                for node in data['transitionDict']:
                    routeControlLookUp[node] = processID
            
            Sequencer(siteID,configData,limitDict,dbConfig,(processDict,routeControlLookUp),self.guiApi)
        else:
            Sequencer(siteID,configData,limitDict,dbConfig,(),self.guiApi)
       
            
        self.guiApi.sendMessage({'command':'reInitLayout'})
        