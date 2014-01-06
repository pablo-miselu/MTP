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

import os
import json
import pUtils


class RouteController:
    """
    Using functions from *DatabaseApi* (see :ref:`label_DatabaseApi`) controls the checks of when it
    is acceptable to run a specific test station on a specific UUT. The *Sequencer* (see :ref:`label_Sequencer`)
    calls those in order to know if is ok to proceed or not with the test.
    
    Args:
    
    * rcData (tuple): Tuple containing:
        * processDict (dict): A dictionary containing all the route control process data as specified in the configuration (see :ref:`label_config`)
        * lookUp : A post processed subset of the data for fast lookup purposes
    
    * dbApi (obj): The handle to the dbApi
    """

    def __init__(self,rcData,dbApi):
        if rcData!=():
            self.processDict = rcData[0]
            self.lookUp = rcData[1]
        self.dbApi = dbApi
        
    
    def isOkToTest(self,SN,testSequenceID,dependencyDict={}):
        """
        Checks if the uut is allowed to be test by *testSequenceID*.
        
        Args:
        
        * SN (str): Serial number of the uut
        * testSequenceID (str): The ID of the test sequence that is intended to be run
        * dependencyDict (dict): A dictionary of the form {processID:SN,...}
        
        Returns:
            True if allowed to test. False if it is not allowed.
        """
        processID = self.getProcessID(testSequenceID)
        process = self.processDict[processID]
        
        nextTestSequenceID = self.dbApi.getNextTestSequenceID(SN,processID)
        if nextTestSequenceID==testSequenceID: return True
               
        if nextTestSequenceID==None and process['startNode']==testSequenceID:
            
            for dependency in process['dependencies']:
                 
                try: depSN = dependencyDict[dependency['name']]
                except:
                    return False #maybe add more error info here
                
                if dependency['name'] in process['preTested']:continue
                if self.dbApi.getNextTestSequenceID(depSN,dependency['name'])!='END':
                    return False
            
            
            return True
            
        return False

        
    def updateRouteControl_manual(self,entryList):
        """
        | Inserts entries into the transitions table.
        | Basically just a wrapper for *DatabaseApi.addTransitions*
        
        Args:
        
        * entryList (list): Contains the entries to insert
        
        Returns:
            None
        """
        self.dbApi.addTransitions(entryList)

    def updateRouteControl_auto(self,SN,testSequenceID,result,dependencyDict={}):
        """
        Automatically updates the transition table based on the information passed as argument plus the
        previously loaded process configuration.
        
        It also verifies if it was ok to test.
        
        Args:
        
        * SN (str): Serial number of UUT
        * testSequenceID (str): ID of the test sequence
        * result (bool): True for PASS. False for FAIL
        * dependencyDict (dict): A dictionary of the form {processID:SN,...}
        
        Returns:
            A boolean. Ture if everything went ok. False if either was not ok to test or result was False.
        """
        
        if self.isOkToTest(SN,testSequenceID,dependencyDict)!=True: return False#maybe add some handling or throw exception here
        if result!=True: return False
        processID = self.getProcessID(testSequenceID)
        process = self.processDict[processID]
        nextTestSequenceID = process['transitionDict'][testSequenceID]
        self.updateRouteControl_manual([[SN,processID,nextTestSequenceID]])
        return True

    def getProcessID(self,testSequenceID):
        """
        Gets the process ID for the specified testSequenceID.
        
        Args:
        
        * testSequenceID (str) : The testSequenceID of which the processID is desired
        
        Returns:
            A string with the process ID.
        """
        return self.lookUp[testSequenceID]
    
    def getComponents(self,processID,SN):
        """
        Gets all the components of a UUT recursively going all levels deep.
        
        Args:
        
        * processID (str): The processID (just in case theer are duplicate SN across different assembly levels)
        * SN (str) : The serial number of the UUT
        
        Returns:
            A list containing all components. The list is nested to receursively contain subcomponent of comconents.
        """
        d = {}
        componentList = []
        
        startNode = self.processDict[processID]['startNode']
        subcomponentList = self.dbApi.getSubcomponentData(SN,startNode)
        
        for subcomponent in subcomponentList:
            subProcessID = subcomponent['processID']
            subSN = subcomponent['SN']
            
            d = {}
            d['processID'] = subProcessID
            d['SN'] = subSN
            d['subcomponentList'] = []
            if subProcessID not in self.processDict[processID]['preTested']:
                d['subcomponentList'].append(self.getComponents(subProcessID,subSN))
            componentList.append(d)
        
        return componentList
   
    def getDependencyList(self,testSequenceID):
        """
        Gets the dependencies. That is the name of the sub assemblies that should be track and
        that also should have reach to the end of a previous process unless they were in the *pretested* list.
        
        Args:
        
        * testSequenceID (str): The testSequenceID of which the dependencies are desired
        
        Returns:
            A list with the dependencies.
        """
        processID = self.getProcessID(testSequenceID)
        process = self.processDict[processID]
        return process['dependencies']
    
    def getUutSNregex(self,testSequenceID):
        """
        Gets the regular expression that defines the format that the SN for the uut should have.
        
        Args:
        
        * testSequenceID (str): The testSequenceID of which the uutSNregex is desired
        
        Returns:
            A string with the uutSNregex.
        """
        processID = self.getProcessID(testSequenceID)
        process = self.processDict[processID]
        return process['uutSNregex']
    
    def isStartNode(self,testSequenceID):
        """
        Checks if the the given testSequenceID is the first one in a route control process.
        
        Args:
        
        * testSequenceID (str): The testSequenceID
        
        Returns:
            A bool, True if it is a start node. False if it is not.
        """
        return self.getStartNode(self.getProcessID(testSequenceID))==testSequenceID
    
    def getStartNode(self,processID):
        """
        Gets the start node of a route control process identified by its process ID.
        
        Args:
        
        * processID (str): The ID of the process in question
        
        Returns:
            A string containing the start node for the given process ID.
        """
        return self.processDict[processID]['startNode']