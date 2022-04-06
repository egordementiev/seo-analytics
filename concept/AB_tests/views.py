import datetime
import os
import shutil
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
    return render(request, 'AB_tests/base_ab_test.html')


@login_required(login_url='/auth/login/')
def delete_admin_from_site(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DeleteUserFromSiteForm(user, request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=False)
            email = form.cleaned_data.get('email')
            site = form.cleaned_data.get('site')
            email_list = [email]
            users_for_delete = User.objects.filter(email__in=email_list)
            print(f'users = {users_for_delete}')

            if not users_for_delete:
                message = 'user didn\'t found'
                form = DeleteUserFromSiteForm(user)
                return render(request, 'AB_tests/delete_admin_from_site.html', {'form': form, 'message': message})

            for user_for_delete in users_for_delete:
                print(f'site.users.all() = {site.users.all()}')
                if user_for_delete in site.users.all():
                    site.users.remove(user_for_delete)
                    message = 'admin successfully deleted'
                    break
                else:
                    message = 'error, user didn\'t be the site admin'
            form = DeleteUserFromSiteForm(user)
            return render(request, 'AB_tests/delete_admin_from_site.html', {'form': form, 'message': message})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = DeleteUserFromSiteForm(user)
        # form.fields['site'].widget.choices.extend([('site 3', 'site 3')])
    return render(request, 'AB_tests/delete_admin_from_site.html', {'form': form})


@login_required(login_url='/auth/login/')
def add_admin_to_site(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddUserToSiteForm(user, request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=False)
            email = form.cleaned_data.get('email')
            site = form.cleaned_data.get('site')
            email_list = [email]
            for user_to in User.objects.filter(email__in=email_list):
                site.users.add(user_to)
                if True:
                    message = 'admin successfully added'
                    break
            else:
                message = 'user didn\'t found'
            form = AddUserToSiteForm(user)
            return render(request, 'AB_tests/add_admin_to_site.html', {'form': form, 'message': message})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddUserToSiteForm(user)
    return render(request, 'AB_tests/add_admin_to_site.html', {'form': form})


@login_required(login_url='/auth/login/')
def create_ab_test(request):
    user = request.user
    if request.method == 'POST':
        print('request = POST')
        form = AddABTest(user, request.POST)
        if form.is_valid():
            form.save(commit=False)
            # title = form.cleaned_data.get('title')
            # description = form.cleaned_data.get('site')
            site = form.cleaned_data.get('site')
            form.save()

    form = AddABTest(user)
    return render(request, 'AB_tests/create_ab_test.html', {'form': form})


@login_required(login_url='/auth/login/')
def finish_ab_test(request):
    return render(request, 'AB_tests/finish_ab_test.html')


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
            data = extract_data(site.domain, 365)
            graphic_plt = get_graphic_from_data(data)
            if not os.path.exists(f'{domain}'):
                os.mkdir(f'{domain}')

            graphic_plt.savefig(f'{domain}/graphic.jpg')
            site.graphic = f'{domain}/graphic.jpg'
            site.graphic_last_update = datetime.date.today()
            site.save()
            site.users.add(request.user)
            site.save()

    form = AddSiteForm()
    return render(request, 'AB_tests/add_site.html', {'form': form})


@login_required(login_url='/auth/login/')
def delete_site(request):

    # Get Domain Name to Delete a Project
    def get_domain_name(start_url):
        domain_name = '{uri.netloc}'.format(uri=urlparse(start_url))  # Get Domain Name To Name Project
        domain_name = domain_name.replace('.', '_')
        return domain_name

    user = request.user

    if request.method == "POST":
        print('post')
        form = DelSiteForm(user, request.POST)
        if form.is_valid:
            form.save(commit=False)
            site = form.cleaned_data.get('site')
            domain = get_domain_name(site.domain)
            if os.path.exists(f'{domain}'):
                shutil.rmtree(f'{domain}')
            site.delete()
            message = 'site successfully deleted'
            return render(request, 'AB_tests/delete_site.html', {'form': form, 'message': message})

    form = DelSiteForm(user)
    return render(request, 'AB_tests/delete_site.html', {'form': form})


@login_required(login_url='/auth/login/')
def my_sites(request):
    user = request.user
    sites = user.sites.all()
    return render(request, 'AB_tests/my_sites.html', {'sites': sites})


