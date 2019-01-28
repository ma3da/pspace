from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


class MainLoginView(LoginView):
    next = "index"


@login_required(login_url="login")
def index(request):
    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))
