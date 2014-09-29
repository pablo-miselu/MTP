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

from SQL import SQL
import uuid
import pUtils

class DatabaseApi():
    """
    Contains the functions for all the database interactions necessary for the line to function.
    """
    def __init__(self,dbConfig):
        self.sql = SQL(**dbConfig)
       
    def submitTestRunData(self,testRunSummary,
                          testMeasurementList,
                          stringDictionary,
                          numericDictionary,
                          fileDictionary,
                          dependencyDict):   
        """
        Submits the test run data to the database
        
        Args:
        
        * testRunSummary (list): The summary of the run (each entry is a string)
        * testMeasurementList (list): The measurement data (see :ref:'label_LimitManager`)
        * stringDictionary (dict): Key,value pairs of string data
        * numericDictionary (dict): Key,value pairs of numeric data
        * fileDictionary (dict): Key,value pairs of fileID and its content (zip and base64 encoded)
        * dependencyDict (dict): The subcomponent dependencies of the UUT
        
        Returns:
            None
        """
        
        self.sql.conn()
        
        testRunID = str(uuid.uuid4())
        
        
        s,v = self.prepsForTestRun(testRunSummary,testRunID)
        if s!='': self.sql.execute(s,v)
        s,v = self.prepsForTestMeasurement(testMeasurementList,testRunID)
        if s!='': self.sql.execute(s,v)
        
        
        s,v = self.prepsForDictionary(stringDictionary,testRunID,'StringDictionary')
        if s!='': self.sql.execute(s,v)
        s,v = self.prepsForDictionary(numericDictionary,testRunID,'DoubleDictionary')
        if s!='': self.sql.execute(s,v)
        s,v = self.prepsForDictionary(fileDictionary,testRunID,'FileDictionary')
        if s!='': self.sql.execute(s,v)
        s,v = self.prepsForDictionary(dependencyDict,testRunID,'Components')
        if s!='': self.sql.execute(s,v)
        
        self.sql.commit()
        self.sql.close()



    def prepsForTestRun(self,testRunSummary,testRunID):
        """
        Prepares the sql statement and values vector for the submission of the test run summary to the database
        
        Args:
        
        * testRunSummary (list): The data
        * testRunID (str): The unique identifier to the test run
        
        Returns:
            A tupple (s,v) where
                * s (str): The sql statement
                * v (list): Vector with the values
        """
        s = 'INSERT INTO TestRun'
        s+= ' (testRunID,SN,siteID,stationID,testSequenceID,startTimestamp,endTimestamp,lastTestEntered,isPass)'
        s+= ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        
        v = [testRunID]+testRunSummary
        
        #This converts YYYMMDD-hhmmss to YYY-MM-DD hh:mm:ss, if needed leaves it the same otherwise
        v[5] = pUtils.dateTimeToString(pUtils.stringToDateTime(v[5]),1)
        v[6] = pUtils.dateTimeToString(pUtils.stringToDateTime(v[6]),1)
        
        return s,v
   
    def prepsForTestMeasurement(self,measurementList,testRunID):
        """
        Prepares the sql statement and values vector for the submission of the measurement list to the database
        
        Args:
        
        * measurementList (list): The data
        * testRunID (str): The unique identifier to the test run
        
        Returns:
            A tupple (s,v) where
                * s (str): The sql statement
                * v (list): Vector with the values
        """
        if len(measurementList)==0: return '',[]
        
        s = 'INSERT INTO TestMeasurement'
        s+= ' (testRunID,startTimestamp,endTimestamp,testName,testMeasurementName,dataType,stringMin,stringMeasurement,stringMax,doubleMin,doubleMeasurement,doubleMax,isPass)'
        s+= ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        s+= ',(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'*(len(measurementList)-1)
        s+= ';'
        
        v = []
        for measurement in measurementList:
            data = measurement
            if data[4]=='numeric':
                formattedMeasurement = [testRunID]+data[0:8]+data[5:8]+data[8:]
            else: #Is dataType is string or something else just store it as string
                formattedMeasurement = [testRunID]+data[0:8]+[0,0,0]+data[8:]
            
            #This converts YYYMMDD-hhmmss to YYY-MM-DD hh:mm:ss, if needed leaves it the same otherwise
            formattedMeasurement[1] = pUtils.dateTimeToString(pUtils.stringToDateTime(formattedMeasurement[1]),1)
            formattedMeasurement[2] = pUtils.dateTimeToString(pUtils.stringToDateTime(formattedMeasurement[2]),1)    
        
            v += formattedMeasurement
        
        return s,v
   
   
    def prepsForDictionary(self,d,testRunID,tableName):
        """
        Prepares the sql statement and values vector for the submission of the specified dictionary data to the database
        
        Args:
        
        * d (list): The dictionary data
        * testRunID (str): The unique identifier to the test run
        * tableName (str): The database table to which this data should go
        
        Returns:
            A tupple (s,v) where
                * s (str): The sql statement
                * v (list): Vector with the values
        """
        if len(d)==0: return '',[]
        
        s = 'INSERT INTO '+tableName
        s+= ' (testRunID,key,value)'
        s+= ' VALUES (%s,%s,%s)'
        s+= ',(%s,%s,%s)'*(len(d)-1)
        s+= ';'
        
        v = []
        for key in d:
            v += [testRunID]+[key]+[d[key]]
        return s,v


    def getNextTestSequenceID(self,SN,processID):
        """
        | A route control query.
        | Gets the ID of the test sequence that should be run on the UUT.
        
        Args:
        
        * SN (str): UUT serial number
        * processID (str): The ID for the process to which this UUT belongs on its current assembly stage. 
        
        Returns:
        
        * None, if the unit is not in the system
        * A string containing the test sequence ID that should be run on the given UUT
        """
        s = 'SELECT nextTestSequenceID FROM Transitions'
        s+= ' WHERE SN = %s'
        s+= ' AND processID = %s'
        s+= 'ORDER BY creationTimeStamp DESC Limit 1'
        s+= ';'
        
        v = [SN,processID] 
        
        t=self.sql.quickSqlRead(s,v)
        if len(t)==1:
            return t[0][0]
        return None
      

    def addTransitions(self,entryList):
        """
        | A route control query.
        | Updates the transitions table.
        
        Args:
        
        * entryList (list): A list of entries of the form *(SN,processID,nextTestSequenceID)*
        
        Returns:
            None
        """
        if len(entryList)==0: return
        s = 'INSERT INTO Transitions'
        s+= ' (SN,processID,nextTestSequenceID)'
        s+= ' VALUES (%s,%s,%s)'
        s+= ',(%s,%s,%s)'*(len(entryList)-1)
        s+= ';'
        
        v = [item for entry in entryList for item in entry]
        self.sql.quickSqlWrite(s,v)


    def getSubcomponentData(self,SN,testSequenceID):
        """
        Retrieves the subcomponents for hte specified UUT
        """
        s = 'SELECT key,value FROM Components,TestRun'
        s+= ' WHERE SN = %s'
        s+= ' AND testSequenceID = %s'
        s+= ' AND Components.testRunID = TestRun.testRunID'
        s+= ';'
        
        v = [SN,testSequenceID] 
        
        t=self.sql.quickSqlRead(s,v)
        
        if len(t)==0:
            return {}
        d=[]
        for key,value in t:
            d.append({'processID':key,'SN':value}) 
            
        return d
