from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.VendAuthLogin.as_view(),
        name='vend_auth_login'),
    url(r'^complete/$', views.VendAuthComplete.as_view(),
        name='vend_auth_complete'),
    url(r'^select-user/$', views.VendAuthSelectUser.as_view(),
        name='vend_auth_select_user'),
]
