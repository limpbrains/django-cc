from django.conf.urls import url

import cc.views as views


urlpatterns = [
    url(r'^blocknotify/$', views.blocknotify, name='cc-blocknotify'),
    url(r'^walletnotify/$', views.walletnotify, name='cc-walletnotify'),
]
