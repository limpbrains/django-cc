from __future__ import absolute_import

from django import forms

from .models import Wallet

class WalletAdminForm(forms.ModelForm):
    class Meta:
        model = Wallet
        exclude = []

    def clean_label(self):
        return self.cleaned_data['label'] or None
