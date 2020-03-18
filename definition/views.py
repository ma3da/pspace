from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import bs4
import re
import operator

def index(request):
    return render(request, "definition/index.html")


def check_input(word):
    if word == "":
        return False
    return True


def format_article(art):
    return "</br>".join([str(div) for div in art])


def get_definition_html(word):
    word = word.lower()
    base_url = "https://www.cnrtl.fr/definition"
    url = f"https://www.cnrtl.fr/definition/{word}"
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.content, "html.parser")
    links = [link for link in soup("a") if link.has_attr("onclick")]
    re_num = re.compile(f"/definition/({word}//[0-9])")
    suffixes = list(map(lambda x: x.group(1), 
                filter(lambda x: x is not None,
                map(re_num.search,
                map(operator.itemgetter("onclick"), links)))))
    def_html = []
    for suffix in suffixes:
        print("process", suffix)
        url = f"{base_url}/{suffix}"
        resp = requests.get(url)
        soup = bs4.BeautifulSoup(resp.content, "html.parser")
        arts = [div for div in soup("div")
                if "id" in div.attrs and div["id"].startswith("art")]
        if arts:
            def_html.extend(arts[0])
            def_html.append("<hr>")

    return format_article(def_html)


class DefinitionView(APIView):
    def get(self, request, word, format=None):
        html_content = get_definition_html(word) if check_input(word) else "Nope"
        return Response({"htmlcontent": html_content})
