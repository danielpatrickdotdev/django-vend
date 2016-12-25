from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.VendAuthLogin.as_view(),
        name='vend_auth_login'),
    url(r'^complete/$', views.VendAuthComplete.as_view(),
        name='vend_auth_complete'),
    url(r'^select-vend-users/$', views.VendProfileSelectVendUsers.as_view(),
        name='vend_profile_select_vend_users'),
]
