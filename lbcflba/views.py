from django.views import generic

from . import app_name
from .models import Transaction


class IndexView(generic.ListView):
    template_name = f"{app_name}/index.html"
    context_object_name = 'transactions'

    def get_queryset(self):
        return app_name
