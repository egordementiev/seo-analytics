"""Wrote by Egor Dementiev, if you have problem, you can write me to email egor.dmnt@gmail.com"""

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
from .HelpPackages.google_search_api import extract_data, get_graphic_from_data,\
    get_clicks_from_date_to_date, extract_data_with_page_from_day_to_day
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
            # print(urls_control_group)
            # print(f'------------------')
            # print(urls_test_group)
            # index = 0
            # for url in urls_test_group:
            #     urls_test_group[index] = url.strip()
            #     index += 1
            #
            # index = 0
            # for url in urls_control_group:
            #     urls_control_group[index] = url.strip()
            #     index += 1
            #
            # print(f'urls_test_group_after_strip == {urls_test_group}')
            # print(f'urls_control_group_after_strip == {urls_control_group}')
            # test.set_urls_control_group = urls_control_group
            # test.set_urls_test_group = urls_test_group
            # print(test.get_urls_control_group())
            # print(test.get_urls_test_group())
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
    user = request.user

    if request.method == "POST":
        print('post')
        form = DelSiteForm(user, request.POST)
        if form.is_valid:
            form.save(commit=False)
            site = form.cleaned_data.get('site')
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
            if test.start_date + timedelta(days=28) < datetime.date.today():
                clicks_control_group_before = 0
                for page in test.get_urls_control_group():
                    print(f'1) {page}')
                    clicks = get_clicks_from_date_to_date(sites[0].domain, page,
                                                                               test.start_date - timedelta(days=28),
                                                                               test.start_date)
                    clicks_control_group_before += clicks if clicks else 0


                clicks_control_group_after = 0
                for page in test.get_urls_control_group():
                    print(f'2) {page}')
                    clicks = get_clicks_from_date_to_date(sites[0].domain, page,
                                                          test.start_date,
                                                          test.start_date + timedelta(days=28))
                    clicks_control_group_after += clicks if clicks else 0

                clicks_test_group_before = 0
                for page in test.get_urls_test_group():
                    print(f'3) {page}')
                    clicks = get_clicks_from_date_to_date(sites[0].domain, page,
                                                          test.start_date - timedelta(days=28),
                                                          test.start_date)
                    clicks_test_group_before += clicks if clicks else 0

                clicks_test_group_after = 0
                for page in test.get_urls_test_group():
                    print(f'4) {page}')
                    clicks = get_clicks_from_date_to_date(sites[0].domain, page,
                                                          test.start_date,
                                                          test.start_date + timedelta(days=28))
                    clicks_test_group_after += clicks if clicks else 0

                print(f'clicks_control_group_before = {clicks_control_group_before}')
                print(f'clicks_control_group_after = {clicks_control_group_after}')
                print(f'clicks_test_group_before = {clicks_test_group_before}')
                print(f'clicks_test_group_after = {clicks_test_group_after}')

                if clicks_control_group_before == 0 or clicks_control_group_before is None:
                    result_before = 1
                else:
                    result_before = clicks_test_group_before / clicks_control_group_before

                if clicks_control_group_after == 0 or clicks_control_group_after is None:
                    result_after = 1
                else:
                    result_after = clicks_test_group_after / clicks_control_group_after

                result = (result_after - result_before) * 100
                print(f'result = {result}')
                test.result = result
                test.save()

        tests = ABTest.objects.filter(site=sites[0])
        print(f'tests = {tests}')
        return render(request, 'AB_tests/site_info.html', {'site': sites[0], 'tests': tests})
    return render(request, 'AB_tests/site_info.html')


# @login_required(login_url='/auth/login/')
# def test_info(request, test_id):
#     tests = ABTest.objects.filter(pk=test_id)
#     if not tests or not request.user in tests[0].site.users.all():
#         return render(request, 'AB_tests/test_info.html')
#     if not tests[0].result:
#         if tests[0].start_date + timedelta(days=28) < datetime.date.today():
#             clicks_control_group_before = 0
#             for page in tests[0].get_urls_control_group():
#                 print(f'1) {page}')
#                 clicks = get_clicks_from_date_to_date(tests[0].site.domain, page,
#                                                                            tests[0].start_date - timedelta(days=28),
#                                                                            tests[0].start_date)
#                 clicks_control_group_before += clicks if clicks else 0
#
#             clicks_control_group_after = 0
#             for page in tests[0].get_urls_control_group():
#                 print(f'2) {page}')
#                 clicks = get_clicks_from_date_to_date(tests[0].site.domain, page,
#                                                       tests[0].start_date,
#                                                       tests[0].start_date + timedelta(days=28))
#                 clicks_control_group_after += clicks if clicks else 0
#
#             clicks_test_group_before = 0
#             for page in tests[0].get_urls_test_group():
#                 print(f'3) {page}')
#                 clicks = get_clicks_from_date_to_date(tests[0].site.domain, page,
#                                                       tests[0].start_date - timedelta(days=28),
#                                                       tests[0].start_date)
#                 clicks_test_group_before += clicks if clicks else 0
#
#             clicks_test_group_after = 0
#             for page in tests[0].get_urls_test_group():
#                 print(f'4) {page}')
#                 clicks = get_clicks_from_date_to_date(tests[0].site.domain, page,
#                                                       tests[0].start_date,
#                                                       tests[0].start_date + timedelta(days=28))
#                 clicks_test_group_after += clicks if clicks else 0
#
#             print(f'clicks_control_group_before = {clicks_control_group_before}')
#             print(f'clicks_control_group_after = {clicks_control_group_after}')
#             print(f'clicks_test_group_before = {clicks_test_group_before}')
#             print(f'clicks_test_group_after = {clicks_test_group_after}')
#
#             if clicks_control_group_before == 0 or clicks_control_group_before is None:
#                 result_before = 1
#             else:
#                 result_before = clicks_test_group_before / clicks_control_group_before
#
#             if clicks_control_group_after == 0 or clicks_control_group_after is None:
#                 result_after = 1
#             else:
#                 result_after = clicks_test_group_after / clicks_control_group_after
#
#             result = (result_after - result_before) * 100
#             print(f'result = {result}')
#             tests[0].result = result
#             tests[0].save()
#
#     table = {'head': ['Date', 'Control Group Clicks', 'Test Group Clicks', 'Ratio']}
#
#     for page in tests[0].get_urls_test_group():
#         test_group_data = extract_data_with_page_from_day_to_day(tests[0].site.domain, page, tests[0].start_date,
#                                                                  tests[0].start_date + timedelta(days=28))
#
#     for page in tests[0].get_urls_control_group():
#         control_group_data = extract_data_with_page_from_day_to_day(tests[0].site.domain, page, tests[0].start_date,
#                                                                     tests[0].start_date + timedelta(days=28))
#
#     if test_group_data.empty or control_group_data.empty:
#         return render(request, 'AB_tests/test_info.html', {'test': tests[0]})
#
#     table['body'] = []
#     index = 0
#     for date in test_group_data['date']:
#         if int(test_group_data['clicks'][index]) == 0:
#             ratio = 0
#         else:
#             ratio = int(control_group_data['clicks'][index]) / int(test_group_data['clicks'][index])
#
#         row = [test_group_data['date'][index], control_group_data['clicks'][index], test_group_data['clicks'][index], ratio]
#         print(row)
#         table['body'].append(row)
#         index += 1
#
#     print(table)
#     return render(request, 'AB_tests/test_info.html', {'test': tests[0], 'table': table})



