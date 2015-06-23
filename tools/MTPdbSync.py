#!/usr/bin/python

from MTP.sfcs.SQL import SQL
import pUtils

from time import sleep
import argparse
import json
import os

fileBaseName = 'MTPdbSync'
extension = 'dump' 
tableNameList = ['TestRun','TestMeasurement','StringDictionary','DoubleDictionary','FileDictionary','Components']#,'Transitions']
MANIFEST_FILE_NAME = 'manifest.json'


def createManifest(manifestFileName,inDirectoryFullPath):
    
    fileNameList = os.listdir(inDirectoryFullPath)
    
    d = {}
    dc = {}
    d['checksumDict'] = dc 
    for fileName in fileNameList:
        if fileName==manifestFileName: continue
        fileFullPath = os.path.join(inDirectoryFullPath,fileName)
        t = pUtils.getFileSha1(fileFullPath)
        dc[fileName] = t
    
    d['meta-data'] = {}
    d['meta-data']['timeStamp_utc'] = pUtils.getTimeStamp()
    d['meta-data']['name'] = os.path.basename(inDirectoryFullPath)
    
    fileFullPath = os.path.join(inDirectoryFullPath,manifestFileName)
    pUtils.quickFileWrite(fileFullPath,json.dumps(d))
    
    return {'retCode':0,'errMsg':None}



    
def dump(**kwargs):
    
    if kwargs['configFileFullPath']:
        DATAMINING_CONFIG = json.loads( pUtils.quickFileRead( kwargs['configFileFullPath'])  )
    else:     
        DATAMINING_CONFIG = json.loads(
           pUtils.quickFileRead(
            os.path.join(
             os.environ['MTP_TESTSTATION'],
             'MTP','config','miselu','database',kwargs['config']
          )
         )
        )
    
    sql = SQL(**DATAMINING_CONFIG)
    sql.conn()
    
    ###   Create virtual table of testRunID's   ###
    SNlist = None
    v = []
    s = 'SELECT testRunID INTO TEMP TABLE SelectedTestRunID FROM TestRun'
    s+= '\n  WHERE creationTimestamp>=%s'
    v.append(kwargs['creationTimestamp_rangeStart'])
    if kwargs['creationTimestamp_rangeEnd']!=None:
        s+= '\n    AND creationTimestamp<=%s'
    if kwargs['startTimestamp_rangeStart']!=None:
        s+= '\n    AND startTimestamp>=%s'
        v.append(kwargs['startTimestamp_rangeStart'])
    if kwargs['startTimestamp_rangeEnd']!=None:
        s+= '\n    AND startTimestamp<=%s'
        v.append(kwargs['startTimestamp_rangeEnd'])
    if kwargs['endTimestamp_rangeStart']!=None:
        s+= '\n    AND endTimestamp>%s'
        v.append(kwargs['endTimestamp_rangeStart'])
    if kwargs['endTimestamp_rangeEnd']!=None:
        s+= '\n    AND endTimestamp<%s'
        v.append(kwargs['endTimestamp_rangeEnd'])
    
    if SNlist!=None:
        s+= '\n    AND (    SN=%s'
        s+= '\n          OR SN=%s'*(len(SNlist)-1)
        s+= '\n )'
        v+= SNlist
   
    if kwargs['siteID']!=None:
        s+= '\n    AND siteID=%s'
        v.append(kwargs['siteID'])
    if kwargs['stationID']!=None:
        s+= '\n    AND stationID=%s'
        v.append(kwargs['stationID'])
    if kwargs['testSequenceID']!=None:
        s+= '\n    AND testSequenceID=%s'
        v.append(kwargs['testSequenceID'])
    if kwargs['isPass']!=None:
        s+= '\n    AND isPass=%s'
        v.append(kwargs['isPass'])
    
    #s+=' limit 10'
    s+='\n ;'
    sql.execute(s,v) ##TODO check if it is blocking or not
    
    
    #For every table, filtered with the TestRunID's table and write it to a file
    directoryFullPath = kwargs['directoryFullPath']
    pUtils.createDirectory(directoryFullPath)
    if len(os.listdir(directoryFullPath))!=0:
        raise Exception ('Directory specified for dump is not empty')
   
    for tableName in tableNameList:
        v=[]
        s = 'COPY'
        s+= '\n (SELECT %s.* FROM %s,SelectedTestRunID'
        s+= '\n WHERE SelectedTestRunID.testRunID = %s.testRunID)'
        s+= '\n TO STDOUT'
        s+= '\n WITH CSV '
        s+= '\n  HEADER '
        s = s % ((tableName,)*3)
        
        fileFullPath = os.path.join(directoryFullPath,fileBaseName+'_'+tableName+'.'+extension)
        with open(fileFullPath,'wt') as f:
            sql.cur.copy_expert(s,f) 
    
    sql.close()
    
    createManifest(MANIFEST_FILE_NAME,directoryFullPath)
    
    return {'retCode':0,'errMsg':None}

def load(**kwargs):
    directoryFullPath = kwargs['directoryFullPath']
    
    t = verify(manifestFileFullPath=os.path.join(directoryFullPath,MANIFEST_FILE_NAME))
    if t['retCode']!=0:
        return {'retCode':1,'errMsg':'Checksum verification failed!','debug':t}
    
    if kwargs['configFileFullPath']:
        DATAMINING_CONFIG = json.loads( pUtils.quickFileRead( kwargs['configFileFullPath'])  )
    else:     
        DATAMINING_CONFIG = json.loads(
           pUtils.quickFileRead(
            os.path.join(
             os.environ['MTP_TESTSTATION'],
             'MTP','config','miselu','database',kwargs['config']
          )
         )
        )
    
    sql = SQL(**DATAMINING_CONFIG)
    sql.conn()
    
    
    
    
   
    
    for tableName in tableNameList:
        #Create Empty Temp table
        v = []
        s = 'SELECT * INTO TEMP TABLE %s FROM %s'
        s+= '\n WHERE testRunID!=testRunID'
        s = s % (tableName+'_t',tableName)
        sql.execute(s,v)
        
        #Load temp table
        v = []
        s = 'COPY'
        s+= '\n %s'
        s+= '\n FROM STDIN'
        s+= '\n WITH CSV '
        s+= '\n  HEADER'
        s = s % (tableName+'_t') 
        fileFullPath = os.path.join(directoryFullPath,fileBaseName+'_'+tableName+'.'+extension)
        
        with open(fileFullPath,'rt') as f:
            sql.cur.copy_expert(s,f)
        
        
    #Create TestRubID_input reference table
    v = ['Table1','Table2','Table2']
    s = 'WITH Table2 as (SELECT testrunID FROM TestRun_t)'
    s+= '\n, TableDiff AS ('
    s+= '\n   SELECT MIN(tableName) as tableName'
    s+= '\n   , testrunID'
    s+= '\n   FROM'
    s+= '\n   ('
    s+= '\n    SELECT %s AS tableName'
    s+= '\n    , testrunID'
    s+= '\n    FROM TestRun'
    s+= '\n    UNION ALL'
    s+= '\n    SELECT %s AS tableName'
    s+= '\n    , testrunID'
    s+= '\n    FROM Table2'
    s+= '\n   ) AS MCH_UnionTable1'
    s+= '\n   GROUP BY testRunID'
    s+= '\n   HAVING COUNT(*) = 1'
    s+= '\n   ORDER BY tableName'
    s+= '\n  )'
    s+= 'SELECT * INTO TEMP TABLE TestRunID_input FROM TableDiff WHERE tableName = %s'
    s+= '\n;'
    sql.execute(s,v)
    
    for tableName in tableNameList:
        #Insert new records
        v = []
        s = 'INSERT INTO %s'
        s+= '\n (SELECT %s.* FROM %s,TestRunID_input WHERE TestRunID_input.testRunID = %s.testRunID)'
        s+= '\n;'
        s = s % ((tableName,)+ (tableName+'_t',)*3)
        sql.execute(s,v)
    
    newRecordsAmount = sql.read('SELECT COUNT(*) FROM TestRunID_input',[])[0][0]
    sql.commit()
    sql.close()
    
    return {'retCode':0,'errMsg':None,'newRecordsAmount':newRecordsAmount}


def packetize(**kwargs):
    
    tmpZipFileName = 'tmpZip.zip'
    tmpZipFileFullPath = os.path.join(kwargs['outDirectoryFullPath'],tmpZipFileName)
    
    pUtils.createDirectory(kwargs['outDirectoryFullPath'])
    
    fileNameList = os.listdir(kwargs['inDirectoryFullPath'])    
    pUtils.createZipFile(kwargs['inDirectoryFullPath'],fileNameList,tmpZipFileFullPath)
    
    t = pUtils.pSlice(tmpZipFileFullPath,kwargs['outDirectoryFullPath'],kwargs['sliceSize'])
    if t['retCode']!=0:
        return {'retCode':1,'errMsg':'Unable to slice file','debug':t}
    
    os.remove(tmpZipFileFullPath)
    
    return {'retCode':0,'errMsg':None}
    
def unpacketize(**kwargs):
    
    fileNameList = os.listdir(kwargs['inDirectoryFullPath'])
    t = [item for item in fileNameList if item.split('.')[-1]=='0']
    
    if len(t)!=1:
        return {'retCode':1,'errMsg':'Unable to determine packet zero'}
    
    packetZeroFileName = t[0]
    packetZeroFullPath = os.path.join(kwargs['inDirectoryFullPath'],packetZeroFileName)
    tmpZipFileName = 'tmpZip.zip'
    tmpZipFileFullPath = os.path.join(kwargs['outDirectoryFullPath'],tmpZipFileName)
    
    pUtils.createDirectory(kwargs['outDirectoryFullPath'])
    
    t = pUtils.pUnSlice(packetZeroFullPath,tmpZipFileFullPath)
    if t['retCode']!=0:
        return {'retCode':2,'errMsg':'Unable to unslice','debug':t}
    
    t = pUtils.unzipFile(tmpZipFileFullPath,kwargs['outDirectoryFullPath'])
    if t!=0:
        return {'retCode':3,'errMsg':'Unable to unzip','debug':t}
    
    os.remove(tmpZipFileFullPath)
    
    manifestFileFullPath = os.path.join(kwargs['outDirectoryFullPath'],MANIFEST_FILE_NAME)
    t = verify(manifestFileFullPath=manifestFileFullPath)
    if t['retCode']!=0:
        return {'retCode':4,'errMsg':'Checksum verification failed!','debug':t}
    
    return {'retCode':0,'errMsg':None} 
    
   
    
def verify(**kwargs):
    directory = os.path.dirname(kwargs['manifestFileFullPath'])
    manifestData = json.loads(pUtils.quickFileRead(kwargs['manifestFileFullPath']))
    
    for fileName,checksum  in manifestData['checksumDict'].iteritems():
        fileFullPath = os.path.join(directory,fileName) 
        if pUtils.getFileSha1(fileFullPath)!=checksum:
            
            return {'retCode':1,'errMsg':'Checksum missmatch: '+fileName}
    
    return {'retCode':0,'errMsg':None}

def transport(**kwargs):
    
    
    srcPath = os.path.dirname(kwargs['packetZeroPath'])
    baseFileName = os.path.basename(kwargs['packetZeroPath'])[:-2]
    
    def scpStr(index):
        s = 'scp -P '+kwargs['port']+' '+kwargs['user']+'@'+kwargs['host']+':'
        s+= os.path.join(srcPath,baseFileName+'.'+str(index))
        s+= ' '+kwargs['dstPath']
        return s
    
    if not os.path.exists(
     os.path.join(kwargs['dstPath'],baseFileName+'.0')):
        
        pUtils.createDirectory(kwargs['dstPath'])
        cmd = scpStr(0)
        t = pUtils.runProgram(cmd,True)
        if t['returnCode']!=0:
            return {'retCode':2,'errMsg':'Unable to retrieve packet zero','debug':t,'cmd':cmd}
        
    
    fileFullPath = os.path.join(kwargs['dstPath'],baseFileName+'.0')
    manifestData = json.loads(pUtils.quickFileRead(fileFullPath))
    sliceAmount = manifestData['sliceAmount']
    checksumDict = manifestData['checksumDict']
    
    for i in range(1,sliceAmount+1):
        fileFullPath = os.path.join(kwargs['dstPath'],baseFileName+'.'+str(i))
        if os.path.exists(fileFullPath):
            fileSha1 = pUtils.getFileSha1(fileFullPath)
            if fileSha1==checksumDict[baseFileName+'.'+str(i)]:
                continue
        
        cmd = scpStr(i)
        t = None
        retryCounter = 0
        while True:
            retryCounter+=1
            if retryCounter>int(kwargs['try']):
                return {'retCode':1,'errMsg':'Max retry reached','debug':t,'cmd':cmd}
            
            t = pUtils.runProgram(cmd,True)
            if t['returnCode']!=0: continue
               
            fileSha1 = pUtils.getFileSha1(fileFullPath)
            if fileSha1!=checksumDict[baseFileName+'.'+str(i)]:
                continue
            
            break
            
    return {'retCode':0,'errMsg':None}
    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser.add_argument('-v', help='Verbose',action='store_true')
    
    command = 'dump'
    subParser=subparsers.add_parser(command)
    subParser.add_argument('--config','-c', help='Name of config file to use (on a predetermined path)',default='dbConfig.json')
    subParser.add_argument('--configFileFullPath', help='Path to the config file to use')
    subParser.add_argument('directoryFullPath', help='Path of the directory to create')
    
    subParser.add_argument('--creationTimestamp_rangeStart', help='',default='1970-01-01 00:00:01')
    subParser.add_argument('--creationTimestamp_rangeEnd'  , help='')
    subParser.add_argument('--startTimestamp_rangeStart', help='')
    subParser.add_argument('--startTimestamp_rangeEnd'  , help='')
    subParser.add_argument('--endTimestamp_rangeStart', help='')
    subParser.add_argument('--endTimestamp_rangeEnd'  , help='')
    
    subParser.add_argument('--siteID'  , help='')
    subParser.add_argument('--stationID'  , help='')
    subParser.add_argument('--testSequenceID'  , help='')
    subParser.add_argument('--isPass'  , help='0,1')
    
    subParser.set_defaults(func=eval(command))  
    
    
    command = 'packetize'
    subParser=subparsers.add_parser(command)
    subParser.add_argument('inDirectoryFullPath', help='')
    subParser.add_argument('outDirectoryFullPath', help='')
    subParser.add_argument('--sliceSize', help='Size in bytes for each packet',default=1024*1024)
    subParser.set_defaults(func=eval(command))
    
    command = 'transport'
    subParser=subparsers.add_parser(command)
    subParser.add_argument('--port','-p', help='Port to use',default = '22')
    subParser.add_argument('--try','-t', help='How many times to try to get each packet',default = '3')
    #subParser.add_argument('--push', help='To push files to remote instead of pull from remote(default)',action='store_true')
    subParser.add_argument('user', help='')
    subParser.add_argument('host', help='')
    subParser.add_argument('packetZeroPath', help='')
    subParser.add_argument('dstPath', help='')
    subParser.set_defaults(func=eval(command))
    
    command = 'unpacketize'
    subParser=subparsers.add_parser(command)
    subParser.add_argument('inDirectoryFullPath', help='')
    subParser.add_argument('outDirectoryFullPath', help='')
    subParser.set_defaults(func=eval(command))
    
    command = 'load'
    subParser=subparsers.add_parser(command)
    subParser.add_argument('--config','-c', help='Name of config file to use (on a predetermined path)',default='dbConfig.json')
    subParser.add_argument('--configFileFullPath', help='Path to the config file to use')
    subParser.add_argument('directoryFullPath', help='Path of the directory to load')    
    subParser.set_defaults(func=eval(command))
    
    command = 'verify'
    subParser=subparsers.add_parser(command)
    subParser.add_argument('manifestFileFullPath', help='Manifest file to use for verification')
    subParser.set_defaults(func=eval(command))
    
    args = parser.parse_args()    
    kwargs = vars(args)
    t = args.func(**kwargs)
    print t

    
