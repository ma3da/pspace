from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import bs4


def index(request):
    return render(request, "definition/index.html")


def check_input(word):
    if word == "":
        return False
    return True


def format_article(art):
    return "</br>".join([str(div) for div in art])


def get_definition_html(word):
    url = f"https://www.cnrtl.fr/definition/{word}"
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.content, "html.parser")
    arts = [div for div in soup("div") if "id" in div.attrs and div["id"].startswith("art")]
    if not arts:
        return "Nope"
    return format_article(arts[0])


class DefinitionView(APIView):
    def get(self, request, word, format=None):
        html_content = get_definition_html(word) if check_input(word) else "Nope"
        return Response({"htmlcontent": html_content})
