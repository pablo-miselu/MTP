from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse_lazy,reverse

from MTP.dataMining.DataMiningApi import DataMiningApi
import pUtils

import json
import datetime
import calendar
import re
import datetime


from KeyCurveReport import KeyCurveReport, isWhiteKey

import logging
logger = logging.getLogger(__name__)




@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def yieldsView(request):
    
    t = mtnPermissionCheck(request)
    if t['mtnID']==None:
        return t['HttpResponse']
    mtnID = t['mtnID']
        
    startDate = request.GET.get('startDate','')
    endDate = request.GET.get('endDate','')
    if startDate =='': startDate = '2015-05-18'
    if endDate   =='': endDate   = '2015-06-05'     
    
    dataMiningApi = getDataMiningApi(mtnID)
    data = dataMiningApi.getYieldAndFailureData(startDate,endDate)
    
    testSequenceIDlist = settings.MTN_DICT[mtnID]['testSequenceIDlist']
    
    t = []        
    for testSequenceID in testSequenceIDlist:
        if testSequenceID not in data: continue
        t.append(testSequenceID)
    
    responseDict = {}
    responseDict['title'] = 'Yields'
    responseDict['startDate'] = startDate
    responseDict['endDate'] = endDate
    responseDict['data_json'] = json.dumps(data)
    responseDict['orderList_json'] = json.dumps(t) 
    responseDict['mtnID'] = mtnID
    responseDict['comboBoxData'] = []
    for mtnID in generate_mtnID_validList(request):
        responseDict['comboBoxData'].append({'text':mtnID,'value':mtnID})
    
    return render_to_response('Dashboard_yield.html',responseDict,context_instance=RequestContext(request))


def findFirstSundayOfMonth(year,month):
    d = datetime.date(year=year,month=month,day=1)
    return 1+(6-d.weekday())
    
def getPdtPstCutline(year):
    month = 3
    nSunday = 2
    hour = 10
    d1 = datetime.datetime(year=year,month=month,day=findFirstSundayOfMonth(year,month)+7*(nSunday-1),hour=hour)
    
    month = 1
    nSunday = 1
    hour = 9
    d2 = datetime.datetime(year=year,month=month,day=findFirstSundayOfMonth(year,month)+7*(nSunday-1),hour=hour)
    return d1,d2

def getPdtPstCutlineP(year):
    month = 3
    nSunday = 2
    hour = 2
    d1 = datetime.datetime(year=year,month=month,day=findFirstSundayOfMonth(year,month)+7*(nSunday-1),hour=hour)
    
    month = 1
    nSunday = 1
    hour = 2
    d2 = datetime.datetime(year=year,month=month,day=findFirstSundayOfMonth(year,month)+7*(nSunday-1),hour=hour)
    return d1,d2
    
def UTC2SFO(timestamp):
    cutLines = getPdtPstCutline(timestamp.year)
    if timestamp>cutLines[0] and timestamp<cutLines[1]: #PDT
        offset = datetime.timedelta(hours=7)
    else: #PST
        offset = datetime.timedelta(hours=8)
    return timestamp-offset

def SFO2UTC(timestamp):
    cutLines = getPdtPstCutlineP(timestamp.year)
    if timestamp>cutLines[0] and timestamp<cutLines[1]: #PDT
        offset = datetime.timedelta(hours=7)
    else: #PST
        offset = datetime.timedelta(hours=8)
    return timestamp+offset
    

def flatten(l):
    return [item for row in l for item in row]


###   Simple Unit Data Reporting   ###
@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def testRunView(request):
    SN=request.GET.get('SN',None)

    t = mtnPermissionCheck(request)
    if t['mtnID']==None:
        return t['HttpResponse']
    mtnID = t['mtnID']
    
    dataMiningApi = DataMiningApi(settings.DATAMINING_CONFIG[  settings.MTN_DICT[mtnID]['dbConfigID']  ])
    
    s = 'SELECT testrunID,SN,stationID,testSequenceID,endTimestamp,lastTestEntered,isPass'
    s+= '\n FROM TestRun'
    s+= '\n WHERE SN = %s'
    s+= '\n ORDER BY endTimestamp ASC'
    s+= '\n ;'
    v = [SN]
    testRunTable,headerRow = dataMiningApi.sql.quickSqlRead(s,v,True)
    
    if testRunTable==None or len (testRunTable)==0:
        return HttpResponse('The SN %s was not found on the data for the mtnID %s' % (SN,mtnID) )
    else:
        testRunColumns = len(testRunTable[0])
    
    
    ############    
    colorList = ['#E2E2E2','#B6B6B6']
    #colorList = ['#FFFFFF','#FFFFFF']
    
    def asf_rowFunction(row):
        asf_rowFunction.colorIndex = (asf_rowFunction.colorIndex+1)%2
        return {'colorIndex':asf_rowFunction.colorIndex}
    asf_rowFunction.colorIndex = 1
    
    def asf_defaultFormatFunc(cellDatum,cropLimit,colorIndex,**kwargs):
        cellBgColor = colorList[colorIndex]
        s = str(cellDatum)
        d = {'text':s[:cropLimit],'cellBgColor':cellBgColor}
        if len(s)>cropLimit:
            import math
            charsPerSet = cropLimit
            d['data_content'] = ' '.join([s[charsPerSet*i:charsPerSet*(i+1)] for i in range(int(math.ceil(len(s)/(charsPerSet*1.0))))])
        return d
    
    def asf_formatFunc_col_negative1(cellDatum,cropLimit,**kwargs):
        cellBgColor = '#55FF55' if cellDatum==True else '#FF0000'
        cellDatum   =    'PASS' if cellDatum==True else 'FAIL'
        return {'text':str(cellDatum)[:cropLimit],'cellBgColor':cellBgColor}

    def asf_formatFunc_col_0(cellDatum,cropLimit,colorIndex,**kwargs):
        cellBgColor = colorList[colorIndex]
        s = str(cellDatum)
        d = {'text':s[:cropLimit],'cellBgColor':cellBgColor,
             'href':reverse('DataMining.views.testMeasurementView')+'?testRunID='+s+'&mtnID='+mtnID}
            
        if len(s)>cropLimit:
            import math
            charsPerSet =2
            d['data_content'] = ' '.join([s[charsPerSet*i:charsPerSet*(i+1)] for i in range(int(math.ceil(len(s)/(charsPerSet*1.0))))])
        return d        

    formatFuncList = []
    for i in range(len(testRunTable[0])):
        formatFuncList.append(asf_defaultFormatFunc)
    
    formatFuncList[-1] = asf_formatFunc_col_negative1
    formatFuncList[0] = asf_formatFunc_col_0
        

    cropLimitList = [10,15,20,20,20,30,6]
    cellWidthList = [(item+4)*10 for item in cropLimitList]
    gridData = gridFormattingSequencer(testRunTable,formatFuncList,cropLimitList,asf_rowFunction)
    
    ######################
    headerRow = ['Test Run ID','SN','Station ID','Test Sequence ID','TimeStamp','Last Test Entered','isPass'] 
    hc = { 
          'top':      {'d':100,'legendList':headerRow,'className':'header'},
          'bottom':   {'d':10,'legendList':[],        'className':'header'},
          'left':     {'d':10,'legendList':[],        'className':'header'},
          'right':    {'d':10,'legendList':[],        'className':'header'},
         }
    
    gcd = {}
    gcd['data'] = flatten(gridData)
    gcd['cellsX'] = testRunColumns
    gcd['cellsY'] = len(gcd['data'])/  gcd['cellsX']
    gcd['cellWidthList'] = cellWidthList
    gcd['cellHeight'] = 36
    gcd['headerConfig'] = hc
       
      
    
    ##################
    
    responseDict = {}
    responseDict['gridConfigAndData_json'] = json.dumps(gcd)
    responseDict['bodyBgColor'] = '#F1F1F1'
    responseDict['title'] = 'Test Runs'
    
    responseDict['mtnID'] = mtnID
    
    return render_to_response('SingleTable.html',responseDict,context_instance=RequestContext(request))

@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def testMeasurementView(request):
    
    mtnID = request.GET.get('mtnID',None)
    testRunID = request.GET.get('testRunID',None)
   
    t = mtnPermissionCheck(request)
    if t['mtnID']==None:
        return t['HttpResponse']
    mtnID = t['mtnID']
    
    dataMiningApi = DataMiningApi(settings.DATAMINING_CONFIG[  settings.MTN_DICT[mtnID]['dbConfigID']  ])
    
    
    gcdL = []
    colorList = ['#E2E2E2','#B6B6B6']
    
    
    #s = 'SELECT SN,stationID,testSequenceID,endTimestamp,isPass'
    s = 'SELECT SN,siteID,stationID,testSequenceID,startTimestamp,endTimestamp,lastTestEntered,isPass'
    s+= '\n FROM TestRun'
    s+= '\n WHERE testRunID = %s'
    v = [testRunID]
    testRunData,testRunHeaderRow = dataMiningApi.sql.quickSqlRead(s,v,True)
    
    def asf_defaultFormatFunc(cellDatum,cropLimit,colorIndex,**kwargs):
        cellBgColor = colorList[colorIndex]
        s = str(cellDatum)
        d = {'text':s[:cropLimit],'cellBgColor':cellBgColor}
        if len(s)>cropLimit:
            import math
            charsPerSet =2
            d['data_content'] = ' '.join([s[charsPerSet*i:charsPerSet*(i+1)] for i in range(int(math.ceil(len(s)/(charsPerSet*1.0))))])
            
        return d
    
    def asf_formatFunc_col_negative1(cellDatum,cropLimit,**kwargs):
        cellBgColor = '#55FF55' if cellDatum==True else '#FF0000'
        cellDatum   =    'PASS' if cellDatum==True else 'FAIL'
        return {'text':str(cellDatum)[:cropLimit],'cellBgColor':cellBgColor}
        

    formatFuncList = []
    for i in range(len(testRunData[0])):
        formatFuncList.append(asf_defaultFormatFunc)
    
    formatFuncList[-1] = asf_formatFunc_col_negative1
        
    cropLimitList = [12,15,15,15,20,20,15,4]
    cellWidthList = [(item+4)*10 for item in cropLimitList]
    
    gridData = gridFormattingSequencer(testRunData,formatFuncList,cropLimitList,lambda s: {'colorIndex':0})
    ############
    
    
    
    
    ######################
    testRunHeaderRow = ['SN','Site ID','Station ID','Sequence ID','Start Timestamp','End Timestamp','Last Test','isPass']

    hc = { 
          'top':      {'d':100,'legendList':testRunHeaderRow, 'className':'header'},
          'bottom':   {'d':10,'legendList':[],        'className':'header'},
          'left':     {'d':10,'legendList':[],        'className':'header'},
          'right':    {'d':10,'legendList':[],        'className':'header'},
         }
    
    gcd = {}
    gcd['data'] = flatten(gridData)
    gcd['cellsX'] = len(testRunData[0])
    gcd['cellsY'] = len(gcd['data'])/  gcd['cellsX']
    gcd['cellWidthList'] = cellWidthList
    gcd['cellHeight'] = 36
    gcd['headerConfig'] = hc
       
    gcdL.append(gcd)
    
    ##################
    
    
    
    
    s = 'SELECT testName,testMeasurementName,stringMin,stringMeasurement,stringMax,isPass'
    s+= '\n FROM TestMeasurement'
    s+= '\n WHERE testRunID = %s'
    v = [testRunID]
    testMeasurementTable,testMeasurementHeaderRow = dataMiningApi.sql.quickSqlRead(s,v,True)
    
    if testMeasurementTable==None or len (testMeasurementTable)==0:
        testMeasurementColumns = 0
    else:
        testMeasurementColumns = len(testMeasurementTable[0])
    
    ############
    
    
    def asf_rowFunction(row):
        if asf_rowFunction.testName != row[0]:
            asf_rowFunction.testName = row[0]
            asf_rowFunction.colorIndex = (asf_rowFunction.colorIndex+1)%2
        return {'colorIndex':asf_rowFunction.colorIndex}
    asf_rowFunction.testName = None
    asf_rowFunction.colorIndex = 1
    

    formatFuncList = []
    for i in range(len(testMeasurementTable[0])):
        formatFuncList.append(asf_defaultFormatFunc)
    
    formatFuncList[-1] = asf_formatFunc_col_negative1
        
    cropLimitList = [ 30,40,10,10,10,4]
    cellWidthList = [(item+4)*10 for item in cropLimitList]
    
    gridData = gridFormattingSequencer(testMeasurementTable,formatFuncList,cropLimitList,asf_rowFunction)
    ############
    
    
    
    
    ######################
    testMeasurementHeaderRow = ['Test Name','Test Measurement','Min','Meas','Max','isPass']

    hc = { 
          'top':      {'d':100,'legendList':testMeasurementHeaderRow, 'className':'header'},
          'bottom':   {'d':10,'legendList':[],        'className':'header'},
          'left':     {'d':10,'legendList':[],        'className':'header'},
          'right':    {'d':10,'legendList':[],        'className':'header'},
         }
    
    gcd = {}
    gcd['data'] = flatten(gridData)
    gcd['cellsX'] = testMeasurementColumns
    gcd['cellsY'] = len(gcd['data'])/  gcd['cellsX']
    gcd['cellWidthList'] = cellWidthList
    gcd['cellHeight'] = 36
    gcd['headerConfig'] = hc
       
    gcdL.append(gcd)
    
    ##################
    
    def asf_getKeys(tableName):
        s = 'SELECT key'
        s+= '\n FROM %s' % tableName
        s+= '\n WHERE testRunID = %s;'
        v = [testRunID]
        IDlist = dataMiningApi.sql.quickSqlRead(s,v,False)
        IDlist = [item[0] for item in IDlist]
        return IDlist
    
    
    storage = []
    storage.append (['file', asf_getKeys('FileDictionary')])
    storage.append (['string', asf_getKeys('StringDictionary')])
    storage.append (['numeric', asf_getKeys('DoubleDictionary')])
    storage.append (['component', asf_getKeys('Components')])
    
    responseDict = {}
    responseDict['gridConfigAndData_json'] = json.dumps(gcdL)
    responseDict['bodyBgColor'] = '#F1F1F1'
    responseDict['title'] = 'Test Measurements'
    
    responseDict['storage'] = storage
    responseDict['mtnID'] = mtnID
    responseDict['testRunID'] = testRunID
    
    return render_to_response('TestMeasurementListing.html',responseDict,context_instance=RequestContext(request))


@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))    
def dictionaryView(request):
    
    t = mtnPermissionCheck(request)
    if t['mtnID']==None:
        return t['HttpResponse']
    mtnID = t['mtnID']
   
    
    typeID = request.GET.get('typeID',None)
    typeID_translationDict = {'file':'FileDictionary','string':'StringDictionary','numeric':'DoubleDictionary','component':'Components'}
    tableName = typeID_translationDict.get(typeID,None)
    if tableName==None:
        return HttpResponse('<HTML><BODY><h2>%s</h2></BODY></HTML>' % 'Error p02')
    
    testRunID = request.GET.get('testRunID',None)
    itemID = request.GET.get('itemID',None)

    dataMiningApi = DataMiningApi(settings.DATAMINING_CONFIG[  settings.MTN_DICT[mtnID]['dbConfigID']  ])
   
    s = 'SELECT value from %s' % tableName
    s+= '\n WHERE testRunID=%s'
    s+= '\n AND key=%s;'
    v = [testRunID,itemID]
    data = dataMiningApi.sql.quickSqlRead(s,v)
    
    if len(data)==0:
        return HttpResponse('<h2>Could not find the requested data</h2>')
    
    data = data[0][0]
    if typeID=='file':
        data = pUtils.pUnpack(data)
    
    from django.utils.html import escape
    return HttpResponse(escape(sanitizeText(data)).replace('\n','<br>'))


@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))    
def searchUnitTestDataView(request):
    responseDict = {}
    responseDict['comboBoxData'] = []
    
    for mtnID in generate_mtnID_validList(request):
        responseDict['comboBoxData'].append({'text':mtnID,'value':mtnID})
    
    return render_to_response('SearchUnitTestData.html',responseDict,context_instance=RequestContext(request))

@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def indexView(request):
    responseDict = {}
    return render_to_response('index.html',responseDict,context_instance=RequestContext(request))


@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def stationStatusView(request):

    t = mtnPermissionCheck(request)
    if t['mtnID']==None:
        return t['HttpResponse']
    mtnID = t['mtnID']
    
    offset = request.GET.get('offset',0)
    
    s = ''
    v = []
    try:    
        dataMiningApi = DataMiningApi(settings.DATAMINING_CONFIG['msite_var'])
        s = 'SELECT creationTimestamp,value from GenericDictionary'
        s+= '\n WHERE key=%s'
        s+= '\n ORDER BY creationTimestamp DESC LIMIT 1 OFFSET %s;'
        v = ['stationStatus_'+mtnID,offset]
        data = dataMiningApi.sql.quickSqlRead(s,v)
        lastUpdated = data[0][0]
        dataIn = json.loads(data[0][1])
    except Exception , e:
        logger.error('stationStatusExcepted:'+str(e)+'\n '+s+'\n '+str(v))
        return HttpResponse('<HTML><BODY>%s</BODY></HTML>' % 'The requested data is unavailable')
        
    
    try:  
        ###
        moduleNameList = ['MTP','nyp','tools']
        ###
        
        
        ###
        moduleList = dataIn['data'][0]['taskArgDict']['moduleList']
        expectedSha1 = {}
        for entry in moduleList:
            expectedSha1[entry['name']] = entry['sha1']
        ###
        
        gridData = []
        for entry in dataIn['data']:
            rowData = []
            gridData.append(rowData)
            
            isOnline = True
            try:
                stationName = entry['taskArgDict']['host'].split('.')[0]
            except:
                stationName = None
                isOnline = False
                
            stationName_text = 'undefined' if stationName==None else stationName
            rowData.append({'text':stationName_text})
            
            for moduleName in moduleNameList:
                try:
                    module_sha1    = entry['taskReturnData']['data'][moduleName]['status']['sha1']
                    module_isClean = entry['taskReturnData']['data'][moduleName]['status']['isClean']
                except:
                    module_sha1    = None
                    module_isClean = None
                    isOnline = False
                
                if  module_isClean==True:
                    module_isClean_text = 'YES'
                    module_isClean_cellBgColor = '#00FF00'
                elif module_isClean==False:
                    module_isClean_text = 'NO'
                    module_isClean_cellBgColor = '#FFFF00'
                    #diffData = 
                else:
                    module_isClean_text = 'undefined'
                    module_isClean_cellBgColor = '#FF0000'
                
                
                if  module_sha1==expectedSha1[moduleName]:
                    module_sha1_cellBgColor = '#00FF00'
                elif module_sha1==None:
                    module_sha1_cellBgColor = '#FF0000'
                else:
                    module_sha1_cellBgColor = '#FFFF00'
                module_sha1_text = 'undefined' if module_sha1==None else module_sha1[:10]
                    
                rowData.append({'text':module_sha1_text   ,'cellBgColor':module_sha1_cellBgColor})
                isCleanDict = {'text':module_isClean_text,'cellBgColor':module_isClean_cellBgColor}
                #if module_isClean==False: isCleanDict['href'] = reverse(devView)+'?datum='+str(diffData)
                rowData.append(isCleanDict)
        
            [item for item in rowData if item['text']=='undefined']
            rowData[0]['cellBgColor'] = '#00FF00' if isOnline else '#FF0000'
            
        headerConfig = { 
            'top':      {'d':100,'legendList':['Station','MTP-sha1','isClean','nyp-sha1','isClean','tools-sha1','isClean'],'className':'header'},
            'bottom':   {'d':10,'legendList':[],        'className':'header'},
            'left':     {'d':10,'legendList':[],        'className':'header'},
            'right':    {'d':10,'legendList':[],        'className':'header'},
        }
    
        
        
        gcd = {}
        gcd['data'] = [item  for entry in gridData for item in entry]
        gcd['cellsX'] = 7
        gcd['cellsY'] = len(gcd['data'])/  gcd['cellsX']
        gcd['cellWidthList'] = [200,160,100,160,100,160,100]
        gcd['cellHeight'] = 36
        gcd['cellClassName'] = 'cell'
        gcd['datumClassName'] = 'datum'
        gcd['headerConfig'] = headerConfig
           
          
        
        responseDict = {}
        
        responseDict['comboBoxData'] = []
        for item_mtnID in generate_mtnID_validList(request):
            responseDict['comboBoxData'].append({'text':item_mtnID,'value':item_mtnID})
        
        responseDict['mtnID'] = mtnID
        responseDict['offset'] = offset
        responseDict['gridConfigAndData_json'] = json.dumps(gcd)
        responseDict['bodyBgColor'] = '#F1F1F1'
        responseDict['title'] = 'Station Status'
        responseDict['lastUpdated'] = pUtils.dateTimeToString(lastUpdated)
        
    except Exception,e:
        logger.error('stationStatusException2:'+str(e))
        
        responseDict = {}
        
        responseDict['comboBoxData'] = []
        for item_mtnID in generate_mtnID_validList(request):
            responseDict['comboBoxData'].append({'text':item_mtnID,'value':item_mtnID})
        
        responseDict['mtnID'] = mtnID
        responseDict['offset'] = offset
        responseDict['bodyBgColor'] = '#F1F1F1'
        responseDict['title'] = 'Station Status'
        responseDict['lastUpdated'] = pUtils.dateTimeToString(lastUpdated)
        responseDict['data'] = 'The specified MTN ('+mtnID+') was down during the last check ('+pUtils.dateTimeToString(lastUpdated)+')'
        
        #Dev's view
        if request.user.is_superuser:
            responseDict['data'] = data[0][1]
        
        
        return render_to_response('StationStatus_fail.html',responseDict,context_instance=RequestContext(request))
    
    return render_to_response('StationStatus.html',responseDict,context_instance=RequestContext(request))

   


@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def displayView(request): 
    datum = request.GET.get('datum','No datumto display')   
    responseDict = {}
    return HttpResponse('<h2>%s</h2>'% datum)


@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def failureTrendView(request):

    t = mtnPermissionCheck(request)
    if t['mtnID']==None:
        return t['HttpResponse']
    mtnID = t['mtnID']
    
    startRange = request.GET.get('startRange',None)
    endRange = request.GET.get('endRange',None)
    testSequenceID = request.GET.get('testSequenceID',None)
    testName = request.GET.get('testName',None)
    interval = request.GET.get('interval',None)
    displayTimeZone = request.GET.get('displayTimeZone',None)
    
    
    requestParamDict = {}
    requestParamDict['startRange'] = startRange
    requestParamDict['endRange'] = endRange
    requestParamDict['testSequenceID'] = testSequenceID
    requestParamDict['testName'] = testName
    requestParamDict['interval'] = interval
    requestParamDict['displayTimeZone'] = displayTimeZone
    
    
    
    #if (startRange==None or
    #    endRange==None or
    #    testSequenceID==None or
    #    testName==None or
    #    interval==None):
    #    return HttpResponse('Missing arguments')
    #
    
 
    tableData = getFailureTrendData(mtnID,
                                    startRange=startRange,
                                    endRange=endRange,
                                    testSequenceID=testSequenceID,
                                    testName=testName,
                                    interval=interval,
                                    displayTimeZone=displayTimeZone) ['data']
    
    
    def asf_formatData(tableData,columnIndex):
    
        ###   Formatting data for template   ###
        d4 = {'left':50,'top':10,'right':0,'bottom':50}
        customRange = range_datetime(justifyTimestamp(startRange,interval),endRange,interval)
        
        data = {}
        data['barWidth'] = 60
        data['barGap'] =  10
        data['barChartWidth'] = (data['barWidth']+data['barGap'])*len(customRange)+d4['left']+d4['right']
        data['barChartHeight'] = 300+d4['top']+d4['bottom']
        data['d4'] = d4
        
           ###   Start of barInstanceData section   ###
        data['barInstanceData'] = []
        
        index = 0
        maxValue = 0
        for entry in customRange:
            d = {}
            data['barInstanceData'].append(d)
                
            
            print '###################################'
            print   str(entry)
            
            if (index<len(tableData) and   
                tableData[index][0]==entry):
            
                print '###################################'
                print str(tableData[index][0])+'  '+str(entry)
            
            
                d['value'] = tableData[index][columnIndex]
                if d['value']==None:d['value'] = 0
                index+=1
            else:
                d['value'] = 0
            
            d['label'] = '%02i'%entry.day
            d['barColor'] = "#2A17B1"
            if d['value'] > maxValue:
                maxValue = d['value']
            
        
        
                
        data['barMaxValue'] = maxValue    
            
            #d['barColor'] = "#FF0000"
            
        if len(tableData)!=index:
            return {'retCode':1,'errMsg':'Resulting index missmatch with tableData length','debug':data}
        
        return {'retCode':0,'data':data}
           ###   End of barInstanceData section   ###
    
    
    failureData = asf_formatData(tableData,1)['data']  ##TODO: add proper error handle
    totalData   = asf_formatData(tableData,2)['data']
    
    
    #print json.dumps(data,sort_keys=True,indent=4)
    #HttpResponse('<BR>\n'.join([str(item) for item in tableData]))
    
    
    ###   Preparing the response dict   ###
    responseDict = {}
    responseDict['failureData_json'] = json.dumps(failureData)
    responseDict['totalData_json'] = json.dumps(totalData)
    responseDict.update(requestParamDict)
    
    responseDict['comboBoxData_mtnID'] = []
    for item_mtnID in generate_mtnID_validList(request):
        responseDict['comboBoxData_mtnID'].append({'text':item_mtnID,'value':item_mtnID})
    
    responseDict['comboBoxData_interval'] = []
    #for item_interval in ['hour','day','week','month','year']:
    for item_interval in ['day']:
        responseDict['comboBoxData_interval'].append({'text':item_interval,'value':item_interval})
        
    return render_to_response('FailureTrend.html',responseDict,context_instance=RequestContext(request))

###################


###   Start of Candidates for DataMiningApi  ###

def getFailureTrendData(mtnID,**kwargs):

    v = {'UTC':'UTC'}
    v.update(kwargs)
    
    def asf_transformTZ (fieldName):
        return 'timezone(%(displayTimeZone)s,timezone(%(UTC)s,'+fieldName+'))'
     

    def asf_table(isTotal):
        s =    'SELECT COUNT(testRunID) ,date_trunc(%(interval)s,'+asf_transformTZ('endTimestamp')+')'
        #s =    'SELECT COUNT(testRunID) ,date_trunc(%(interval)s,'+'endTimestamp'+')' 
        s+= '\n FROM TestRun'
        s+= '\n WHERE testSequenceID=%(testSequenceID)s'
      
          
        if kwargs.get('startRange',None)!=None:
            s+= '\n AND '+asf_transformTZ('endTimestamp')+'>='+'%(startRange)s'
        if kwargs.get('endRange',None)!=None:
            s+= '\n AND '+asf_transformTZ('endTimestamp')+'<='+'%(endRange)s'

      
        if isTotal==False:
            s+= '\n AND isPass=false'
            s+= '\n AND lastTestEntered=%(testName)s'     
        s+= '\n GROUP BY date_trunc' 
        return s
    
    s = '   WITH '
    s+= '\n table_fail AS('
    s+= asf_table(isTotal=False)
    s+= '\n )'
    s+= ',table_total AS('
    s+= asf_table(isTotal=True)
    s+= '\n )'
    s+= '\n SELECT'
    s+= '\n  CASE WHEN table_fail.date_trunc IS NOT NULL'
    s+= '\n       THEN table_fail.date_trunc'
    s+= '\n       ELSE table_total.date_trunc' 
    s+= '\n  END AS date_trunc'
    s+= '\n  ,table_fail.count AS failCount'
    s+= '\n  ,table_total.count AS totalCount' 
    s+= '\n FROM table_fail' 
    s+= '\n FULL OUTER JOIN table_total'
    s+= '\n ON table_fail.date_trunc = table_total.date_trunc'
    s+= '\n ORDER BY date_trunc'
    s+= '\n ;'
    
    
    dataMiningApi = getDataMiningApi(mtnID)
    data,header = dataMiningApi.sql.quickSqlRead(s,v,True)
    
    return {'data':data,'header':header}
    
###   End of Candidates for DataMiningApi  ###
    


def mtnPermissionCheck(request):
    mtnID_validList = generate_mtnID_validList(request)
    mtnID = request.GET.get('mtnID',None)
    if mtnID not in mtnID_validList:
        return {'mtnID':None, 'HttpResponse':HttpResponse(
         '<HTML><BODY><h2>%s</h2></BODY></HTML>' %
         'The data for the MTN resource you are trying to access is not available.')}
    return {'mtnID':mtnID}

def generate_mtnID_validList(request):
    return ['AQS-CHINA-1_sys','AQS-CHINA-1_smt']


def gridFormattingSequencer(table,formatFuncList,cropLimitList,rowFunction=lambda s: {}):
    gridData = []
    for j in range(len(table)):
        row = table[j]
        gridRow = []
        gridData.append(gridRow)
        kwargs = rowFunction(row)
        for i in range(len(row)):
            cell = row[i]
            formatFunc = formatFuncList[i]
            cropLimit = cropLimitList[i]
            gridRow.append( formatFunc(cell,cropLimit,**kwargs) )    
    return gridData

def getDataMiningApi(mtnID):
    return DataMiningApi(settings.DATAMINING_CONFIG[  settings.MTN_DICT[mtnID]['dbConfigID']  ])

def sanitizeText(text):
    return ''.join([item for item in text if ord(item) in (range(32,127)+[10,13])])


def range_datetime(timestamp1,timestamp2,interval):
    if isinstance(timestamp1,str) or isinstance(timestamp1,unicode):
        timestamp1 = stringToDateTime(timestamp1) 
    if isinstance(timestamp2,str) or isinstance(timestamp2,unicode):
        timestamp2 = stringToDateTime(timestamp2)
    
          
    if interval=='hour':
        def asf_addInterval(i):
            return i + datetime.timedelta(hours=1)
    elif interval=='day':
        def asf_addInterval(i):
            return i + datetime.timedelta(days=1)
    elif interval=='week':
        def asf_addInterval(i):
            return i + datetime.timedelta(weeks=1)
    elif interval=='month':
        def asf_addInterval(i):
            i = i.replace(month=i.month+1)
            if i.month==1:  #Happy New Year!!
                i = i.replace(year=i.year+1)
            return i
    elif interval=='year':
        def asf_addInterval(i):
            return i.replace(year=i.year+1)
    else:
        raise Exception('Invalid Interval Keyword: '+str(interval))
    
    l = []
    i = timestamp1
    while i<=timestamp2:
        l.append(i)
        i = asf_addInterval(i)

    return l


def justifyTimestamp(timestamp,interval):
    if isinstance(timestamp,str) or isinstance(timestamp,unicode):
        timestamp = stringToDateTime(timestamp) 
    
          
    if interval=='hour':
        return timestamp.replace(minute=0,second=0,microsecond=0)
    elif interval=='day':
        return timestamp.replace(hour=0,minute=0,second=0,microsecond=0)
    elif interval=='week':
        return (timestamp-datetime.timedelta(days=(timestamp.isocalendar()[2]-1))).replace(hour=0,minute=0,second=0,microsecond=0)
    
    
    elif interval=='month':
        return timestamp
    elif interval=='year':
        return timestamp
    else:
        raise Exception('Invalid Interval Keyword: '+str(interval))
       

###   From pUtils   ###    
def stringToDateTime(string):
    patternList = [
        '%Y%m%d-%H%M%S',
        '%Y-%m-%d %H:%M:%S',
        
        ###mods here###
        '%Y%m%d',
        '%Y-%m-%d',
        ###############
        ]

    for pattern in patternList:
        try:
            obj = datetime.datetime.strptime(string,pattern)
            return obj
        except:
            pass
    raise Exception('Unrecognized dateTime format: '+string)

    