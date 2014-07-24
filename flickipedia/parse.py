import re

from BeautifulSoup import BeautifulSoup, Tag
from flickipedia.config.settings import GET_VAR_ARTICLE

from flickipedia.config import log, settings

TITLE_PHOTO_SIZE_X = 600
TITLE_PHOTO_SIZE_Y = 400


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


def embed_photo_content(idx, photo, soup, sizex=300, sizey=300):
    """
    Embeds a new photo at the top of a section

    :param photo:       Photo info from flickr.photos.search
    :param section:     Section header

    :return:    modified section content
    """
    tag = Tag(soup, 'div')
    tag['title'] = photo['title']
    tag['class'] = settings.SECTION_IMG_CLASS
    tag['id'] = settings.SECTION_IMG_CLASS + '-' + str(idx)
    tag['photo-id'] = photo['id']
    tag['votes'] = photo['votes']

    # Tag for link glyph
    tag_link_container = Tag(soup, 'div')
    tag_link_container['id'] = 'link-glyph-' + str(idx)
    tag_link_container['class'] = 'link-glyph'
    tag_link_container['style'] = 'position: absolute; top:0; ' \
                'left:100; z-index:150'

    tag_link = Tag(soup, 'a')
    tag_link['href'] = 'https://www.flickr.com/photos/%s/%s' % (
        photo['owner'], photo['photo_id'])
    tag_link.string = '<img style="opacity:0.4; background-color:#cccccc;" ' \
                      'src="/static/img/link.png" width="25" height="25">'

    tag_link_container.string = str(tag_link)

    # Format the image block
    #
    #   1. Define the outer div
    #   2. Define the img element for Flickr images
    #   3. Define the inner divs which contains the vote glyph, endorse and reject glyphs

    outer_div = '<div style="position: relative; z-index:100">%s%s%s</div>'
    outer_div += '<div style="clear:both;">&nbsp;</div>'
    inner_div = '<div id="vote-glyph-' + str(idx) + '"' + \
                ' class="vote-glyph" style="position: absolute; bottom:0; ' \
                'left:10; z-index:150">' \
                '<div id="endorse-' + str(idx) + '" class="endorse" ' \
                                                 'style="float:left"></div>' \
                '<div id="endorsecount-' + str(idx) + '" class="endorsecount" ' \
                                                 'style="float:left"></div>' \
                '<div id="exclude-' + str(idx) + '" class="exclude" ' \
                                                'style="float:left"></div>' \
                '<div id="excludecount-' + str(idx) + '" class="excludecount" ' \
                                                'style="float:left"></div>' \
                '</div>'

    inner_img = '<img src="https://farm%s.staticflickr.com/%s/%s_%s.jpg" ' \
                'width="' + str(sizex) + '" height="' + str(sizey) + '">'
    inner_img = inner_img % (photo['farm'], photo['server'],
                             photo['photo_id'], photo['secret'])

    tag.string = outer_div % (inner_div, str(tag_link_container), inner_img)
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

    # Embed Title photo
    lf = '<div style="clear:both;">&nbsp;</div>'
    try:
        tag = embed_photo_content(photo_index, photos[photo_index], soup,
            TITLE_PHOTO_SIZE_X, TITLE_PHOTO_SIZE_Y)
    except (ValueError, KeyError, IndexError):
        log.info('In parse no photos found')
        return html

    html = str(tag) + lf + lf + html
    photo_index += 1

    # Embed section photos
    headers = soup.findAll('h2')
    headers.extend(soup.findAll('h3'))
    for node in headers:
        if len(photos) > photo_index:
            tag = embed_photo_content(photo_index, photos[photo_index], soup)
            html = html.replace(str(node), str(node) + str(tag))
            photo_index += 1
        else:
            break
    return html


def format_title_link(title, title_link):
    """Format the title header"""
    soup = BeautifulSoup('')
    tag = Tag(soup, 'a')
    tag['href'] = 'http://en.wikipedia.org/wiki/%s' % title_link
    tag.string = title
    return str(tag)


def get_section_titles(html, section_tag):
    """Fetch the section headers of the page"""
    soup = BeautifulSoup(html)
    headers = soup.findAll(section_tag)
    titles = []
    for node in headers:
        titles.append(node.string)
    return []
