#!/usr/bin/python

# Copyright (C) 2011 by Stuart Carnie
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import httplib, urllib, sys, argparse, getpass
from datetime import datetime
from datetime import timedelta

def date_type(string):
    if string.lower() != 'daily' and string.lower() != 'weekly':
        raise argparse.ArgumentTypeError("%s is an invalid value for datetype" % string)
    return string

def report_date(val):
    if val == 'today':
        today = datetime.today() + timedelta(-1)
        result = today.strftime('%Y%m%d')
    else:
        result = val

    return result


parser = argparse.ArgumentParser(description='iTunesConnect report download utility')
parser.add_argument('-u', '--username', required=True, help='The user name you use to log into iTunes Connect')
parser.add_argument('-p', '--password', help='The password you use to log into iTunes Connect; if omitted you will be prompted')
parser.add_argument('--id', metavar='VENDOR_ID', required=True, help='A value in the form 8#######, which identifies the entity for the reports you wish to download')
parser.add_argument('--reporttype', default='Sales', choices=['Sales'], help='This is the report type you want to download.  Currently only Sales Reports are available.')
parser.add_argument('--datetype', default='Daily', choices=['Daily', 'Weekly'], help='Selecting Weekly will provide you the Weekly version of the report. Selecting Daily will provide you the Daily version of the report.')
parser.add_argument('--subtype', default='Summary', choices=['Summary', 'Opt-In'], help='This is the parameter for the Sales Reports.')
parser.add_argument('--date', metavar='YYYYMMDD', default='today', type=report_date, help='This is the date of report you are requesting. If the value for Date parameter is not provided, you will get the latest report available.')
parser.add_argument('--output',default='./', help='Specifies the output directory.  The default is current directory.')

res = parser.parse_args()

if res.password is None:
    res.password = getpass.getpass()

if res.password is None or len(res.password) == 0:
    sys.exit(1)

params = urllib.urlencode({
    'USERNAME': res.username, 
    'PASSWORD': res.password, 
    'VNDNUMBER': res.id,
    'TYPEOFREPORT': res.reporttype,
    'DATETYPE': res.datetype,
    'REPORTTYPE': res.subtype,
    'REPORTDATE': res.date
})
headers = {"Content-type": "application/x-www-form-urlencoded"}
cn = httplib.HTTPSConnection('reportingitc.apple.com')
cn.request('POST', '/autoingestion.tft?', params, headers)
response = cn.getresponse()
errormsg = response.getheader('ERRORMSG')

if errormsg is None and response.status == httplib.OK:
    filename = response.getheader('filename')
    f = open(res.output + filename, 'w')
    data = response.read()
    f.write(data)
    f.close()
    print ("downloaded %s" % filename)

elif errormsg is not None:
    print errormsg
else:
    print response.status, response.reason
