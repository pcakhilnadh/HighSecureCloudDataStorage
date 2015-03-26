from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^$', 'cloud.views.home', name='home'),
    url(r'^register/$', 'cloud.views.register', name='register'),
    url(r'^ulogin/$', 'cloud.views.ulogin', name='ulogin'),
    url(r'^forgot_password/$', 'cloud.views.forgot_password', name='forgot_password'),
    url(r'^ulogin/(?P<user>.*)/otp$', 'cloud.views.otp', name='otp'),
    url(r'^ulogout/$', 'cloud.views.ulogout', name='ulogout'),
    url(r'^profile/$', 'cloud.views.profile', name='profile'),
    url(r'^settings/$','cloud.views.setting', name='settings',) ,
    url(r'^dashboard/$','cloud.views.dashboard', name='dashboard') ,
    url(r'^dashboard/search/$','cloud.views.dashboardSearch', name='dashboardSearch') ,
    url(r'^dashboard/upload/$','cloud.views.dashboardUpload', name='dashboardUpload') ,
    url(r'^dashboard/share/$','cloud.views.dashboardShare', name='dashboardShare') ,
    url(r'^dashboard/incoming/$','cloud.views.dashboardIncoming', name='dashboardIncoming') ,
    url(r'^dashboard/viewFile/$','cloud.views.dashboardViewFile', name='dashboardViewFile') ,
    url(r'^download/$','cloud.views.download', name='download',) ,
    url(r'^addSystem/$','cloud.views.addSystem', name='addSystem',) ,
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/(?P<path>.*)$', 'django.views.static.serve',{'document_root':settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^settings/(?P<path>.*)$', 'django.views.static.serve',{'document_root':settings.MEDIA_ROOT, 'show_indexes': True}),
    
)
