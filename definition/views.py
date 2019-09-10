from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView


def index(request):
    return render(request, "definition/index.html")


def get_definition_html(word):
    return word


class DefinitionView(APIView):
    def get(self, request, word, format=None):
        html_content = get_definition_html(word)
        return Response({"htmlcontent": html_content})
