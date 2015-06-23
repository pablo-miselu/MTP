from django.conf.urls import  patterns, url,include

urlpatterns = patterns('',
    url(r'^$', 'DataMining.views.indexView'),
    url(r'^yields/$', 'DataMining.views.yieldsView'),
    url(r'^stationStatus/$', 'DataMining.views.stationStatusView'),
    url(r'^searchUnitTestData/$', 'DataMining.views.searchUnitTestDataView'),
    url(r'^testRun/$', 'DataMining.views.testRunView'),
    url(r'^testMeasurement/$', 'DataMining.views.testMeasurementView'),
    url(r'^testRunInfo/$', 'DataMining.views.dictionaryView'),

    url(r'^failureTrend/$', 'DataMining.views.failureTrendView'),
)
