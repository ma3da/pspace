from flaskr import dao_defsrc
import requests
import bs4
import re
import operator
import json
import psycopg2
import os


def get_articles_src_already_stored(word):
    src = dao_defsrc.get(word)
    if src is not None:
        return json.loads(src)


def has_class(tag, class_name):
    return isinstance(tag, bs4.element.Tag) and tag.has_attr("class") and class_name in tag["class"]


def to_raw_html(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    article = soup.find("div", id=re.compile("^art"))
    return "<br>".join(map(str, article)) if article else ""


def process_article_src(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    article = soup.find("div", id=re.compile("^art"))

    if not article:
        return ""

    word = article.find_all("div", class_="tlf_cvedette")
    if len(word) != 1:
        raise ValueError(f"Expected to find exactly one word, found: {word}")
    word = word[0]

    def getcls(t):
        return ".".join(t.get("class", ()))

    def_obj = {"word": word.text, "defs": []}
    for parah in filter(lambda t: getcls(t) == "tlf_parah", article.children):
        group = []
        waiting = None
        for t in parah.find_all("span"):
            cls = getcls(t)
            text = t.text
            if cls == "tlf_cdefinition":
                if waiting:
                    group.append({"type": "synt", "synt": waiting, "def": text})
                else:
                    group.append({"type": "def", "def": text})
                waiting = None
            elif cls == "tlf_csyntagme":
                waiting = text
            else:
                waiting = None
        def_obj["defs"].append(group)

    return def_obj


def get_definition(word, process_fn, raw):
    """For the given word, return code to embed: if raw, a string of html, else,
    a dict to be parsed by the client.
    :returns: (str|dict, str): definition, data source (local/remote)
    """
    word = word.lower()
    base_url = "https://www.cnrtl.fr/definition"
    url = f"https://www.cnrtl.fr/definition/{word}"
    articles_src = []
    source = "remote"

    _stored = get_articles_src_already_stored(word)
    if _stored is not None:
        articles_src = _stored
        source = "local"
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

    if raw:
        return "<hr>".join(map(process_fn, articles_src)), source
    else:
        return {d["word"]: d["defs"] for d in map(process_fn, articles_src)}, source


def check_input(word):
    return word.strip() != ""
