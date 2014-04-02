import re

def parse(lines):
    out = ''
    for line in lines:
        if re.search(r'^== ', line):
            out += '<br><h3>' + ''.join(line.strip().split('==')[1:-1]).strip() \
                   + '</h3>'
        elif re.search(r'^=== ', line):
            out += '<br><h4>' + ''.join(line.strip().split('===')[1:-1]).strip() \
                   + '</h4>'
        elif re.search(r'^==== ', line):
            out += '<br><h4>' + ''.join(line.strip().split('====')[1:-1]).strip() \
                   + '</h4>'
        else:
            out += '<p>' + line.strip() + '</p>'
    return out
