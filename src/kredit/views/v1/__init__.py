from django.conf.urls import url, include
from . import application, request, filters


urlpatterns = [
    url(r'^application/', include(application.urlpatterns)),
    url(r'^filters/', include(filters.urlpatterns)),

]