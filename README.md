What's info2cpe
===============

info2cpe is a library that try to convert a simple string (a service banner, for example) into their CPE v2.3 value. The library report the CPE following the standard CPE 2.3.

For more information, please visit the official website of CPE, maintained by MITRE: [http://cpe.mitre.org/](http://cpe.mitre.org/)

![CPE specification logo](http://cpe.mitre.org/images/cpe_logo.gif)

How it works?
=============

info2cpe use different mathematicians methods to try to match a simple text into the more approximate CPE value.

** A lot of times, the library can't find the exactly correspondence with CPE database. **

Usage
=====

You use the info2cpe as a library and as a command line tool:

Command line
------------

Diplay the help:

	python info2cpe.py -h
	usage: info2cpe.py [-h] [-t INPUT_TEXT] [-c CPE_FILE] [--update]

	info2cpe try to convert any string into CPE

	optional arguments:
	  -h, --help            show this help message and exit
	  -t INPUT_TEXT, --text INPUT_TEXT
                        text where looking for the CPE.
	  -c CPE_FILE, --cpe-db CPE_FILE
                        cpe database
	  --update              update cpe database
	
Update the CPE database:

	python info2cpe.py --update
	[*] Downloading CPE database (this can take some time).
	[*] Loading XML CPE file.
	[*] Converting XML to CPE database.
	[*] Saving CPE database in 'cpe.db' file.
	[*] Done!
	
Looking for a CPE from command line:

	python info2cpe.py -t "Microsoft IIS httpd 7.5"
	[*] Starting analysis...
	[*] Analysis time: 0.552829027176
	[*] Results:
	
	|----
	| CPE: cpe:/a:microsoft:iis:7.5
	| Name: Microsoft Internet Information Services (IIS) 7.5
	| Probability: 100%
	|____
	
	|----
	| CPE: cpe:/a:microsoft:iis:7.0
	| Name: Microsoft Internet Information Services (IIS) 7.0
	| Probability: 98%
	|____
	
	|----
	| CPE: cpe:/a:microsoft:iis:6.0
	| Name: Microsoft Internet Information Services (IIS) 6.0
	| Probability: 90%
	|____


As a library
------------

Looking for a CPE from command python code:

	>>>from api import search_cpe
	>>>banner="Microsoft IIS httpd 7.5"
	>>>result=search_cpe(banner)
	>>>print result
	[(100, 'cpe:/a:microsoft:iis:7.5', 'Microsoft Internet Information Services (IIS) 7.5'), (98, 'cpe:/a:microsoft:iis:7.0', 'Microsoft Internet Information Services (IIS) 7.0'), (90, 'cpe:/a:microsoft:iis:6.0', 'Microsoft Internet Information Services (IIS) 6.0')]

Contribute
==========

Any kind of contribution is wellcome. Feel free to make a fork and send me your changes.
