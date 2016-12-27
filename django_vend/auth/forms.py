from django import forms
from django.conf import settings

from .models import VendProfile, VendUser


class VendProfileSelectVendUsersForm(forms.ModelForm):
    class Meta:
        model = VendProfile
        fields = ['vendusers']

    def __init__(self, retailer_id, *args, **kwargs):
        super(VendProfileSelectVendUsersForm, self).__init__(*args, **kwargs)
        
        self.fields['vendusers'].queryset = VendUser.objects.filter(
            retailer__pk=retailer_id)
