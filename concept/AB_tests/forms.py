from django import forms

from .models import Site, SiteAdmins


class AddSiteForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = ('domain',)


class DelSiteForm(forms.Form):
    domain = forms.Select()


class AddAdminToSite(forms.Form):

    class Meta:
        model = SiteAdmins
        fields = ('user', 'site',)


class DelAdminsFromSite(forms.Form):
    site = forms.Select()
    email = forms.SelectMultiple()


class AddABTest(forms.Form):
    title = forms.TextInput()
    description = forms.Textarea()
    site = forms.Select()
    start_group_a_date = forms.DateField
    start_group_b_date = forms.DateField

