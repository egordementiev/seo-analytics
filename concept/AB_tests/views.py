import datetime
import os
import shutil
import datetime
from datetime import timedelta
from urllib.parse import urlparse

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from .HelpPackages.google_search_api import extract_data, get_graphic_from_data, get_data_from_date_to_date
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
            form.save()
            form = AddABTest(user)
            message = 'Test added successfully'
            return render(request, 'AB_tests/create_ab_test.html', {'form': form, 'message': message})

    form = AddABTest(user)
    return render(request, 'AB_tests/create_ab_test.html', {'form': form})


@login_required(login_url='/auth/login/')
def delete_ab_test(request):
    user = request.user
    if request.method == "POST":
        print('request.method = POST ')
        form = DeleteABTest(user, request.POST)
        if form.is_valid():
            print('form is valid')
            form.save(commit=False)
            ab_test = form.cleaned_data.get('ABTest')
            print(f'ab_test = {ab_test}')
            ab_test.delete()
            message = 'ab_test successfully deleted'
            return render(request, 'AB_tests/delete_ab_test.html', {'form': form, 'message': message})
        print('form is not valid')

    print('request.method = GET ')
    form = DeleteABTest(user)
    return render(request, 'AB_tests/delete_ab_test.html', {'form': form})


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
        if form.is_valid():
            site = form.save(commit=False)
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


@login_required(login_url='/auth/login/')
def site_info(request, site_id):
    sites = Site.objects.filter(pk=site_id)
    if sites and request.user in sites[0].users.all():
        tests = ABTest.objects.filter(site=sites[0]).filter(result=None)
        for test in tests:
            if test.start_group_a_date + timedelta(days=28) < datetime.date.today() \
                    and test.start_group_b_date + timedelta(days=28) < datetime.date.today():
                data_group_a_before = get_data_from_date_to_date(sites[0].domain,
                                                                 test.start_group_a_date - timedelta(days=28),
                                                                 test.start_group_a_date)
                data_group_a_after = get_data_from_date_to_date(sites[0].domain, test.start_group_a_date,
                                                                test.start_group_a_date + timedelta(days=28))
                data_group_b_before = get_data_from_date_to_date(sites[0].domain,
                                                                 test.start_group_b_date - timedelta(days=28),
                                                                 test.start_group_b_date)
                data_group_b_after = get_data_from_date_to_date(sites[0].domain, test.start_group_b_date,
                                                                test.start_group_b_date + timedelta(days=28))

                print(f'data_group_a_before = {data_group_a_before}')
                print(f'data_group_a_after = {data_group_a_after}')
                print(f'data_group_b_before = {data_group_b_before}')
                print(f'data_group_b_after = {data_group_b_after}')
                if data_group_a_before is None or data_group_a_after is None \
                        or data_group_b_before is None or data_group_b_after is None:
                    test.delete()
                    continue

                data_group_a_before_int = 0
                for clicks in data_group_a_before.get('clicks'):
                    data_group_a_before_int += int(clicks)

                data_group_a_after_int = 0
                for clicks in data_group_a_after.get('clicks'):
                    data_group_a_after_int += int(clicks)

                data_group_b_before_int = 0
                for clicks in data_group_b_before.get('clicks'):
                    data_group_b_before_int += int(clicks)

                data_group_b_after_int = 0
                for clicks in data_group_b_after.get('clicks'):
                    data_group_b_after_int += int(clicks)

                before_result = data_group_b_before_int / data_group_a_before_int
                after_result = data_group_b_after_int / data_group_a_after_int

                result = (after_result - before_result) * 100
                print(f'result = {result}')
                test.result = result
                test.save()

        tests = ABTest.objects.filter(site=sites[0])
        print(f'tests = {tests}')
        return render(request, 'AB_tests/site_info.html', {'site': sites[0], 'tests': tests})
    return render(request, 'AB_tests/site_info.html')
