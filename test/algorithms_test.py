#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
info2cpe - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""


import time
import re

from fuzzywuzzy import fuzz
from collections import OrderedDict


#----------------------------------------------------------------------
def search_token_set_radio(list_items, search_term):
    """Comment"""

    result = None

    partial_results = OrderedDict()

    for cve, x in list_items.iteritems():
        v = fuzz.token_set_ratio(search_term, x, force_ascii=True)

        # if v == 100:
        #     result = (cve, x, v)
        #     break

        partial_results[v] = (cve, x)

    # if partial_results and result is None:
    #     result = max(partial_results)

    # result = partial_results
    result = [partial_results.popitem() for x in xrange(20)]

    return result


#----------------------------------------------------------------------
def fsplit(text):
    return set(_fsplit(text))


def _fsplit(text):
    """Comment"""

    splitters = [" ", "/", "-", "..", ",", ";"]

    if not any([x in text for x in splitters]):
        return [text]
    else:
        results = []
        for spliter in splitters:
            if spliter in text:
                for sp in text.split(spliter):
                    results.extend(_fsplit(sp))

    return results


#----------------------------------------------------------------------
def search_token_manual(list_items, search_term):
    """Comment"""

    result = []

    terms = fsplit(search_term)

    # Create acronyms regular expressions
    acronyms = []
    for x in search_term.split(" "):
        if x.isupper():
            tmp_acronyms = []
            for x1 in x:
                tmp_acronyms.append("([%s][a-z0-9]+)[\s]*" % x1)
            acronyms.append(re.compile("".join(tmp_acronyms)))

    # First filter
    partial_results1 = []
    partial_results1_append = partial_results1.append
    for k, x in list_items.iteritems():
        # Only unicode strings
        try:
            unicode (x)
        except UnicodeError:
            continue

        # Any coincidence?
        if any((True for w in terms if w in x.lower())):
            partial_results1_append((k, False))  # Store only the key

        # There is an acronym?
        if any([True for acronym in acronyms if acronym.search(x) is not None]):
            partial_results1_append((k, True))

    # Apply token_set_ratio
    partial_results2 = {}
    for x, is_acronym in partial_results1:
        r = fuzz.partial_token_set_ratio(search_term, list_items[x], force_ascii=True)
        # r = fuzz.WRatio(search_term, list_items[x])

        # More weight if there is an acronym
        if is_acronym:
            r *= 1.25
            # Fix Valuer
            r = r if r <= 100 else 100

        partial_results2[x] = int(r)

    # Transform and get only the first N elements
    for x, y in sorted(partial_results2.iteritems(), key=lambda (k, v): v, reverse=True)[:3]:  # Order by value
        result.append((y, x, list_items[x]))

    return result


#----------------------------------------------------------------------
def search_partial_radio(list_items, search_term):
    """Comment"""

    result = None

    for cve, x in list_items.iteritems():
        v = fuzz.partial_ratio(search_term, x)

        if v == 100:
            result = (cve, x, v)
            break

    return result


#----------------------------------------------------------------------
def search_partial_radio_bubble(list_items, search_term):
    """Comment"""

    result = None

    items = list_items.values()
    items_reversed = {v: k for k, v in list_items.iteritems()}

    if len(list_items) % 2 != 0:
        items.append("")
        items_reversed[""] = ""

    partial_results = []

    for x in xrange(len(items)/2):

        if x == abs(-x-1):
            break

        x1 = items[x]
        y1 = items[-x-1]

        v1 = fuzz.partial_ratio(search_term, x1)
        v2 = fuzz.partial_ratio(search_term, y1)

        if v1 == 100:
            result = (v1, items_reversed[x1], x1)
            break
        if y1 == 100:
            result = (v2, items_reversed[y1], y1)
            break

        partial_results.append((v1, items_reversed[x1], x1))
        partial_results.append((v2, items_reversed[y1], y1))

    if partial_results and result is None:
        result = max(partial_results)

    return result


#----------------------------------------------------------------------
def load_file(file_path):
    """
    :return: dict(CPE -> str)
    :rtype: dict
    """
    with open(file_path, "rU") as f:
        d = {}

        for l in f.readlines():
            l = l.replace("\n", "")
            k = l.split(" ### ")

            d[k[0].strip()] = k[1].strip()

        return d

    return None


if __name__ == '__main__':
    file_info = "../Doc/lista.txt"

    info = load_file(file_info)

    banners = [
        "JBoss Web/7.0.17 Final-redhat-1",
        "Zeus/4.2",
        "Sun ONE Web Server 6.1",
        "Microsoft IIS httpd 7.5"
    ]

    methods = [
        # search_partial_radio_bubble,
        # search_partial_radio,
        # search_token_set_radio,
        search_token_manual
    ]

    # Search for banners
    for banner in banners:

        for method in methods:
            print "Method: %s" % str(method)
            print "Banner: %s" % banner
            print

            start = time.time()
            r = method(info, banner)
            print r
            end = time.time()

            print "Execution time: %s\n\n" % (end - start)