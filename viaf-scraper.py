#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 15:22 2018

@author: sjhuskey

This program does the following:
    
    * creates a CSV file for output and writes a header row
    * creates a list of VIAF ids to serve as the basis for url requests
    * connects to https://viaf.org
    * scrapes author names and other information
    * writes the results to the CSV file

"""

import csv, codecs, requests, time, re
from bs4 import BeautifulSoup

# Open the source file to get the VIAF ID's.
file = codecs.open('../editors/Editors-To-Add-2018-09-09.csv','r',encoding='utf-8')
data = csv.reader(file,delimiter=',')

# Make a list of VIAF ID's
VIAF_URLS = []
for row in data:
    # Ignore any empty rows; add real values to VIAF_IDS
    if row[0] != '':
        VIAF_URLS.append(row[0].strip())

#del VIAF_URLS[0]
# Create or open the file for storing the data.
with codecs.open('../editors/editors-output-2018-09-11.csv','a',encoding='utf-8') as f:
    w = csv.writer(f)
    # Write the header row for the output file, using the existing VIAF ID as the key.
    w.writerow(['Key','Authorized Name','Author Name English',
                'Author Name Latin','Perseus Name','Time Period',
                'Author Birth Date','Author Death Date','Floruit/Active',
                'Ancient Geographic Identity','Modern Geographic Identity',
                'LoC Name','LoC ID','LoC Source: URL','LofC URI: URL','PHI Number',
                'Stoa Number','VIAF ID','VIAF Source: URL','BNE Name',
                'BNE URL','BNF Name','BNF URL','DNB Name',
                'DNB URL','ICCU Name','ICCU URL','ISNI Name',
                'ISNI URL','Wikidata URL','Wikipedia URL','WorldCat Identity URL'])    
    
# Iterate over the IDS in VIAF_IDS and scrape.    
    for i in VIAF_URLS:

        # Look like a human.
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
               'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept_Language':'en-GB,en;q=0.5'}

        # Append each VIAF ID to the base URL and get the content 
        req = requests.get(i, headers=headers)
        # Make sure that the data is in Unicode.
        req.encoding = 'utf-8'

        # Make the Beautiful Soup object.
        bs = BeautifulSoup(req.text, 'lxml')
            
   # Define functions for scraping authorized name forms and URIs from different library databases
    # Wikidata
        # Wikidata link
        def wkp_a(href):
            return href and re.compile(r'.*wikidata\.org.*').search(href)
        
        def wkp_link():
            wkp_link_find = bs.find('a', href=wkp_a)
            if not wkp_link_find:
                return ''
            else:
                wkp_link = wkp_link_find.attrs['href']
                return 'https:'+wkp_link
        
        # Wikidata preferred name
        def wkp_b(href):
                return href and re.compile(r'.*processed/WKP.*').search(href)
            
        def wkp_name():
            wkp_name_find = bs.find(href=wkp_b)
            if not wkp_name_find:
                return ''
            else:
                wkp_names = wkp_name_find.select('span')
                wkp_name_list = [i.get_text() for i in wkp_names]
                wkp_name = ' '.join(wkp_name_list)
                return wkp_name
    
    # International Standard Name Identifier (ISNI)
        #ISNI link
        def isni_a(href):
            return href and re.compile(r'.*isni\.org.*').search(href)
        
        def isni_link():
            isni_link_find = bs.find(href=isni_a)
            if not isni_link_find:
                return ''
            else:
                isni_link = isni_link_find.attrs['href']
                return isni_link
        # ISNI authorized name
        def isni_b(href):
            return href and re.compile(r'.*processed/ISNI.*').search(href)
        
        def isni_name():
            isni_name_find = bs.find(href=isni_b)
            if not isni_name_find:
                return ''
            else:
                isni_names = isni_name_find.select('span')
                isni_name_list = [i.get_text() for i in isni_names]
                isni_name = ' '.join(isni_name_list)
                return isni_name
                            
    # Library of Congress
        # Find the link to the specific page on id.loc.gov
        def loc_a(href):
            return href and re.compile(r'.*id\.loc\.gov.*').search(href)
        
        def loc_link():
            loc_link_find = bs.find(href=loc_a)
            if not loc_link_find:
                return ''
            else:
                loc_link = loc_link_find.attrs['href']
                return 'https:'+loc_link
            
        def loc_id():
            loc_id_find = bs.find(href=loc_a)
            if not loc_id_find:
                return ''
            else:
                loc_id = loc_id_find.attrs['href']
                loc_id_stripped = str(loc_id.strip('//id.loc.gov/authorities/'))
                return loc_id_stripped
        
        def loc_source():
            loc_source_find = bs.find(href=loc_a)
            if not loc_source_find:
                return ''
            else:
                loc_source = loc_source_find.attrs['href']
                loc_source_stripped = loc_source.strip('//id.log.gov/authorities/names/')
                loc_source_url = 'https://lccn.loc.gov/' + loc_source_stripped
                return loc_source_url
            
        # Find the LOC authorized name form.
        def loc_b(href):
            return href and re.compile(r'.*processed/LC.*').search(href)
        
        def loc_name():
            loc_name_find = bs.find(href=loc_b)
            if not loc_name_find:
                return ''
            else:
                loc_names = loc_name_find.select('span')
                loc_name_list = [i.get_text() for i in loc_names]
                loc_name = ' '.join(loc_name_list)
                return loc_name
        
    # French National Library (BNF)
        # French National Library Link
        def bnf_a(href):
            return href and re.compile(r'.*catalogue\.bnf\.fr.*').search(href)
        
        def bnf_link():
            bnf_link_find = bs.find(href=bnf_a)
            if not bnf_link_find:
                return ''
            else:
                bnf_link = bnf_link_find.attrs['href']
                return bnf_link
        
        # French National Library Authorized Name
        def bnf_b(href):
            return href and re.compile(r'.*processed/BNF.*').search(href)
        
        def bnf_name():
            bnf_name_find = bs.find(href=bnf_b)
            if not bnf_name_find:
                return ''
            else:
                bnf_names = bnf_name_find.select('span')
                bnf_name_list = [i.get_text() for i in bnf_names]
                bnf_name = ' '.join(bnf_name_list)
                return bnf_name
        
    # German National Library (DNB)       
        # German National Library Link
        def dnb_a(href):
            return href and re.compile(r'.*d-nb\.info\/gnd.*').search(href)
        
        def dnb_link():
            dnb_link_find = bs.find(href=dnb_a)
            if not dnb_link_find:
                return ''
            else:
                dnb_link = dnb_link_find.attrs['href']
                return dnb_link
        
        # German National Library Authorized Name
        def dnb_b(href):
            return href and re.compile(r'.*processed/DNB.*').search(href)
        
        def dnb_name():
            dnb_name_find = bs.find(href=dnb_b)
            if not dnb_name_find:
                return ''
            else:
                dnb_names = dnb_name_find.select('span')
                dnb_list = [i.get_text() for i in dnb_names]
                dnb_name = ' '.join(dnb_list)
                return dnb_name
        
    # Central Institute for the Union Catalogue of the Italian libraries (ICCU)
        # ICCU Link
        def iccu_a(href):
            return href and re.compile(r'.*id\.sbn\.it.*').search(href)
        
        def iccu_link():
            iccu_link_find = bs.find(href=iccu_a)
            if not iccu_link_find:
                return ''
            else:
                iccu_link = iccu_link_find.attrs['href']
                return iccu_link
                
        # iCCU Authorized Name
        def iccu_b(href):
            return href and re.compile(r'.*processed/ICCU.*').search(href)
        
        def iccu_name():
            iccu_name_find = bs.find(href=iccu_b)
            if not iccu_name_find:
                return ''
            else:
                iccu_names = iccu_name_find.select('span')
                iccu_list = [i.get_text() for i in iccu_names]
                iccu_name = ' '.join(iccu_list)
                return iccu_name
            
    # National Library of Spain (BNE)
        # BNE Link
        def bne_a(href):
            return href and re.compile(r'.*catalogo\.bne\.es.*').search(href)
        
        def bne_link():
            bne_link_find = bs.find(href=bne_a)
            if not bne_link_find:
                return ''
            else:
                bne_link = bne_link_find.attrs['href']
                return bne_link
            
        # BNE Authorized Name
        def bne_b(href):
            return href and re.compile(r'.*processed/BNE').search(href)
        
        def bne_name():
            bne_name_find = bs.find(href=bne_b)
            if not bne_name_find:
                return ''
            else:
                bne_names = bne_name_find.select('span')
                bne_name_list = [i.get_text() for i in bne_names]
                bne_name = ' '.join(bne_name_list)
                return bne_name
               
        
    # Focus in on the list of links in the "About" section.
        list_of_links = bs.find('ul', id="listOfLinks")
        if not list_of_links:
            link_list = []
        else:
            link_list = []
            links = list_of_links.select('li > a')
        # Make a list of the links to search in the functions below.
            for link in links:
                link_list.append(link.get('href'))
          
        
    # Functions to filter for the different links in the About section
        # WorldCat Identities
        def worldcat():
            wc_search = re.compile(r'.*www\.worldcat\.org.*')
            worldcat_list = [i for i in filter(wc_search.match, link_list)]
            if not worldcat_list:
                return ''
            else:
                return 'https:' + worldcat_list[0]
    
        # ISNI, though we grabbed that above...
        def isni():
            isni_search = re.compile(r'.*isni\.org.*')
            isni_list = [i for i in filter(isni_search.match, link_list)]
            if not isni_list:
                return ''
            else:
                return 'http:' + isni_list[0]
        
        # Wikipedia (English)
        def wiki():
            wiki_search = re.compile(r'.*en\.wikipedia\.org.*')
            wiki_list = [i for i in filter(wiki_search.match, link_list)]
            if not wiki_list:
                return ''
            else:
                return wiki_list[0]
        
        # Get the VIAF ID and Permalink        
        def viaf():
           viaf_data = bs.find('div', id="Title")
           viaf_goodness = viaf_data.select('h1')
           if not viaf_goodness:
               return ''
           else:
               viaf_id = viaf_goodness[0].text
               viaf_permalink = viaf_goodness[1].text
               return viaf_id,viaf_permalink

# Assign variables for all of the data that will go into the CSV file.      
        loc_name = loc_name()
        loc_id = loc_id()
        loc_source = loc_source()
        loc_url = loc_link()
        viaf = viaf()
        viafid = str(viaf[0].strip('\n     (Personal)'))
        viaf_perm = viaf[1]
        bne_name = bne_name()
        bne_url = bne_link()
        bnf_name = bnf_name()
        bnf_url = bnf_link()
        dnb_name = dnb_name()
        dnb_url = dnb_link()
        iccu_name = iccu_name()
        iccu_url = iccu_link()
        isni_name = isni_name()
        isni_url = isni_link()
        wiki = wiki()
        wkp_url = wkp_link()
        wc = worldcat()
        
        
# Make a list of those variables
        row = [i,loc_name,'','','','','','','','','','',loc_id,loc_source,
               loc_url,'','',viafid,viaf_perm,bne_name,bne_url,bnf_name,bnf_url,
               dnb_name,dnb_url,iccu_name,iccu_url,isni_name,isni_url,wkp_url,
               wiki,wc]

# Write the list to the CSV
        w.writerow(row)
        print(row)
# Give the viaf.org server a rest.
        time.sleep(2)