#!/usr/bin/env /python
"""This module provides a function for shipping logs to Airtable."""

import os
import time
from airtable import Airtable
import cloudinary
from documentcloud import DocumentCloud


airtab_log = Airtable(os.environ['log_db'],
                      table_name='log',
                      api_key=os.environ['AIRTABLE_API_KEY'])

airtab_courts = Airtable(os.environ['other_scrapers_db'],
                         table_name='courts',
                         api_key=os.environ['AIRTABLE_API_KEY'])

airtab_tweets = Airtable(os.environ['botfeldman89_db'],
                         table_name='scheduled_tweets',
                         api_key=os.environ['AIRTABLE_API_KEY'])

cloudinary.config(cloud_name='bfeldman89',
                  api_key=os.environ['CLOUDINARY_API_KEY'],
                  api_secret=os.environ['CLOUDINARY_API_SECRET'])

dc = DocumentCloud(username=os.environ['MUCKROCK_USERNAME'],
                   password=os.environ['MUCKROCK_PW'])


muh_headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

my_funcs = {'scrape_court_news': 'receET4GbZsIHZ1ap',
            'scrape_court_newsletters': 'recl93NdV0nvxiP6B',
            'scrape_court_reports': 'rec6iaRXOshuZ3OwY',
            'get_full_news_release': 'recwiYi77Mq1USCfh'}

def wrap_from_module(module):
    def wrap_it_up(t0, new=None, total=None, function=None):
        this_dict = {
            'module': module,
            'function': function,
            '_function': my_funcs[function],
            'duration': round(time.time() - t0, 2),
            'total': total,
            'new': new
        }
        airtab_log.insert(this_dict, typecast=True)

    return wrap_it_up
