from django import forms

from .models import Site, ABTest
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


class DeleteUserFromSiteForm(forms.ModelForm):
    # site = forms.ChoiceField(choices=[(choice.pk, choice) for choice in Site.objects.all() if SiteAdmins.objects.get(site=choice)])
    # email = forms.EmailField()
    # site = forms.ChoiceField(choices=[Site.objects.filter(siteadmins__user_id=user) for user in User.objects.all()])
    #

    def __init__(self, user, *args, **kwargs):
        super(DeleteUserFromSiteForm, self).__init__(*args, **kwargs)
        self.fields['site'] = forms.ModelChoiceField(queryset=Site.objects.filter(users=user))

    class Meta:
        model = User
        fields = ['email']


class AddSiteForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = ('domain',)


class DelSiteForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(DelSiteForm, self).__init__(*args, **kwargs)
        self.fields['site'] = forms.ModelChoiceField(queryset=Site.objects.filter(users=user))

    class Meta:
        model = Site
        fields = []


class DelAdminsFromSite(forms.Form):
    site = forms.Select()
    email = forms.SelectMultiple()


class AddABTest(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(AddABTest, self).__init__(*args, **kwargs)
        self.fields['site'] = forms.ModelChoiceField(queryset=Site.objects.filter(users=user))
        self.fields['start_group_a_date'] = forms.DateField()
        self.fields['start_group_b_date'] = forms.DateField()

    class Meta:
        model = ABTest
        fields = '__all__'
        exclude = ['is_finished', 'result']

