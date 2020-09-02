from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import bs4
import re
import operator
from . import dao
import json
from .nocommit import hiddensettings

dao_defsrc = dao.DefinitionSrcDao(
    dbname=hiddensettings.DB_NAME,
    user=hiddensettings.DB_USER,
    pwd=hiddensettings.DB_PWD,
    host=hiddensettings.DB_HOST
)


def index(request):
    return render(request, "definition/index.html")


def check_input(word):
    if word == "":
        return False
    return True


def format_articles(divs):
    return "<br>".join([str(div) for div in divs])


def get_articles_src_already_stored(word):
    src = dao_defsrc.get(word)
    if src is not None:
        return json.loads(src)


def get_definition_html(word):
    """For the given word, return html code to embed."""
    word = word.lower()
    base_url = "https://www.cnrtl.fr/definition"
    url = f"https://www.cnrtl.fr/definition/{word}"
    articles_src = []

    _stored = get_articles_src_already_stored(word)
    if _stored is not None:
        articles_src = _stored
    else:
        resp = requests.get(url)
        html_content = resp.content
        soup = bs4.BeautifulSoup(html_content, "html.parser")
        links = [link for link in soup("a") if link.has_attr("onclick")]
        re_num = re.compile(f"/definition/({word}//[0-9])")
        for suffix in map(lambda x: x.group(1),
                      filter(lambda x: x is not None,
                      map(re_num.search,
                      map(operator.itemgetter("onclick"), links)))):
            url = f"{base_url}/{suffix}"
            resp = requests.get(url)
            articles_src.append(resp.content.decode("utf8"))
        dao_defsrc.write(word, json.dumps(articles_src))

    articles_divs = []
    for html in articles_src:
        soup = bs4.BeautifulSoup(html, "html.parser")
        divss = [div for div in soup("div")
                 if "id" in div.attrs and div["id"].startswith("art")]
        if divss:
            articles_divs.extend(divss[0])
            articles_divs.append("<hr>")

    return format_articles(articles_divs)


class DefinitionView(APIView):
    def get(self, request, word, format=None):
        html_content = get_definition_html(word) if check_input(word) else "Nope"
        return Response({"htmlcontent": html_content})
