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

import pUtils

class LimitManager:
    """
    | Receives and stores the limits to be use on the test run.
    | Contains the methods to compare a specific result against its limits.
    | Stores the test measurement data (min, measured, max, pass/fail and so forth).

    On init:
    
    .. code-block:: python
    
        self.testMeasurementList = []
        self.limitDict = limitDict
   
    Args:
    
    * limitDict (dict): Dictionary containing the limist to use(see :ref:`label_config`).
    """
      
    def __init__(self,limitDict):
        self.testMeasurementList = []
        self.limitDict = limitDict
        
    
    def checkLimits(self,testName,measurementDict,testStartTimestamp,testEndTimestamp):
        """
        | This is the heart of the  LimitManager.
        | For every key in *measurementDict* compares its value against limits.
        | Updates *self.testMeasurementList*.
        | Each entry of the list has the format:
        | <startTimestamp>,<endTimestamp>,<testName>,<measurementName>,<varType>,<min>,<measured>,<max>,<pass/fail (bool) >

        On init:
        
        .. code-block:: python
        
            self.testMeasurementList = []
            self.limitDict = limitDict
       
        Args:
        
        * testName (str): The name of the test to which this measuments belong to
        * measurementDict (dict): Key,value pairs of <measurementName>:<measurementValue>
        * testStartTimeStamp (str): The timestamp of when the test started
        * testEndTimeStamp (str): The timestamp of when the test ended
        
        Returns:
            A bool, true if every measurement was within limits, false otherwise
        """
        overallTestResult = True
        for measurementName,measurementValue in measurementDict.iteritems():
            
            limitName = measurementName
            if isinstance(measurementValue,dict):
                limitName = measurementValue.get('limitName',measurementName)
                measurementValue = measurementValue['measurementValue']
                
            
            limit = self.limitDict.get(limitName,{"type":"string","expected":"PASS"})
            
            if isinstance(measurementValue,list) and len(measurementValue)>0:
                isAddPostFix = True
                measurementValueList = measurementValue
            else:
                isAddPostFix = False
                measurementValueList = [measurementValue]
                
            
            i = 0
            for measurementValue in measurementValueList:
            
                if isAddPostFix:
                    postfix =  '_a'+str(i)
                else:
                    postfix = ''
                    
                if limit['type']=='numeric':
                    if (measurementValue >= limit['min'] and 
                        measurementValue <= limit['max'] ):
                        result = True
                    else:
                        result = False
                        overallTestResult = False
                
                    self.testMeasurementList.append([testStartTimestamp,testEndTimestamp,
                                                    testName,measurementName+postfix,
                                                    'numeric',
                                                    limit['min'],
                                                    measurementValue,
                                                    limit['max'],
                                                    result])
                
                elif limit['type']=='string':
                    if measurementValue == limit['expected']: 
                        result = True
                    else:
                        result = False
                        overallTestResult = False
    
                    self.testMeasurementList.append([testStartTimestamp,testEndTimestamp,
                                                    testName,measurementName+postfix,
                                                    'string',
                                                    limit['expected'],
                                                    measurementValue,
                                                    limit['expected'],
                                                    result])
                
                
                else:
                    raise Exception('Invalid type for limitName='+measurementName+'. Review your limit files')
            
                i+=1
                
        return overallTestResult
    
    
    def clearTestMeasurementList(self):
        """
        Clears *testMeasurementList*
        """
        self.testMeasurementList = []
        
    def getTestMeasurementList(self):
        """
        Gets the *testMeasurementList* which is updated every call to *checkLimits*.
        """
        return self.testMeasurementList
     
    def getLimits(self):
        """
        Gets the *limitDict*.
        """
        return self.limitDict