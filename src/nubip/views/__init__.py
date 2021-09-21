from django.conf.urls import url, include

#from src.nubip.models import general
from . import v1
from .v1 import tables

urlpatterns = [
#    url(r'^', include(general.urlpatterns)),
    url(r'^v1/', include(v1.urlpatterns)),
    url('details/', tables.detail_view, name="details"),
]
