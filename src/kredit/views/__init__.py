from django.conf.urls import url, include

#from src.kredit.models import general
from . import v1

urlpatterns = [
#    url(r'^', include(general.urlpatterns)),
    url(r'^v1/', include(v1.urlpatterns))
]
