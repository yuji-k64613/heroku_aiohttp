import re

def is_text(content_type):
    return re.match("^text/", content_type) is not None

