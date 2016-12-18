from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='vend_auth_login'),
    url(r'^complete/$', views.complete, name='vend_auth_complete'),
    url(r'^select-user/$', views.select_user, name='vend_auth_select_user'),
]
