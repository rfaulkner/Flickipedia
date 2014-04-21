import re

from BeautifulSoup import BeautifulSoup, Tag
from flickipedia.config.settings import GET_VAR_ARTICLE

from flickipedia.config import log


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


def embed_photo_content(photo, soup, section_node):
    """
    Embeds a new photo at the top of a section

    :param photo:       Photo info from flickr.photos.search
    :param section:     Section header

    :return:    modified section content
    """
    tag = Tag(soup, 'a')
    tag['href'] = 'https://www.flickr.com/photos/%s/%s' % (photo['owner'],
                                                           photo['photo_id'])
    tag['title'] = photo['title']
    img_tag = '<img src="https://farm%s.staticflickr.com/%s/%s_%s.jpg" ' \
              'width="300" height="300">'
    tag.string = img_tag % (photo['farm'], photo['server'],
                            photo['photo_id'], photo['secret'])
    return tag


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

    for node in soup.findAll('h3'):
        if len(photos) > photo_index:
            log.debug(photos[photo_index])
            tag = embed_photo_content(photos[photo_index], soup, node)
            html = html.replace(str(node), str(node) + str(tag))
            photo_index += 1
        else:
            break
    return html

