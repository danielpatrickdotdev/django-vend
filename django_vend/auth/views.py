from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

import requests
from oauthlib.common import generate_token

from .models import VendRetailer, VendUser, VendProfile
from .forms import VendProfileSelectVendUsersForm


class OAuth2Mixin(object):

    def get_param_or_error(self, param_name, dict_obj=None):
        if not dict_obj:
            dict_obj = self.request.GET
        param = dict_obj.get(param_name)
        if not param:
            raise SuspiciousOperation('OAuth2 failure')
        return param


class VendAuthLogin(LoginRequiredMixin, RedirectView):

    http_method_names = ['get']
    permanent = False
    query_string = False
    url = ('https://secure.vendhq.com/connect?response_type=code'
           '&client_id={}'
           '&redirect_uri={}'
           '&state={}'
    )

    def get_redirect_url(self, *args, **kwargs):
        client_id = getattr(settings, "VEND_KEY", None)
        if not client_id:
            raise ImproperlyConfigured('django setting VEND_KEY is required')

        redirect_uri = self.request.build_absolute_uri(
            reverse('vend_auth_complete'))
        state = self.create_state()

        return self.url.format(client_id, redirect_uri, state)

    def create_state(self):
        state = generate_token()
        self.request.session['vend_state'] = state
        return state


class VendAuthComplete(LoginRequiredMixin, RedirectView, OAuth2Mixin):

    VEND_TOKEN_URL = 'https://{}.vendhq.com/api/1.0/token'
    http_method_names = ['get']
    permanent = False
    query_string = False

    def get_setting_or_error(self, setting):
        try:
            result = getattr(settings, setting)
        except AttributeError:
            raise ImproperlyConfigured(
                'django setting {} is required'.format(setting))
        return result

    def get_redirect_url(self, *args, **kwargs):
        name = self.get_param_or_error('domain_prefix')
        code = self.get_param_or_error('code')
        user_id = self.get_param_or_error('user_id')
        returned_state = self.get_param_or_error('state')

        session_state = self.request.session.get('vend_state')
        if returned_state != session_state:
            raise SuspiciousOperation('OAuth2 failure')

        url = self.VEND_TOKEN_URL.format(name)
        client_id = self.get_setting_or_error('VEND_KEY')
        client_secret = self.get_setting_or_error('VEND_SECRET')
        redirect_uri = self.request.build_absolute_uri(
            reverse('vend_auth_complete'))

        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        r = requests.post(url, data=data)

        try:
            data = r.json()
        except ValueError:
            raise SuspiciousOperation('OAuth2 failure')
        access_token = self.get_param_or_error('access_token', data)
        token_type = self.get_param_or_error('token_type', data)
        if token_type != 'Bearer':
            raise SuspiciousOperation('OAuth2 failure')
        expires = self.get_param_or_error('expires', data)
        expires_in = self.get_param_or_error('expires_in', data)
        refresh_token = self.get_param_or_error('refresh_token', data)

        retailer, created = VendRetailer.objects.update_or_create(
            name=name,
            defaults={
                'access_token': access_token,
                'expires': datetime.fromtimestamp(expires),
                'expires_in': expires_in,
                'refresh_token': refresh_token,
            },
        )
        VendProfile.objects.update_or_create(
            user=self.request.user,
            defaults={'retailer':retailer},
        )
        self.request.session['retailer_id'] = retailer.pk

        return self.request.build_absolute_uri(
            reverse('vend_profile_select_vend_users'))


class VendProfileSelectVendUsers(LoginRequiredMixin, UpdateView):

    form_class = VendProfileSelectVendUsersForm
    template_name_suffix = '_update_vendusers'
    success_url = reverse_lazy('vend_profile_select_vend_users')

    def get_object(self):
        return VendProfile.objects.get(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(VendProfileSelectVendUsers, self).get_form_kwargs()
        kwargs['retailer_id'] = self.request.user.vendprofile.retailer.pk
        return kwargs


class VendAuthVendUserListSelect(LoginRequiredMixin, TemplateView):

    model = VendUser
    template_name = 'vend_auth/venduser_list_select.html'
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return self.model.objects.filter(
            vendprofiles=self.request.user.vendprofile)

    def get_context_data(self, *args, **kwargs):
        self.model.objects.synchronise(self.request.user.vendprofile.retailer)
        return {'object_list': self.get_queryset()}

    def post(self, request, *args, **kwargs):
        pk = request.POST.get("venduser_id")
        if not pk:
            raise SuspiciousOperation('No VendUser pk supplied in POST')

        try:
            vu = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404(
                'VendUser id {} not found for logged in User'.format(
                    self.object.pk))

        request.session['venduser_id'] = pk
        return HttpResponseRedirect(reverse('vend_auth_select_vend_user'))
