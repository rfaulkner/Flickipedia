import re


def parse(lines):
    out = ''
    section = None
    for line in lines:
        if re.search(r'^== ', line):
            formatted, section = set_heading(line, '==', 'h3')
        elif re.search(r'^=== ', line):
            formatted, section = set_heading(line, '===', 'h4')
        elif re.search(r'^==== ', line):
            formatted, section = set_heading(line, '====', 'h4')
        else:
            formatted = '<p>' + line.strip() + '</p>'

        if not section == "seealso" and not section == "externallinks":
            out += formatted
    return out


def set_heading(line, token, heading_markup):
    section = ''.join(line.strip().split(token)[1:-1]).strip()
    out = '<br><{0}>'.format(heading_markup) + section + \
          '</{0}>'.format(heading_markup)
    return out, ''.join(section.lower().split())


def parse_links(content, links):
    raise NotImplementedError()