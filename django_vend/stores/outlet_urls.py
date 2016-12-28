from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.OutletList.as_view(),
        name='vend_outlet_list'),
    url(r'^(?P<uid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.OutletDetail.as_view(),
        name='vend_outlet_detail'),
]
