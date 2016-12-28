from django.conf.urls import url

from django_vend.core.utils import UUID_REGEX

from . import views

urlpatterns = [
    url(r'^$', views.OutletList.as_view(),
        name='vend_outlet_list'),
    url(r'^(?P<uid>{})/$'.format(UUID_REGEX), views.OutletDetail.as_view(),
        name='vend_outlet_detail'),
]
