#!/usr/bin/python
import json 
import sys

# return the base from a url
def url_basename(url):
    basename = ''
    pieces = url.split("/")
    if len(pieces) > 2:
        basename = pieces[2]
    elif len(pieces) == 2:
        basename = pieces[1]

    return basename
