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
  
  
    def getTestRunData_all(self,testSequenceID,startRange=None,endRange=None,SNlist=None,isPass=None):
        """
        Used only by getTestRunData. For more information see getTestRunData docstring
        """
        
        v = [testSequenceID]
    
        ss_TestRunAllPass =   'TestRunAllPass AS'
        ss_TestRunAllPass+= '\n (SELECT * FROM TestRun'
        ss_TestRunAllPass+= '\n  WHERE testSequenceID=%s'
        if isPass!=None:
            ss_TestRunAllPass+= '\n    AND isPass=%s'
            v.append(isPass)
        if startRange!=None:
            ss_TestRunAllPass+= '\n    AND endTimestamp>%s'
            v.append(startRange)
        if endRange!=None:
            ss_TestRunAllPass+= '\n    AND endTimestamp<%s'
            v.append(endRange)
        if SNlist!=None:
            ss_TestRunAllPass+= '\n    AND (    SN=%s'
            ss_TestRunAllPass+= '\n          OR SN=%s'*(len(SNlist)-1)
            ss_TestRunAllPass+= '\n )'
            v+= SNlist
        ss_TestRunAllPass+= '\n )'
      
        s = 'WITH '+ss_TestRunAllPass+'\n SELECT * from TestRunAllPass;'
        
        return self.sql.quickSqlRead(s,v,False)
    
    
    def getTestRunData_first(self,testSequenceID,startRange=None,endRange=None,SNlist=None,isPass=None):
        """
        Used only by getTestRunData. For more information see getTestRunData docstring
        """
        
        v = [testSequenceID]
        
        ss_FirstPass =   'FirstPass AS'
        ss_FirstPass+= '\n (SELECT SN,MIN(endTimestamp) AS endTimestamp FROM TestRun'
        ss_FirstPass+= '\n  WHERE testSequenceID=%s'
        if isPass!=None:
            ss_FirstPass+= '\n    AND isPass=%s'
            v.append(isPass)
        if startRange!=None:
            ss_FirstPass+= '\n    AND endTimestamp>%s'
            v.append(startRange)
        if endRange!=None:
            ss_FirstPass+= '\n    AND endTimestamp<%s'   
            v.append(endRange)
        if SNlist!=None:
            ss_FirstPass+= '\n    AND (    SN=%s'
            ss_FirstPass+= '\n          OR SN=%s'*(len(SNlist)-1)
            ss_FirstPass+= '\n )'
            v+= SNlist
        ss_FirstPass+= '\n GROUP BY SN'
        ss_FirstPass+= '\n )'
      
      
        ss_TestRunFirstPass =   'TestRunFirstPass AS'
        ss_TestRunFirstPass+= '\n (SELECT TestRun.* FROM TestRun, FirstPass'
        ss_TestRunFirstPass+= '\n  WHERE TestRun.SN = FirstPass.SN'
        ss_TestRunFirstPass+= '\n    AND TestRun.endTimestamp = FirstPass.endTimeStamp'
        ss_TestRunFirstPass+= '\n )'
        
        s = 'WITH '+ss_FirstPass+'\n ,'+ss_TestRunFirstPass + '\n SELECT * from TestRunFirstPass;'
        
        return self.sql.quickSqlRead(s,v,False)
    
    
    def getTestRunData_last(self,testSequenceID,startRange=None,endRange=None,SNlist=None,isPass=None):
        """
        Used only by getTestRunData. For more information see getTestRunData docstring
        """
        
        v = [testSequenceID]
        
        ss_LastPass =   'LastPass AS'
        ss_LastPass+= '\n (SELECT SN,MAX(endTimestamp) AS endTimestamp FROM TestRun'
        ss_LastPass+= '\n  WHERE testSequenceID=%s'
        if isPass!=None:
            ss_LastPass+= '\n    AND isPass=%s'
            v.append(isPass)
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
     
    
        
    def getTestRunData(self,testSequenceID,startRange=None,endRange=None,SNlist=None,isPass=None,firstOrLastOnly='last'):
        """
        Queries the database and returns a table containing the data from TestRun table after having been
        filtered by the arguments.
        
        Args:
        * testSequenceID (str): testSequenceID to filter by
        
        * startRange (str): The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * endRange (str):   The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * SNlist (list): A list of SN (str) to filter by
        * isPass (bool+None): If True:  filter for only testruns that are a PASS
                              If False: filter for only testruns that are a FAIL
                              If None: Don't filter, get them both
        * firstOrLastOnly (str): If 'first': Get only the first test run per SN (from the filtered set)
                                 If 'last':  Get only the last  test run per SN (from the filtered set)
                                 If  None:   Get all test runs of each SN (from the filtered set)
        
        Returns:
            A table (list of tuples). Containing the resulting data
        
        | WARNING: When using firstOrLastOnly keep in mind that such will take either the first or last test run per serial number from the set of records that is
        | filtered by the other parameters, such as  isPass, startRange and endRange, etc.
        | For example, if you want for each SN, the last of the PASS test runs within a range, you can get it by using these parameters.
        | But if you want for each SN  within a range, the last test run and only if such last testrun was a PASS, then you need to leave
        | isPass=None and firstOrLastOnly='last'. Then filter out afterwards those that were a FAIL. Because if the last testrun within a range is a FAIL,
        | but there is an earlier record that passed, the isPass flag would filter the FAIL and pick the earlier PASS.
        """
        
        if firstOrLastOnly==None:
            return self.getTestRunData_all(testSequenceID,startRange,endRange,SNlist,isPass)
        elif firstOrLastOnly=='first':
            return self.getTestRunData_first(testSequenceID,startRange,endRange,SNlist,isPass)
        elif firstOrLastOnly=='last':
            return self.getTestRunData_last(testSequenceID,startRange,endRange,SNlist,isPass)
        else:
            raise Exception('getTestRunData: Invalid parameter for firstOrLastOnly')
        
    
    def getComponents(self,testRunID):
        """
        Queries the database and returns the contents of the Components table for
        the given TestRunID.
        
        Args:
        
        * testRunID (str): The testRunID of the testRun of interest
            
        Returns:
            A dictionary containing the key,value pairs of data from the Components table
        """
        
        d = {}
        s = 'SELECT key,value FROM Components'
        s+='\n WHERE %s=testRunID'
        s+='\n;'
        v = [testRunID]
        data = self.sql.quickSqlRead(s,v,False)
        for row in data:
            d[row[0]]=row[1]
        return d
    
    
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

 
    def getTestEntryList(self,testSequenceID):
        """
        | Queries the database to find out the list of test for a given testSequenceID.
        | It uses the last time that a unit ran and pass hte station.
        
        Args:
        
        * testSequenceID (str): The testSequenceID to use
            
        Returns:
            A nested list of the form:
        
        .. code-block:: python
        
            [
                [ testName, [tesrMeasurementName,...,testMeasurementName] ],
                .
                .
                .
                [ testName, [tesrMeasurementName,...,testMeasurementName] ],
            ]
        """
        
        s =   ' SELECT testRunID FROM TestRun'
        s+= '\n WHERE testSequenceID = %s'
        s+= '\n   AND isPass = true'
        s+= '\n ORDER by endTimestamp DESC'
        s+= '\n LIMIT 1 '
        s+= '\n ;'
        v = [testSequenceID]
        
        data = self.sql.quickSqlRead(s,v)
        
        try:
            testRunId = data[0][0]
        except:
            return []
        
        s = 'SELECT testName,testMeasurementName'
        s+= '\n FROM TestMeasurement'
        s+= '\n WHERE testRunID = %s'
        s+= '\n ORDER BY endTimestamp ASC'
        s+= '\n ;'
        
        v = [testRunId]
        data = self.sql.quickSqlRead(s,v)
        
        
        testEntryList = []
        testEntry = [0,[]]
        for row in data:
            if testEntry[0]== row[0]:
                testEntry[1].append(row[1])
            else:
                if testEntry[0]!= 0: #If is not the very first cycle
                    testEntryList.append(testEntry)
                
                testEntry = [row[0],[row[1]]]

        testEntryList.append(testEntry)
        return testEntryList
    
    def getHorizontalaizedTestMeasurementData(self,testSequenceID,testEntryList,isPass=None,startRange=None,endRange=None,isLast=False,SNlist=None):
        """
        Queries the database and returns a table containing
        *Horizontalized* Test Measurement Data
        
        Args:
        * testSequenceID (str): testSequenceID to filter by
        * testEntryList (list): A nested list containing the test and test measurement names (see getTestEntryList docString for format details.
        * isPass (bool+None): If True:  filter for only testruns that are a PASS
                              If False: filter for only testruns that are a FAIL
                              If None: Don't filter, get them both
        * startRange (str): The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * endRange (str):   The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * isLast (bool): If true: only the last testrun, within the filtered subset, of each SN would be used.
                         If false: all testruns, within the filtered subset, of each SN would be used.
        * SNlist (list): A list of SN (str) to filter by
        
        
        Returns:
            A tuple. First element is a table with the data. Second element contain the header for each of the colums.
        
        | WARNING: When using isLast, keep in mind that such will take the las test run per serial number from the set of records that is
        | filtered by the other parameters, such as  isPass, startRange and endRange.
        | For example, if you want for each SN, the last of the PASS test runs within a range, you can get it by using these parameters.
        | But if you want for each SN  within a range, the last test run and only if such last testrun was a PASS, then you need to leave
        | isPass=None and isLast=True. Then filter out afterwards those that were a FAIL. Because if the last testrun within a range is a FAIL,
        | but there is an earlier record that passed, the isPass flag would filter the FAIL and pick the earlier PASS.
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
        
        
        ss_Horizontalize,v_Horizontalize = self.genHorizontalizeString('TableH','TestMeasurementSubset',testEntryList)
            
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

        ####   DEBUG   #############
        #ss = s
        #for i in range(len(v)):
        #    ss=ss.replace('%s',"'"+v[i]+"'",1)
        #print ss
        #print v
        ############################
        
        return self.sql.quickSqlRead(s,v,True)

    def genHorizontalizeString(self,tableName,srcTableName,testEntryList):
        """
           | Cretes a SQL string used to "orizontalize" and report all test measurements
           
           Args:
           
           * tableName (str): The name of the Table to crate
           * srcTableName (str): The name of the Table to use as source
           * testEntryList (list): A nested list containing the test and test measurement names (see getTestEntryList docString for format details.
           
           Returns:
               A string with the SQL string
        """
        
        v = []
        s = ''
        s+= tableName
        s+= '\n AS (SELECT t0.testRunID,t0.SN'
        
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
                    s+= '\n FROM (SELECT DISTINCT testRunID,SN FROM '+srcTableName+' ) AS t0'
                s+= '\n FULL OUTER JOIN\n'
                    
                s+=   '(SELECT testRunID,SN, val AS '+testName+'_'+testMeasurementName+' FROM '+srcTableName
                s+= '\n WHERE testName=%s'
                s+= '\n   AND testMeasurementName=%s'
                s+= '\n) AS '+'t'+str(i)        
              
                s+= ' ON t0.testRunID='+'t'+str(i)+'.testRunID'
                
                v.append(testName)
                v.append(testMeasurementName)
                i+=1
                isFirst = False
        
        s+='\n )'
        
        return s,v
    
    def getFailureData(self,testSequenceID,startRange=None,endRange=None,SNlist=None):
        """
        Queries the database and returns an structure with the details of the failures.
        
        Args:
        * testSequenceID (str): testSequenceID to filter by
        
        * startRange (str): The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * endRange (str):   The start of the time range to mine.
                            The format should be the same as accepted by the database manager.
                            The timestamp when the test was ended is the one used.
        * SNlist (list): A list of SN (str) to filter by
        
        Returns:
            A structure of the form:
            
            .. code-block:: python
        
            [
                { fieldName1:fieldValue1,...,errorDict{testName_testMEasurementName:stringMeasurement,...}  },
                .
                .
                .
            ]
            
        """
        
        isPass = False
        v = [testSequenceID]
        ss_TestRunAllPass =   'TestRunAllPass AS'
        ss_TestRunAllPass+= '\n (SELECT * FROM TestRun'
        ss_TestRunAllPass+= '\n  WHERE testSequenceID=%s'
        if isPass!=None:
            ss_TestRunAllPass+= '\n    AND isPass=%s'
            v.append(isPass)
        if startRange!=None:
            ss_TestRunAllPass+= '\n    AND endTimestamp>%s'
            v.append(startRange)
        if endRange!=None:
            ss_TestRunAllPass+= '\n    AND endTimestamp<%s'
            v.append(endRange)
        if SNlist!=None:
            ss_TestRunAllPass+= '\n    AND (    SN=%s'
            ss_TestRunAllPass+= '\n          OR SN=%s'*(len(SNlist)-1)
            ss_TestRunAllPass+= '\n )'
            v+= SNlist
        ss_TestRunAllPass+= '\n )'
      
        #s = 'WITH '+ss_TestRunAllPass+'\n SELECT * from TestRunAllPass;'
        s = 'WITH '+ss_TestRunAllPass
        s+= '\n SELECT TestRunAllPass.testRunID'
        s+= '\n ,TestRunAllPass.SN'
        s+= '\n ,TestRunAllPass.siteID'
        s+= '\n ,TestRunAllPass.stationID'
        s+= '\n ,TestRunAllPass.testSequenceID'
        s+= '\n ,TestRunAllPass.startTimestamp'
        s+= '\n ,TestRunAllPass.endTimestamp'
        s+= '\n ,TestRunAllPass.lastTestEntered'
        s+= '\n ,SubTestMeasurement.testName'
        s+= '\n ,SubTestMeasurement.testMeasurementName'
        s+= '\n ,SubTestMeasurement.stringMeasurement'
        s+= '\n FROM TestRunAllPass'
        s+= '\n  JOIN'
        s+= '\n (SELECT testName,testMeasurementName,stringMeasurement,testRunID'
        s+= '\n FROM TestMeasurement'
        s+= '\n WHERE isPass=%s ) AS SubTestMeasurement'
        v.append(isPass)
        s+= '\n ON TestRunAllPass.testRunID = SubTestMeasurement.testRunID'
        s+= '\n ORDER BY TestRunAllPass.testRunID ASC'
        s+='\n ;'
        
        resultTable = self.sql.quickSqlRead(s,v,False)
        
        TEST_RUN_ID_INDEX = 0
        SUB_HEADER = ['testRunID', 'SN','siteID','stationID','testSequenceID','startTimestamp','endTimestamp','lastTestEntered']
        returnList = []
        currentTestRunID = None
        
        
        for entry in resultTable:
            if currentTestRunID!=entry[TEST_RUN_ID_INDEX]:
                currentTestRunID=entry[TEST_RUN_ID_INDEX]
                
                d1 = {}
                d2 = {}
                for i in range(len(SUB_HEADER)):
                    d1[SUB_HEADER[i]] = entry[i]
                d1['errorDict'] = d2
                returnList.append(d1)
                
            offset = len(SUB_HEADER)
            d2[ entry[offset]+'_'+entry[offset+1] ] = entry[offset+2]
        
        return returnList