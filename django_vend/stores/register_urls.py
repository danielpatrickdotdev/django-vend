from django.conf.urls import url

from django_vend.core.utils import UUID_REGEX

from . import views

urlpatterns = [
    url(r'^$', views.RegisterList.as_view(),
        name='vend_register_list'),
    url(r'^(?P<uid>{})/$'.format(UUID_REGEX), views.RegisterDetail.as_view(),
        name='vend_register_detail'),
]
