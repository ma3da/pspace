from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


@login_required()
def index(request):
    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))
