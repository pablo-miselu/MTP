#standardApp

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       
    url(r'^login/$', 'standardApp.views_login.loginView'),
    url(r'^logout/$', 'standardApp.views_login.logout_view'),
    url(r'^permissionDenied/$', 'standardApp.views_login.permissionDenied'),
)
