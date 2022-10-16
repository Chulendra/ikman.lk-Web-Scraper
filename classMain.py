# Task: Scraping data from the ikman.lk's vehicle section and retrieving first ten data as a JSON format

from bs4 import BeautifulSoup
import json
import requests
import urllib.parse


class WebScraper:

    def __init__(self, ad_type, number_of_ads):

        '''
        There are two types of ads. Top ads and normal ads.
        Class ids of those two ads are
        'normal--2QYVk gtm-normal-ad' and 'top-ads-container--1Jeoq gtm-top-ad'
        '''

        if ad_type.lower() == 'top':
            self.ad_type = 'top-ads-container--1Jeoq gtm-top-ad'
        else:
            self.ad_type = 'normal--2QYVk gtm-normal-ad'

        self.number_of_ads = number_of_ads

    def scrape(self, query):

        # url encoding the search query
        query = urllib.parse.quote(query)

        # The URLs which are going to be used for data scraping
        main_url = 'https://ikman.lk'
        page_url = 'https://ikman.lk/en/ads/sri-lanka/vehicles?sort=relevance&buy_now=0&urgent=0&query=' + query + '&page=1'

        # list for storing vehicle details
        vehicles = []

        # calling the url
        html_text = requests.get(page_url).text

        # parsing html body using BeautifulSoup
        soup = BeautifulSoup(html_text, 'lxml')

        # filtering list ads depending on ad_type
        all_ads = soup.find_all('li', class_=self.ad_type)

        for ad in all_ads[:self.number_of_ads]:

            # for one vehicle detail
            vehicle = {'overview': {}}

            # Extracting initial attributes
            name = ad.find('h2', class_='heading--2eONR').text
            price = ad.find('div', class_='price--3SnqI color--t0tGX').text
            location = ad.find('div', class_='description--2-ez3').text.split(',')[0].replace(' ', '')

            # Finding the new url to retrieve the data inside the add (the data we see after clicking on the ad)
            url_part = ad.find('a', href=True)
            url2 = main_url + url_part['href']

            # Getting posted date and time from that new url
            new_html_text = requests.get(url2).text
            new_soup = BeautifulSoup(new_html_text, 'lxml')
            posted_on = new_soup.find('span', class_='sub-title--37mkY').text[10:]

            # Looking for other attributes inside the ad
            # there can be one of the following class ids
            attributes = new_soup.find_all('div',
                                           class_="full-width--XovDn justify-content-flex-start--1Xozy align-items-normal--vaTgD flex-wrap-nowrap--3IpfJ flex-direction-row--27fh1 flex--3fKk1")
            if attributes == []:
                attributes = new_soup.find_all('div',
                                               class_="two-columns--19Hyo full-width--XovDn justify-content-flex-start--1Xozy align-items-normal--vaTgD flex-wrap-nowrap--3IpfJ flex-direction-row--27fh1 flex--3fKk1")

            # default values for remaining attributes
            condition = ''
            engine_capacity = ''
            year_of_manufacture = ''

            # extracting condition, engine_capacity, year_of_manufacture
            for attribute in attributes:
                if attribute.find('div', class_='word-break--2nyVq label--3oVZK').text == 'Condition: ':
                    try:
                        condition = attribute.find('span').text
                    except:
                        condition = attribute.find('div', class_='word-break--2nyVq value--1lKHt').text

                elif attribute.find('div', class_='word-break--2nyVq label--3oVZK').text == 'Year of Manufacture: ':
                    year_of_manufacture = attribute.find('span').text

                elif attribute.find('div', class_='word-break--2nyVq label--3oVZK').text == 'Engine capacity: ':
                    engine_capacity = attribute.find('div', class_='word-break--2nyVq value--1lKHt').text

            # storing to vehicle dictionary
            vehicle['overview'] = {'name': name, 'posted on': posted_on, 'posted_City': location, 'price': price,
                                   'Condition': condition, 'Engine_capacity': engine_capacity,
                                   'year_of_manufacture': year_of_manufacture, 'link': url2}

            # appending to each vehicle detail to vehicles list
            vehicles.append(vehicle)

        return vehicles


if __name__ == '__main__':

    # Search query
    query = 'Honda Vezel'

    # Scraping top ads
    top_ads_scraper = WebScraper('top', 10)
    top_ads = top_ads_scraper.scrape(query)

    # Scraping normal ads
    normal_ads_scraper = WebScraper('normal', 10 - len(top_ads))
    normal_ads = normal_ads_scraper.scrape(query)

    # Combining ads and printing
    all_ads = top_ads + normal_ads
    print(json.dumps(all_ads, indent=4))
