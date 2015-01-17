from django.conf.urls import patterns, include, url

urlpatterns = patterns('cc.views',
    url(r'^blocknotify/$', 'blocknotify', name='cc-blocknotify'),
    url(r'^walletnotify/$', 'walletnotify', name='cc-walletnotify'),
)
