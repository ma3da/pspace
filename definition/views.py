from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import bs4
import re
import operator
import os

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


def get_html_src(word):
    """return {"article number": "html content bytes"} for given word"""

    word = word.lower()
    base_url = "https://www.cnrtl.fr/definition"
    url = f"https://www.cnrtl.fr/definition/{word}"

    articles = {}
    # for dev, to stop spamming mothership:
    src_fp = os.path.join(os.path.expanduser("~"), "tmp", "pspace-def", word)
    if not os.path.exists(src_fp):
        print("save")
        os.makedirs(src_fp)
        resp = requests.get(url)
        soup = bs4.BeautifulSoup(resp.content, "html.parser")
        links = [link for link in soup("a") if link.has_attr("onclick")]
        re_num = re.compile(f"/definition/{word}//([0-9])")
        suffixes = list(map(lambda x: x.group(1), 
                    filter(lambda x: x is not None,
                    map(re_num.search,
                    map(operator.itemgetter("onclick"), links)))))
        for suffix in suffixes:
            url = f"{base_url}/{word}/{suffix}"
            resp = requests.get(url)
            with open(os.path.join(src_fp, suffix), "wb") as f:
                f.write(resp.content)
            articles[suffix] = resp.content
    else:
        print("read")
        for suffix in os.listdir(src_fp):
            with open(os.path.join(src_fp, suffix), "rb") as f:
                articles[suffix] = f.read()

    return articles


def get_definition_html(word):
    articles = []
    sources = get_html_src(word)
    for suffix, content in sources.items():
        soup = bs4.BeautifulSoup(content, "html.parser")

        article = {}
        
        detail = soup.find(class_="tlf_cvedette") 
        print(detail.contents)
        article["word"] = detail.text if detail else word
        article["blocs"] = []

        # transform definitions words into links
        for tag in soup.find_all(class_="tlf_cdefinition"):
            d = {}
            article["blocs"].append(d)

            d["definition"] = str(tag.string).split()
        articles.append(article)

    return articles


class DefinitionView(APIView):
    def get(self, request, word, format=None):
        data = get_definition_html(word) if check_input(word) else "Nope"
        return Response(data)
