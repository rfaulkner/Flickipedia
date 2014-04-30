import re

from BeautifulSoup import BeautifulSoup, Tag
from flickipedia.config.settings import GET_VAR_ARTICLE

from flickipedia.config import log, settings


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


def embed_photo_content(idx, photo, soup, section_node):
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
    tag['class'] = settings.SECTION_IMG_CLASS
    tag['id'] = settings.SECTION_IMG_CLASS + '-' + str(idx)

    # Format the image block
    #
    #   1. Define the outer div
    #   2. Define the img element for Flickr images
    #   3. Define the inner div which contains the like glyph

    outer_div = '<div style="position: relative; z-index:100">%s%s</div>'
    inner_div = '<div id="like-glyph-' + str(idx) + \
                '" class="like-glyph" style="position: absolute; bottom:0; ' \
                'left:10; z-index:150"></div>'
    inner_img = '<img src="https://farm%s.staticflickr.com/%s/%s_%s.jpg" ' \
                'width="300" height="300">'
    inner_img = inner_img % (photo['farm'], photo['server'],
                             photo['photo_id'], photo['secret'])

    tag.string = outer_div % (inner_div, inner_img)
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
            tag = embed_photo_content(photo_index, photos[photo_index], soup, node)
            html = html.replace(str(node), str(node) + str(tag))
            photo_index += 1
        else:
            break
    return html

