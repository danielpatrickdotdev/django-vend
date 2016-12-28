from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.RegisterList.as_view(),
        name='vend_register_list'),
]
