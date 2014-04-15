import re

from BeautifulSoup import BeautifulSoup
from flickipedia.config.settings import GET_VAR_ARTICLE


def parse_strip_elements(html):
    """
    Strips out undesirable divs & spans
    """
    soup = BeautifulSoup(html)

    # Remove thumbs
    for node in soup.findAll(attrs={'class': re.compile(r".*\bgallery\b.*")}): node.extract()
    for node in soup.findAll(attrs={'class': re.compile(r".*\bthumb\b.*")}): node.extract()
    for node in soup.findAll(attrs={'class': re.compile(r".*\bimage\b.*")}): node.extract()

    for div in soup.findAll('div', 'gallery'): div.extract()
    for td in soup.findAll('td', 'mbox-image'): td.extract()

    # Remove edit links
    for div in soup.findAll('span', 'mw-editsection'): div.extract()
    return str(soup)


def parse_convert_links(html):
    """
    Handles converting links to Flickipedia
    """
    # TODO - get all the links

    soup = BeautifulSoup(html)

    # for a in soup.findAll('a', 'mw-redirect'):
    #     a['href'] = a['href'].replace('/wiki/', '?' + GET_VAR_ARTICLE + '=')

    for a in soup.findAll('a'):
        if re.search(r'/wiki/', a['href']):
            a['href'] = a['href'].replace('/wiki/', '?' + GET_VAR_ARTICLE + '=')
    return str(soup)