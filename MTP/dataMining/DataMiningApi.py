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

from MTP.sfcs.SQL import SQL


class DataMiningApi:
    """
    Contains functions for mining the data collected in the line.
    
    Args:
        
        * dbConfig (dict): Contains the database connection parametes (see :ref:`label_config`).
    """
    
    def __init__(self,dbConfig):
        self.sql = SQL(**dbConfig)
    
    def getYieldAndFailureData(self,startRange,endRange):
        """
        Queries the database and prepares a data structure containing
        per station how many uuts passed on the first try *(first pass yield)*,
        how many units passed after the retests *(last pass yield)* and the total
        of units tested.
        
        Additionally for every test of every test station it contains how many units
        fail such test also on both, first and last pass basis.
        
        Args:
        
        * startRange (str): The start of the time range to mine (the format should be the same as accepted by the database manager)
        * endRange (str): The end of the time range to mine (the format should be the same as accepted by the database manager)
        
        Returns:
            A dictionary of the form:
        
        .. code-block:: python
        
            {
                testSequenceID:[firstPassYield,lastPassYield,totalUUT,[
                    [testName,firstPassFailures,lastPassFailures],
                    [testName,firstPassFailures,lastPassFailures],
                    .
                    .
                    .
                    [testName,firstPassFailures,lastPassFailures]
                ]],
                testSequenceID:[firstPassYield,lastPassYield,totalUUT,[
                    [testName,firstPassFailures,lastPassFailures],
                    [testName,firstPassFailures,lastPassFailures],
                    .
                    .
                    .
                    [testName,firstPassFailures,lastPassFailures]
                ]],
                .
                .
                .
                testSequenceID:[firstPassYield,lastPassYield,totalUUT,[
                    [testName,firstPassFailures,lastPassFailures],
                    [testName,firstPassFailures,lastPassFailures],
                    .
                    .
                    .
                    [testName,firstPassFailures,lastPassFailures]
                ]]
            }
        """
        
        d1 = self.getYieldData(startRange,endRange)
        d2 = self.getFailureData(startRange,endRange)
        
        for testSequenceID in d1:
            if testSequenceID not in d2: continue
            testNameList = sorted (d2[testSequenceID].keys())
            
            testNameDataList = []
            for testName in testNameList:
                testNameDataList.append([testName,d2[testSequenceID][testName][0],d2[testSequenceID][testName][1]])
            
            d1[testSequenceID].append(testNameDataList)
            
        return d1


    def getYieldData(self,startRange,endRange):
        """
        Queries the database and prepares a data structure containing
        per station how many uuts passed on the first try *(first pass yield)*,
        how many units passed after the retests *(last pass yield)* and the total
        of units tested.
        
        Args:
        
        * startRange (str): The start of the time range to mine (the format should be the same as accepted by the database manager)
        * endRange (str): The end of the time range to mine (the format should be the same as accepted by the database manager)
            
        Returns:
            A dictionary of the form:
        
        .. code-block:: python
        
            {
                testSequenceID:[firstPassYield,lastPassYield,totalUUT],
                testSequenceID:[firstPassYield,lastPassYield,totalUUT],
                .
                .
                .
                testSequenceID:[firstPassYield,lastPassYield,totalUUT]
            }
        """
        
        ###   First Pass Yield   ###
        s = ' SELECT COUNT(TestRun.SN) AS units,TestRun.testSequenceID,TestRun.isPass FROM TestRun,'
        s+= '    (SELECT SN,testSequenceID, MIN(startTimestamp) AS selectedTimestamp'
        s+= '    FROM TestRun'
        s+= '    WHERE'
        s+= '        startTimestamp > %s'
        s+= '    AND startTimeStamp < %s'
        s+= '    GROUP BY SN,testSequenceID) AS t'
        s+= ' WHERE '
        s+= '     TestRun.SN = t.SN'
        s+= ' AND TestRun.testSequenceID = t.testSequenceID'
        s+= ' AND TestRun.startTimeStamp = selectedTimestamp'
        s+= ' GROUP BY TestRun.testSequenceID,TestRun.isPass'
        s+= ';'
        v = [startRange,endRange]
        data1 = self.sql.quickSqlRead(s,v)
        
        ###   Last Pass Yield   ###
        s = ' SELECT COUNT(TestRun.SN) AS units,TestRun.testSequenceID,TestRun.isPass FROM TestRun,'
        s+= '    (SELECT SN,testSequenceID, MAX(startTimestamp) AS selectedTimestamp'
        s+= '    FROM TestRun'
        s+= '    WHERE'
        s+= '        startTimestamp > %s'
        s+= '    AND startTimeStamp < %s'
        s+= '    GROUP BY SN,testSequenceID) AS t'
        s+= ' WHERE '
        s+= '     TestRun.SN = t.SN'
        s+= ' AND TestRun.testSequenceID = t.testSequenceID'
        s+= ' AND TestRun.startTimeStamp = selectedTimestamp'
        s+= ' GROUP BY TestRun.testSequenceID,TestRun.isPass'
        s+= ';'
        v = [startRange,endRange]
        data2 = self.sql.quickSqlRead(s,v)
        
        d = {}
        for entry in data1:
            if entry[1] not in d:
                d[entry[1]] = [0,0,0]
            
            if entry[2]:       
                d[entry[1]][0] = entry[0]
            d[entry[1]][2] += entry[0]
        
        for entry in data2:    
            if entry[2]:       
                d[entry[1]][1] = entry[0]
                
        return d


    def getFailureData(self,startRange,endRange):
        """
        Queries the database and prepares a data structure containing
        for every test of every test station how many units
        fail such test on both, first and last pass basis.
        
        Args:
        
        * startRange (str): The start of the time range to mine (the format should be the same as accepted by the database manager)
        * endRange (str): The end of the time range to mine (the format should be the same as accepted by the database manager)
        
        Returns:
            A dictionary of the form:
            
        .. code-block:: python
        
            {
                testSequenceID:{
                    testName:[firstPassFailures,lastPassFailures],
                    testName:[firstPassFailures,lastPassFailures],
                    .
                    .
                    .
                    testName:[firstPassFailures,lastPassFailures]
                ],
                 testSequenceID:{
                    testName:[firstPassFailures,lastPassFailures],
                    testName:[firstPassFailures,lastPassFailures],
                    .
                    .
                    .
                    testName:[firstPassFailures,lastPassFailures]
                ],
                .
                .
                .
                 testSequenceID:{
                    testName:[firstPassFailures,lastPassFailures],
                    testName:[firstPassFailures,lastPassFailures],
                    .
                    .
                    .
                    testName:[firstPassFailures,lastPassFailures]
                ]
            }
        """
        

        s = ' SELECT COUNT(TestRun.SN),TestRun.testSequenceID,TestRun.lastTestEntered FROM TestRun,'
        s+= '    (SELECT SN,testSequenceID,MIN(startTimestamp) as selectedTimestamp' 
        s+= '     FROM TestRun'
        s+= '     WHERE'
        s+= '         startTimestamp > %s'
        s+= '     AND startTimeStamp < %s'
        s+= '     GROUP BY SN,testSequenceID) AS t'
        s+= ' WHERE'
        s+= '     TestRun.SN = t.SN'
        s+= ' AND TestRun.testSequenceID = t.testSequenceID'
        s+= ' AND TestRun.startTimeStamp = selectedTimestamp'
        s+= ' AND TestRun.isPass = FALSE'
        s+= ' GROUP BY TestRun.testSequenceID,TestRun.lastTestEntered'
        s+= ';'
        v = [startRange,endRange]
        data1 = self.sql.quickSqlRead(s,v)
        

        s = ' SELECT COUNT(TestRun.SN),TestRun.testSequenceID,TestRun.lastTestEntered FROM TestRun,'
        s+= '    (SELECT SN,testSequenceID,MAX(startTimestamp) as selectedTimestamp' 
        s+= '     FROM TestRun'
        s+= '     WHERE'
        s+= '         startTimestamp > %s'
        s+= '     AND startTimeStamp < %s'
        s+= '     GROUP BY SN,testSequenceID) AS t'
        s+= ' WHERE'
        s+= '     TestRun.SN = t.SN'
        s+= ' AND TestRun.testSequenceID = t.testSequenceID'
        s+= ' AND TestRun.startTimeStamp = selectedTimestamp'
        s+= ' AND TestRun.isPass = FALSE'
        s+= ' GROUP BY TestRun.testSequenceID,TestRun.lastTestEntered'
        s+= ';'
        v=[startRange,endRange]
        data2 = self.sql.quickSqlRead(s,v)

        d = {}
        for entry in data1:
            if entry[1] not in d:
                d[entry[1]] = {}    
            if entry[2] not in d[entry[1]]:
                d[entry[1]][entry[2]] = [0,0]
            d[entry[1]][entry[2]][0] = entry[0]
            
        for entry in data2:
            if entry[1] not in d:
                d[entry[1]] = {}    
            if entry[2] not in d[entry[1]]:
                d[entry[1]][entry[2]] = [0,0]
            d[entry[1]][entry[2]][1] = entry[0]
            
        return d
