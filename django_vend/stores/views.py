from django.shortcuts import render
from django.views.generic import ListView, DetailView

from django_vend.core.views import (VendAuthSingleObjectSyncMixin,
                                    VendAuthCollectionSyncMixin)

from .models import VendOutlet, VendRegister


class RegisterList(VendAuthCollectionSyncMixin, ListView):
    model = VendRegister


class RegisterDetail(VendAuthSingleObjectSyncMixin, DetailView):
    model = VendRegister


class OutletList(VendAuthCollectionSyncMixin, ListView):
    model = VendOutlet


class OutletDetail(VendAuthSingleObjectSyncMixin, DetailView):
    model = VendOutlet
