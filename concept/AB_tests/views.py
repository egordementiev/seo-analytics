import datetime
import os
from urllib.parse import urlparse

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from .HelpPackages.google_search_api import extract_data, get_graphic_from_data
from .models import Site


@login_required(login_url='/auth/login/')
def hello_world(request):
    user = request.user
    print([f.name for f in User._meta.get_fields()])
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddUserToSiteForm(user, request.POST)
        # form.fields['site'].widget.choices.extend([('site 3', 'site 3')])
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=False)
            email = form.cleaned_data.get('email')
            site = form.cleaned_data.get('site')
            email_list = [email]
            print(f'User.objects.filter(email__in=email) = {User.objects.filter(email__in=email_list)}')
            for user_to in User.objects.filter(email__in=email_list):
                print(f'user = {user_to}')
                site.users.add(user_to)
            # site = Site(users=User.objects.get(email=email), site=site)
            # site.save()
            # process the data in form.cleaned_data as required
            # ...
            # return html
            print(f'email = {email} / {email_list}')
            print(f'site = {site}')
            return HttpResponse('thanks')

    # if a GET (or any other method) we'll create a blank form
    else:

        form = AddUserToSiteForm(user)
        # form.fields['site'].widget.choices.extend([('site 3', 'site 3')])
    return render(request, 'AB_tests/add_admin_to_site.html', {'form': form})


@login_required(login_url='/auth/login/')
def add_admin_to_site(request):
    user = request.user
    print(user)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddAdminToSiteForm(request.POST)
        form.fields['site'].widget.choices.extend([('site 3', 'site 3')])
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # return html
            return HttpResponse('thanks')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddAdminToSiteForm()
        form.fields['site'].widget.choices.extend([('site 3', 'site 3')])
    return render(request, 'AB_tests/add_admin_to_site.html', {'form': form})


@login_required(login_url='/auth/login/')
def create_ab_test(request):
    return render(request, 'AB_tests/create_ab_test.html')


@login_required(login_url='/auth/login/')
def finish_ab_test(request):
    return render(request, 'AB_tests/finish_ab_test.html')


@login_required(login_url='/auth/login/')
def add_site_admin(request):
    form = AddAdminToSite()


@login_required(login_url='/auth/login/')
def add_site(request):

    # Get Domain Name to Create a Project
    def get_domain_name(start_url):
        domain_name = '{uri.netloc}'.format(uri=urlparse(start_url))  # Get Domain Name To Name Project
        domain_name = domain_name.replace('.', '_')
        return domain_name

    if request.method == "POST":
        print('post')
        form = AddSiteForm(request.POST)
        if form.is_valid:
            site = form.save(commit=False)
            domain = get_domain_name(site.domain)
            data = extract_data(site.domain, 7)
            graphic_plt = get_graphic_from_data(data)
            if not os.path.exists(f'{domain}'):
                os.mkdir(f'{domain}')

            graphic_plt.savefig(f'{domain}/graphic.jpg')
            site.graphic = f'{domain}/graphic.jpg'
            site.graphic_last_update = datetime.date.today()
            site.save()

            site_admin = SiteAdmins(user=request.user, site=site)
            site_admin.save()

    form = AddSiteForm()
    return render(request, 'AB_tests/add_site.html', {'form': form})

