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


def embed_photo_content(photo, section_soup):
    """
    Embeds a new photo at the top of a section

    :param photo:       Photo info from flickr.photos.search
    :param section:     Section header

    :return:    modified section content
    """

    tag = section_soup.Tag(section_soup, 'a')
    tag.string = '<a href="https://www.flickr.com/photos/' + photo.owner + \
                 '/' + photo.photo_id  + '" title="' + photo.title + \
                 '"><img src="https://farm' + photo.farm + \
                 '.staticflickr.com/' + photo.server + '/' + photo.photo_id \
                 + '_' +  photo.secret + '.jpg" width="300" height="300"></a>'

    section_soup.insert(1, tag)
    return str(section_soup)


def handle_photo_integrate(photos, html):
    """
    Integrate photo link tags into content.  This walks through each section
    header and inserts an image below the header.

    :param photos:  List of photo meta-info
    :param html:    Wiki-html

    :return:    modified content
    """
    soup = BeautifulSoup(html)

    photo_index = 0
    for node in soup.findAll(attrs={'class': 'mw-headline'}):
        if len(photos) > photo_index:
            embed_photo_content(photos[photo_index], node)
            photo_index += 1
        else:
            break
    return str(soup)

