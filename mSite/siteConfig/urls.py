from django.conf.urls import  patterns, url,include

urlpatterns = patterns('',
    url(r'^s/', include('standardApp.urls') ),
    url(r'^', include('DataMining.urls') ),
)
