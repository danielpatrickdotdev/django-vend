from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.OutletList.as_view(),
        name='vend_outlet_list'),
]
