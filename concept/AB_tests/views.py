import datetime
import os
from urllib.parse import urlparse

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from .HelpPackages.google_search_api import extract_data, get_graphic_from_data
from .models import Site, SiteAdmins


def hello_world(request):
    return HttpResponse('Hello World')


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

