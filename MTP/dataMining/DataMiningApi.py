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
        
    
    def getTestRunData(self,testSequenceID,startRange=None,endRange=None,SNlist=None):    
        v = [testSequenceID]
        
        ss_LastPass =   'LastPass AS'
        ss_LastPass+= '\n (SELECT SN,MAX(endTimestamp) AS endTimestamp FROM TestRun'
        ss_LastPass+= '\n  WHERE testSequenceID=%s'
        if startRange!=None:
            ss_LastPass+= '\n    AND endTimestamp>%s'
            v.append(startRange)
        if endRange!=None:
            ss_LastPass+= '\n    AND endTimestamp<%s'   
            v.append(endRange)
        if SNlist!=None:
            ss_LastPass+= '\n    AND (    SN=%s'
            ss_LastPass+= '\n          OR SN=%s'*(len(SNlist)-1)
            ss_LastPass+= '\n )'
            v+= SNlist
        
        ss_LastPass+= '\n GROUP BY SN'
        ss_LastPass+= '\n )'
      
      
        ss_TestRunLastPass =   'TestRunLastPass AS'
        ss_TestRunLastPass+= '\n (SELECT TestRun.* FROM TestRun, LastPass'
        ss_TestRunLastPass+= '\n  WHERE TestRun.SN = LastPass.SN'
        ss_TestRunLastPass+= '\n    AND TestRun.endTimestamp = LastPass.endTimeStamp'
        ss_TestRunLastPass+= '\n )'
        
        s = 'WITH '+ss_LastPass+'\n ,'+ss_TestRunLastPass + '\n SELECT * from TestRunLastPass;'
        
        return self.sql.quickSqlRead(s,v,False)
    
    
    
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


    def getWIPdata(self,startRange=None,endRange=None):
        """
        Queries the database to find out for each unit what was the last
        test sequence that it passed and returns an agregate per sequence ID.
        
        Args:
        
        * startRange (str): The start of the time range to mine (the format should be the same as accepted by the database manager)
        * endRange (str): The end of the time range to mine (the format should be the same as accepted by the database manager)
            
        Returns:
            A dictionary of the form:
        
        .. code-block:: python
        
            {
                testSequenceID:amountOfUnitsAtStation,
                testSequenceID:amountOfUnitsAtStation,
                .
                .
                .
                testSequenceID:amountOfUnitsAtStation,
            }
        """
        
        
        s = ' SELECT COUNT(TestRun.SN) AS units,TestRun.testSequenceID FROM TestRun,'
        s+= '    (SELECT SN, MAX(startTimestamp) AS selectedTimestamp'
        s+= '    FROM TestRun'
        s+= '    WHERE'
        s+= '        TestRun.isPass = True'
        if startRange:
            s+= '    AND startTimestamp > %s'
        if endRange:
            s+= '    AND startTimeStamp < %s'
        s+= ' GROUP BY SN'
        s+= '    ) AS t'
        s+= ' WHERE '
        s+= '     TestRun.SN = t.SN'
        s+= ' AND TestRun.startTimestamp = selectedTimestamp'
        s+= ' GROUP BY TestRun.testSequenceID'
        s+= ';'
        v = [startRange,endRange]
        data = self.sql.quickSqlRead(s,v)
        
        d = {}
        for v,k in data:
            d[k] = v
        
        return d

 
###############################################################################################################3333
    def getTestEntryList(self,testSequenceID):
        s =   ' SELECT testRunID FROM TestRun'
        s+= '\n WHERE testSequenceID = %s'
        s+= '\n   AND isPass = true'
        s+= '\n ORDER by endTimestamp DESC'
        s+= '\n LIMIT 1 '
        s+= '\n ;'
        v = [testSequenceID]
        
        data = self.sql.quickSqlRead(s,v)
        testRunId = data[0][0]
        
        s = 'SELECT testName,testMeasurementName'
        s+= '\n FROM TestMeasurement'
        s+= '\n WHERE testRunID = %s'
        s+= '\n ORDER BY endTimestamp ASC'
        s+= '\n ;'
        
        v = [testRunId]
        data = self.sql.quickSqlRead(s,v)
        
        testEntryList = []
        testEntry = [0,[]]
        buffer0 = ''
        for row in data:
            if testEntry[0]== row[0]:
                testEntry[1].append(row[1])
            else:
                if testEntry[0]!= 0:
                    testEntryList.append(testEntry)
                
                testEntry = [0,[]]
                testEntry[0] = row[0]
                testEntry[1].append(row[1])
        testEntryList.append(testEntry)
        
        
        return testEntryList
    
    def getHorizontalaizedTestMeasurementData(self,testSequenceID,testEntryList,isPass=None,startRange=None,endRange=None,isLast=True,SNlist=None):
        """
        | THIS FUNCTION IS UNDER DEVELOPMENT
        |
        Queries the database and returns a table containing
        *Horizontalized* Test Measurement Data
        
        Args:
        * testSequenceID (str): testSequenceID to filter by
        * testEntryList (list): a list of the format <TO FILL IN> that indicates which test and test measurements to include
        * isPass (bool): isPass to filter by
        * startRange (str): The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * endRange (str):   The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        
        
        Returns:
            A table...dictionary of the form:
        
        .. code-block:: python
        
            ###TBD
        """
        
        
        ss_LastPass =   'LastPass AS'
        ss_LastPass+= '\n (SELECT SN,MAX(endTimestamp) AS endTimestamp FROM TestRun'
        ss_LastPass+= '\n  WHERE testSequenceID=%s'
        if isPass!=None:
            ss_LastPass+= '\n    AND isPass=%s'
        if startRange!=None:
            ss_LastPass+= '\n    AND endTimestamp>%s'
        if endRange!=None:
            ss_LastPass+= '\n    AND endTimestamp<%s'   
        if SNlist!=None:
            ss_LastPass+= '\n    AND (    SN=%s'
            ss_LastPass+= '\n          OR SN=%s'*(len(SNlist)-1)
            ss_LastPass+= '\n )'
        ss_LastPass+= '\n GROUP BY SN'
        ss_LastPass+= '\n )'
      
      
        ss_TestRunLastPass =   'TestRunLastPass AS'
        ss_TestRunLastPass+= '\n (SELECT TestRun.* FROM TestRun, LastPass'
        ss_TestRunLastPass+= '\n  WHERE TestRun.SN = LastPass.SN'
        ss_TestRunLastPass+= '\n    AND TestRun.endTimestamp = LastPass.endTimeStamp'
        ss_TestRunLastPass+= '\n )'
        
        ss_TestRunAllPass =   'TestRunAllPass AS'
        ss_TestRunAllPass+= '\n (SELECT * FROM TestRun'
        ss_TestRunAllPass+= '\n  WHERE testSequenceID=%s'
        if isPass!=None:
            ss_TestRunAllPass+= '\n    AND isPass=%s'
        if startRange!=None:
            ss_TestRunAllPass+= '\n    AND endTimestamp>%s'
        if endRange!=None:
            ss_TestRunAllPass+= '\n    AND endTimestamp<%s'   
        if SNlist!=None:
            ss_TestRunAllPass+= '\n    AND (    SN=%s'
            ss_TestRunAllPass+= '\n          OR SN=%s'*(len(SNlist)-1)
            ss_TestRunAllPass+= '\n )'
        ss_TestRunAllPass+= '\n )'
      
        
        ss_InTestRunID =   'InTestRunID AS'
        if isLast:
            ss_InTestRunID+= '\n (SELECT testRunID,SN FROM TestRunLastPass)'
        else:
            ss_InTestRunID+= '\n (SELECT testRunID,SN FROM TestRunAllPass)'
    
      
        ss_TestMeasurementSubset =   'TestMeasurementSubset AS'
        ss_TestMeasurementSubset+= '\n (SELECT TestMeasurement.testRunID'
        ss_TestMeasurementSubset+= '\n        ,InTestRunID.SN'
        ss_TestMeasurementSubset+= '\n        ,TestMeasurement.testName'
        ss_TestMeasurementSubset+= '\n        ,TestMeasurement.testMeasurementName'
        ss_TestMeasurementSubset+= '\n        ,TestMeasurement.stringMeasurement AS val'
        ss_TestMeasurementSubset+= '\n        ,TestMeasurement.isPass'
        ss_TestMeasurementSubset+= '\n  FROM TestMeasurement, InTestRunID'
        ss_TestMeasurementSubset+= '\n  WHERE TestMeasurement.testRunID=InTestRunID.testRunID'
        ss_TestMeasurementSubset+= '\n )'
        
        
        ss_Horizontalize,v_Horizontalize = genHorizontalizeString('TableH','TestMeasurementSubset',testEntryList)
            
        if isLast:
            s = 'WITH '+ ss_LastPass
            s+= '\n , '+ ss_TestRunLastPass
        else:
            s = 'WITH '+ ss_TestRunAllPass
        
        s+= '\n , '+ ss_InTestRunID
        s+= '\n , '+ ss_TestMeasurementSubset
        s+= '\n , '+ ss_Horizontalize
        s+= '\n SELECT * from TestRun,TableH WHERE TestRun.testRunID=TableH.testRunID'
        s+= ';'
        
        v = [testSequenceID]
        if isPass!=None:
            v.append(isPass)
        if startRange!=None:
            v.append(startRange)
        if endRange!=None:
            v.append(endRange)
        if SNlist!=None:
            v+= SNlist
            
        v += v_Horizontalize

        return self.sql.quickSqlRead(s,v,True)
        
############################################################################################################################

def genHorizontalizeString(tableName,srcTableName,testEntryList):
    v = []
    s = ''
    s+= tableName
    s+= '\n AS (SELECT t1.testRunID,t1.SN'
    
    for testEntry in testEntryList:
        testName = testEntry[0]
        for testMeasurementName in testEntry[1]:
            s+= '\n,'+testName+'_'+testMeasurementName

    i = 1
    isFirst = True
    for testEntry in testEntryList:
        testName = testEntry[0]
        for testMeasurementName in testEntry[1]:
            if isFirst:
                s+= '\n FROM ('
            else:
                s+= '\n FULL OUTER JOIN\n'
                
            s+=   '(SELECT testRunID,SN, val AS '+testName+'_'+testMeasurementName+' FROM '+srcTableName
            s+= '\n WHERE testName=%s'
            s+= '\n   AND testMeasurementName=%s'
            s+= '\n) AS '+'t'+str(i)        
          
            if not isFirst:
                s+= ' ON t1.testRunID='+'t'+str(i)+'.testRunID'
            
            v.append(testName)
            v.append(testMeasurementName)
            i+=1
            isFirst = False
    
    s+='\n )'
    s+='\n )'
    
    return s,v



#def genHorizontalizeString(tableName,srcTableName,testEntryList):
#    v = []
#    s = ''
#    s+= tableName
#    s+= '\n AS (SELECT t1.testRunID,t1.SN'
#    
#    for testEntry in testEntryList:
#        testName = testEntry[0]
#        for testMeasurementName in testEntry[1]:
#            s+= '\n,'+testName+'_'+testMeasurementName
#
#    i = 1
#    isFirst = True
#    for testEntry in testEntryList:
#        testName = testEntry[0]
#        for testMeasurementName in testEntry[1]:
#            if isFirst:
#                isFirst = False
#                s+= '\n FROM '
#            else:
#                s+= '\n , '
#                
#            s+=   '(SELECT testRunID,SN, val AS '+testName+'_'+testMeasurementName+' FROM '+srcTableName
#            s+= '\n WHERE testName=%s'
#            s+= '\n   AND testMeasurementName=%s'
#            s+= '\n) AS '+'t'+str(i)        
#            
#            v.append(testName)
#            v.append(testMeasurementName)
#            i+=1
#    
#    
#    i = 1
#    isFirst = True
#    for testEntry in testEntryList:
#        testName = testEntry[0]
#        for testMeasurementName in testEntry[1]:
#            if i==1:
#                i+=1
#                continue
#            
#            if isFirst:
#                isFirst = False
#                s+= '\n WHERE '
#            else:
#                s+= '\n   AND '
#                
#            s+= 't1.testRunID='+'t'+str(i)+'.testRunID'
#            i+=1
#           
#    s+='\n )'
#    
#    return s,v

############################################################


    