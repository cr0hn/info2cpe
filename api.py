#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
info2cpe - Copyright (C) 2014

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

import re

try:
    from cPickle import load, PickleError
except ImportError:
    from pickle import load, PickleError

from fuzzywuzzy import fuzz

__all__ = ["search_cpe"]


#----------------------------------------------------------------------
def fsplit(text):
    """
    Split a text in chunks.

    :param text: text to split.
    :type text: str

    :return: a set with the chunks.
    :rtype: set(str)
    """
    return set(_fsplit(text))


#----------------------------------------------------------------------
def _fsplit(text):
    """
    Private and recursive function for split text in chunks.

    :param text: text to split.
    :type text: str

    :return: a set with the chunks.
    :rtype: set(str)
    """

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
def search_cpe(search_term, cpe_db="cpe.db", results_number=1):
    """
    From a text try to get a CPE, using different approximations methods.

    ..note:
        If results_number is '1', search will be optimized because search ends when the first element,
        with 100% of match is found.

    :param search_term: String to looking for.
    :type search_term: str

    :param cpe_db: CPE database path.
    :type cpe_db: str

    :param results_number: maximum number of results to return.
    :type: int

    :return: a list of tuples as format: [(SEARCH_PROBABILITY, CPE, COMPLETE_DESCRIPTION), ...]
    :rtype: list(set(str, str, str)]

    :raises: ValueError
    """

    try:
        list_items = load(open(cpe_db, "rb"))
    except PickleError, e:
        raise ValueError("Error while loading CPE database. Error: %s." % e.message)

    terms = fsplit(search_term)

    # Create acronyms regular expressions
    acronyms = []
    for x in search_term.split(" "):
        if x.isupper():
            tmp_acronyms = []
            for x1 in x:
                tmp_acronyms.append("([%s][a-z0-9]+)[\s]*" % x1)
            acronyms.append(re.compile("".join(tmp_acronyms)))

    # Filters for false positives
    filters = [
        re.compile("(^[0-9\.]+$)")  # To detect expression like: 1.0.0
    ]

    # First filter
    partial_results1 = []
    partial_results1_append = partial_results1.append
    for k, x in list_items.iteritems():
        # Only unicode strings
        try:
            str(x)
        except UnicodeError:
            continue

        # Any coincidence?
        if any(w in x.lower() for w in terms):
            partial_results1_append((k, x, False))

        # Search in CPE
        #if any(w in k.lower() for w in terms):
        #    partial_results1_append((k, x, False))

        # There is an acronym?
        if any(acronym.search(x) is not None for acronym in acronyms):
            partial_results1_append((k, x, True))

    # Apply token_set_ratio
    partial_results2 = {}

    # k = CPE (str)
    # x = CPE description (str)
    # is_acronym = Bool
    for k, x, is_acronym in partial_results1:
        r = fuzz.partial_token_set_ratio(search_term, x, force_ascii=True)

        # Is false positive?
        if any(fil.search(x) is not None for fil in filters):
            continue

        # More weight if there is an acronym
        if is_acronym:
            r *= 1.25
            # Fix Valuer
            r = r if r <= 100 else 100

        partial_results2[k] = int(r)

        if results_number == 1 and r == 100:
            break

    result = []
    # Transform and get only the first N elements
    for x, y in sorted(partial_results2.iteritems(), key=lambda (k, v): v, reverse=True)[:results_number]:  # By value
        result.append((y, x, list_items[x]))

    return result
