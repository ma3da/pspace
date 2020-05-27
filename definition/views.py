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


def url_def(word):
    return f"https://www.cnrtl.fr/definition/{word}"


def url_tag(soup, word):
    link = soup.new_tag("a")
    link.string = word
    link["href"] = "#"
    return link


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
    main_divs = []
    for suffix in suffixes:
        print("process", suffix)
        url = f"{base_url}/{suffix}"
        resp = requests.get(url)
        soup = bs4.BeautifulSoup(resp.content, "html.parser")

        # transform definitions words into links
        for tag in soup.find_all(class_="tlf_cdefinition"):
            s = str(tag.string)
            tag.clear()
            for w in s.split():
                if tag.contents:
                    tag.append(" ")
                tag.append(url_tag(soup, w))

        arts = [div for div in soup("div")
                if "id" in div.attrs and div["id"].startswith("art")]
        if arts:
            art_html = arts[0]

            main_divs.extend(art_html)
            main_divs.append("<hr>")

    return format_article(main_divs)


class DefinitionView(APIView):
    def get(self, request, word, format=None):
        html_content = get_definition_html(word) if check_input(word) else "Nope"
        return Response({"htmlcontent": html_content})
