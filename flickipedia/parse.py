import re
from BeautifulSoup import BeautifulSoup


def parse_strip_elements(html):
    soup = BeautifulSoup(html)

    #
    for div in soup.findAll('div', 'thumbinner'): div.extract()
    for div in soup.findAll('div', 'thumb tright'): div.extract()

    #
    for div in soup.findAll('span', 'mw-editsection'): div.extract()
    return str(soup)


