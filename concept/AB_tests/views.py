from django.shortcuts import render
from django.http import HttpResponse


def hello_world(request):
    return HttpResponse('Hello World')


def create_ab_test(request):
    return render(request, 'AB_tests/create_ab_test.html')


def finish_ab_test(request):
    return render(request, 'AB_tests/finish_ab_test.html')
