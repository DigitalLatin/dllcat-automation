#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 21:43:48 2018

This script iterates through a CSV of HathiTrust URLs, one per row in the 
first column, searches each page for the table row that lists publication 
information, and writes that information to a new CSV.

The reason for this is that some records originally gathered by DLL students
did not include publication information, so we had to go get it.

@author: sjhuskey
"""

import csv, codecs, requests, time, re
from bs4 import BeautifulSoup

# Open the source file to get the URLs.
file = codecs.open('Hathi-URLS.csv','r',encoding='utf-8')
data = csv.reader(file,delimiter=',')

# Make a list of URLs to iterate through.
HATHI_URLS = []
for row in data:
    # Ignore any empty rows; add only real values to the list.
    if row[0] != '':
        HATHI_URLS.append(row[0].strip())

# Create or open the file for storing the data.
with codecs.open('Hathi-output.csv','a',encoding='utf-8') as f:
    w = csv.writer(f)
    for i in HATHI_URLS:

        # Look like a human.
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
               'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept_Language':'en-GB,en;q=0.5'}

        # Assemble the request.
        req = requests.get(i, headers=headers)
        # Make sure that the data is in Unicode.
        req.encoding = 'utf-8'

        # Make the Beautiful Soup object.
        bs = BeautifulSoup(req.text, 'lxml')
        
        # Look for the data that we need. It's in a table with @class 'citation'
        data = []
        table = bs.find('table', attrs={'class':'citation'})
        rows = table.find_all('tr')
        
        # Make the row for the CSV.
        row_data = [i]
        
        # Cycle through the rows and get the data.
        for row in rows:
            # Since Hathi doesn't use @id or @class on its tables, we have to isolate the data the hard way.
            header = row.find('th')
            label = header.text
            stripped_label = str(label).strip(': ')
            
            # Look for the row that contains "Published", then grab the data in the adjacent column.
            if stripped_label == 'Published':
                td = row.find('td')
                # Clean up the data.
                data = td.text
                regex = re.compile(r'[\n\r\t]')
                reg_data = regex.sub('', data)
                stripped_data = reg_data.strip('  ')
                # Add the data to the list "row_data", to be added to the CSV below.
                row_data.append(stripped_data)
        
        # Write the row and print it, so that we can monitor the progress.
        w.writerow(row_data)
        print(row_data)

# Give the server a rest.
        time.sleep(2)