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

import time
import argparse
import os

from sys import exit

from api import search_cpe


#----------------------------------------------------------------------
def update_db():
    """
    This function download, parse and update cpe.db.
    """
    from urllib2 import urlopen, HTTPError, URLError
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        from xml.etree import ElementTree as ET

    try:
        from cPickle import dump, PickleError
    except ImportError:
        from pickle import dump, PickleError

    cpe_xml_url = "http://static.nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml"
    cpe_filename = "official-cpe-dictionary_v2.3.xml"
    cpe_db_filename = "cpe.db"

    #
    # Download the file
    #
    try:
        print "[*] Downloading CPE database (this can take some time)."
        d = urlopen(cpe_xml_url)

        with open(cpe_filename, "w") as f:
            f.write(d.read())

    except HTTPError, e:
        print "[!] Can't download CPE dictionary: Error: %s" % e.message
        exit(1)
    except URLError, e:
        print "[!] Can't download CPE dictionary: Error: %s" % e.message
        exit(1)

    #
    # Parse the file
    #
    cpe_info = {}

    try:
        print "[*] Loading XML CPE file."
        root = ET.parse(cpe_filename).getroot()
    except ET.ParseError, e:
        print "[!] Error while parsing CPE dictionary: Error: %s" % e.message
        exit(1)

    # Start at 1 because first element is 'generator' tag, and is not valid for us
    print "[*] Converting XML to CPE database."
    for item in root.getchildren()[1:]:
        cpe_info[item.attrib["name"]] = item.getchildren()[0].text

    # Serialize
    try:
        print "[*] Saving CPE database in '%s' file." % cpe_db_filename
        dump(cpe_info, open(cpe_db_filename, "wb"), protocol=2)
    except PickleError, e:
        print "[!] Error while saving CPE database: Error: %s" % e.message
        exit(1)

    print "[*] Done!"


#----------------------------------------------------------------------
def main(args):
    """
    Main function

    :param args: ArgumentParser object.
    :type args: ArgumentParser
    """
    # Update database?
    if args.UPDATE:
        update_db()
        exit(0)

    #
    # Common vars
    #

    # Input text
    in_text = args.INPUT_TEXT

    if in_text is None:
        print "[!] --text option is required."
        exit(1)


    # CPE database
    cpe_db = os.path.join(os.path.split(__file__)[0], "cpe.db")
    if args.CPE_FILE:
        cpe_db = args.CPE_FILE
    if not os.path.exists(cpe_db):
        print "\n[!] CPE database '%s' not exits." % cpe_db
        exit(0)
    if os.path.isdir(cpe_db):
        print "\n[!] CPE database '%s' is not a regular file." % cpe_db
        exit(0)

    #
    # Call
    #
    print "[*] Starting analysis..."

    start_time = time.time()
    results = search_cpe(in_text, cpe_db)
    stop_time = time.time()

    # Display results
    print "[*] Analysis time: %s" % (stop_time - start_time)
    print "[*] Results:\n"

    for prob, cpe, name in results:

        print "   |----"
        print "   | CPE: %s" % cpe
        print "   | Name: %s" % name
        print "   | Probability: %s%%" % prob
        print "   |____"
        print



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='info2cpe try to convert any string into CPE')
    parser.add_argument('-t', '--text', dest="INPUT_TEXT", help="text where looking for the CPE.", default=None)
    parser.add_argument('-c', '--cpe-db', dest="CPE_FILE", type=int, help="cpe database", default=None)
    parser.add_argument('--update', action="store_true", dest="UPDATE", help="update cpe database", default=False)

    args = parser.parse_args()

    main(args)