from flaskr import dao
import requests
import bs4
import re
import operator
import json
import psycopg2
import os

try:
    from flaskr.nocommit import hiddensettings as hs
    dao_defsrc = dao.DefinitionSrcDao(
        dbname=os.environ.get("PSPACE_DB_NAME", hs.DB_NAME),
        user=os.environ.get("PSPACE_DB_USER", hs.DB_USER),
        pwd=os.environ.get("PSPACE_DB_PWD", hs.DB_PWD),
        host=os.environ.get("PSPACE_DB_HOST", hs.DB_HOST),
        port=os.environ.get("PSPACE_DB_PORT", hs.DB_PORT)
    )
except Exception as e:  # e.g. connection issue
    if "dao_defsrc" in globals():
        dao_defsrc.close()
    print(e)
    print("Using a dummy DAO, no data to be read or written.")
    dao_defsrc = dao.DummyDao()


def format_articles(divs):
    return "<hr>".join(divs)


def get_articles_src_already_stored(word):
    src = dao_defsrc.get(word)
    if src is not None:
        return json.loads(src)


def has_class(tag, class_name):
    return isinstance(tag, bs4.element.Tag) and tag.has_attr("class") and class_name in tag["class"]


def process_article_src_dummy(html):
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

    def convert(tag_iter, current):
        for tag in tag_iter:
            if has_class(tag, "tlf_cdefinition"):
                if not tag.find_previous_sibling(class_="tlf_csyntagme") \
                        and not tag.find_next_sibling(class_="tlf_cdefinition"):
                    return [tag]
            if has_class(tag, "tlf_parah"):
                current.append(convert(tag.children, []))
        return current

    tree = convert(article, [])

    def flatten(node):
        if isinstance(node, bs4.element.Tag):
            return str(node)
        # list | None
        if not node:
            return None
        flattened = list(filter(lambda s: s is not None, map(flatten, node)))
        if not flattened:
            return None
        elif len(flattened) == 1:
            return flattened[0]
        else:
            return f"<ul>{''.join(map(lambda s: f'<li>{s}</li>', flattened))}</ul>"

    return f"<p>{word}</p><div>{flatten(tree)}</div>"


def get_definition_html(word, process_fn):
    """For the given word, return html code to embed.
    :returns: (str, str): html code, data source (local/remote)
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

    return format_articles(map(process_fn, articles_src)), source


def check_input(word):
    return word.strip() != ""
