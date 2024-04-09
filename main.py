import re
import sys
import time
import xml.etree.ElementTree as ET

import bs4
import lxml
import requests
from tqdm import tqdm

from markdownify import markdownify as md

def get_sitemap_url(site_url: str) -> None:
    resp: requests.Response = requests.get(f"{site_url}/robots.txt")
    lines = resp.text.splitlines()
    line = list(filter(
        lambda line: re.match(r"^[Ss]itemap:", line),
        lines
    ))
    return line[0].split(" ")[-1]


def sitemap(url: str):
    resp: requests.Response = requests.get(url)
    data = ET.fromstring(resp.text)
    for item in data:
        yield item[0].text


def scrape_recipe(recipe_url: str) -> tuple:
    # We could get the recipe name from the Structured Data,
    # but we're going to use the title instead for brevity.
    resp: requests.Response = requests.get(recipe_url)
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(resp.text, "lxml")
    title: bs4.Tag | None = soup.select_one('title')
    str_title: str = str(title.text).split("–")[0].rstrip()
    recipe: bs4.Tag | None = soup.select_one(".wprm-recipe-container")
    return str_title, str(recipe)


def write_recipe(recipe_name: str, recipe_html: str) -> None:
    with open(f"./recipes/{recipe_name}.md", "wt") as recipe_file:
            recipe_file.write(md(recipe_html))


if __name__ == "__main__" :
    sm_url = get_sitemap_url(sys.argv[1])
    for url in tqdm(sitemap(sm_url)):
        name, html = scrape_recipe(url)
        write_recipe(name, html)
        time.sleep(0.5)
