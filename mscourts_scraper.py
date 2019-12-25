# !/usr/bin/env python3
"""This module does blah blah."""
import time
import requests
from bs4 import BeautifulSoup
from ..jail_scrapers.common import airtab_courts as airtab, muh_headers, wrap_from_module


wrap_it_up = wrap_from_module('mscourts_scraper.py')


def legacy_scrape():
    years = list(range(2006, 2019))
    for yr in years:
        this_url = f"https://courts.ms.gov/news/news_{yr}.php"
        print(this_url)
        r = requests.get(this_url, headers=muh_headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.table.find_all('tr')
        for row in rows:
            this_dict = {'type': 'news'}
            try:
                this_dict['raw_url'] = row.a.get('href')
            except AttributeError:
                this_dict['raw_url'] = row.get_text()
            try:
                this_dict['raw_title'] = row.find('a').get_text()
            except AttributeError:
                this_dict['raw_title'] = row.get_text()
            try:
                this_dict['raw_date'] = row.find('em').get_text()
            except AttributeError:
                this_dict['raw_date'] = row.get_text()
            try:
                this_dict['raw_description'] = row.p.get_text()
            except AttributeError:
                this_dict['raw_description'] = row.get_text()
            airtab.insert(this_dict)
            time.sleep(.5)


def scrape_court_news():
    url, t0, i = 'https://courts.ms.gov/news/news.php', time.time(), 0
    r = requests.get(url, headers=muh_headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.table.find_all('tr')
    for row in rows:
        this_dict = {'type': 'news'}
        raw_url = row.a.get('href')
        if raw_url.startswith('../'):
            this_dict['raw_url'] = raw_url.replace('../', 'https://courts.ms.gov/')
        elif raw_url.startswith('/news'):
            this_dict['raw_url'] = f"https://courts.ms.gov{raw_url}"
        elif raw_url.startswith('20'):
            this_dict['raw_url'] = f"https://courts.ms.gov/news/{raw_url}"
        elif raw_url.startswith('http'):
            this_dict['raw_url'] = raw_url
        else:
            pass
        this_dict['url'] = this_dict['raw_url'].replace(' ', '%20')
        this_dict['raw_title'] = row.a.string.strip()
        this_dict['raw_date'] = row.find('span', class_='newsdatetext').get_text().strip()
        this_dict['raw_description'] = row.p.string.strip()
        m = airtab.match('raw_url', this_dict['raw_url'])
        if not m:
            airtab.insert(this_dict)
            i += 1
        else:
            airtab.update(m['id'], this_dict)
        time.sleep(.2)
    wrap_it_up(t0, new=i, total=len(rows), function='scrape_court_news')


def scrape_court_newsletters():
    url, t0, i = 'https://courts.ms.gov/news/newsletters/newsletters.php', time.time(), 0
    r = requests.get(url, headers=muh_headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.table.find_all('tr')
    for row in rows:
        stripped_strings = list(row.stripped_strings)
        this_dict = {'type': 'newsletter'}
        raw_url = row.a.get('href')
        if raw_url.startswith('MS '):
            this_dict['raw_url'] = f"https://courts.ms.gov/news/newsletters/{raw_url}"
        elif raw_url.startswith('../../news/newsletters/'):
            this_dict['raw_url'] = raw_url.replace('../../', 'https://courts.ms.gov/')
        else:
            pass
        this_dict['url'] = this_dict['raw_url'].replace(' ', '%20')
        this_dict['raw_title'] = stripped_strings[0]
        this_dict['raw_src'] = row.img.get('src')
        this_dict['raw_caption'] = stripped_strings[1]
        this_dict['raw_date'] = this_dict['raw_title'].split('-')[1].strip()
        this_dict['raw_description'] = stripped_strings[2]
        m = airtab.match('raw_url', this_dict['raw_url'])
        if not m:
            i += 1
            airtab.insert(this_dict)
        else:
            airtab.update(m['id'], this_dict)
        time.sleep(.2)
    wrap_it_up(t0, new=i, total=len(rows), function='scrape_court_newsletters')


def get_full_news_release():
    t0, i = time.time(), 0
    records = airtab.get_all(formula="AND(type = 'news', yr = '2019', full_text = '')")
    print(len(records))
    for record in records:
        r = requests.get(record['fields']['url'], headers=muh_headers)
        if r.status_code != requests.codes.ok:
            return {}, f'Got bad status code in response: {r.status_code}'
        soup = BeautifulSoup(r.text, 'html.parser')
        this_dict = {'html': soup.table.prettify()}
        try:
            this_dict['full_text'] = soup.table.get_text()
        except AttributeError as err:
            print(err)
        pic = soup.find('img')
        if pic:
            img_url = soup.img.get('src')
            this_dict["img"] = [{"url": img_url}]
        airtab.update(record["id"], this_dict)
        i += 1
    wrap_it_up(t0, new=i, total=len(records), function='get_pixelated_mug')


def scrape_court_reports():
    url, t0, i = 'https://courts.ms.gov/research/reports/reports.php', time.time(), 0
    r = requests.get(url, headers=muh_headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('td')
    for row in rows:
        this_dict = {'type': 'reports'}
        raw_url = row.a.get('href')
        this_dict['raw_url'] = raw_url.replace('../../research', 'https://courts.ms.gov/research')
        this_dict['url'] = this_dict['raw_url'].replace(' ', '%20')
        this_dict['raw_title'] = row.a.string
        m = airtab.match('url', this_dict['url'])
        if not m:
            i += 1
            airtab.insert(this_dict)
    wrap_it_up(t0, new=i, total=len(rows), function='scrape_msaoc_reports')

