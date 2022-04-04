from django import forms

from .models import Site
from django.contrib.auth.models import User


class AddUserToSiteForm(forms.ModelForm):
    # site = forms.ChoiceField(choices=[(choice.pk, choice) for choice in Site.objects.all() if SiteAdmins.objects.get(site=choice)])
    # email = forms.EmailField()
    # site = forms.ChoiceField(choices=[Site.objects.filter(siteadmins__user_id=user) for user in User.objects.all()])
    #

    def __init__(self, user, *args, **kwargs):
        super(AddUserToSiteForm, self).__init__(*args, **kwargs)
        self.fields['site'] = forms.ModelChoiceField(queryset=Site.objects.filter(users=user))

    class Meta:
        model = User
        fields = ['email']


class AddSiteForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = ('domain',)


class DelSiteForm(forms.Form):
    domain = forms.Select()


class DelAdminsFromSite(forms.Form):
    site = forms.Select()
    email = forms.SelectMultiple()


class AddABTest(forms.Form):
    title = forms.TextInput()
    description = forms.Textarea()
    site = forms.Select()
    start_group_a_date = forms.DateField
    start_group_b_date = forms.DateField

