from django.conf.urls import url, include
from django.urls import path
from . import views


urlpatterns = [
    #path(r'^api/', include(('nubip.urlpatterns', 'nubip'), namespace='nubip')),
    url(r'^api/', include(views.urlpatterns)),
]
