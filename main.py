#Task: Scraping data from the ikman.lk's vehicle section and retrieving data inside the ads also
#Contributor's Name: Ranmal Mendis

from bs4 import BeautifulSoup
import json
import requests
import urllib.parse

# class ikman_vehicle_details:
#     def __init__(self, ad_list_type, NumberofPages):
#         self.ad_list_type = ad_list_type
#         self.NumberofPages


def ikman_vehicle_details(query,ad_list_type,number_of_ads):

    # The URLs which are going to be used for data scraping

    query = urllib.parse.quote(query)
    main_url = 'https://ikman.lk'

    # page_url = 'https://ikman.lk/en/ads/sri-lanka/vehicles?sort=date&order=desc&buy_now=0&urgent=0&page='
    page_url = 'https://ikman.lk/en/ads/sri-lanka/vehicles?sort=relevance&buy_now=0&urgent=0&query=' + query + '&page=1'

    vehicles = []

    # print(page_url)

    html_text = requests.get(page_url).text

    soup = BeautifulSoup(html_text, 'lxml')

    # There are two types of ads. Top ads and normal ads. Here one fuction was defined for data
    # scraping from ikman.lk's vehicle section.For that function the class id of the list element was passed as the parameter.
    # Class ids of those two's list element were 'top-ads-container--1Jeoq gtm-top-ad'
    # and 'normal--2QYVk gtm-normal-ad' and 'top-ads-container--1Jeoq gtm-top-ad'

    # created a dictionary to store data

    all_ads=soup.find_all('li', class_=ad_list_type)

    for ad in all_ads[:number_of_ads]:

        vehicle = {'overview': {}}

        #Assigning the retrieved values to the variables
        name= ad.find('h2',class_='heading--2eONR').text
        price= ad.find('div',class_='price--3SnqI color--t0tGX').text
        location= ad.find('div',class_='description--2-ez3').text.split(',')[0].replace(' ','')

        #Finding the new url to retrieve the data inside the add (the data we see after clicking on the ad)
        url_part=ad.find('a', href=True)
        url2=main_url+url_part['href']

        #Getting the description and posted date and time from that new url
        new_html_text = requests.get(url2).text
        new_soup = BeautifulSoup(new_html_text, 'lxml')
        #description = new_soup.find('div', class_='description--1nRbz').text
        posted_on= new_soup.find('span',class_='sub-title--37mkY').text[10:]

        #Condition
        attributes = new_soup.find_all('div', class_="full-width--XovDn justify-content-flex-start--1Xozy align-items-normal--vaTgD flex-wrap-nowrap--3IpfJ flex-direction-row--27fh1 flex--3fKk1")
        if attributes == []:
            attributes = new_soup.find_all('div', class_="two-columns--19Hyo full-width--XovDn justify-content-flex-start--1Xozy align-items-normal--vaTgD flex-wrap-nowrap--3IpfJ flex-direction-row--27fh1 flex--3fKk1")

        condition = ''
        engine_capacity = ''
        year_of_manufacture = ''

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


        # print(condition)
        # print(engine_capacity)
        # print(year_of_manufacture)

        #Adding new data
        vehicle['overview'] = {'name': name, 'posted on': posted_on, 'posted_City': location, 'price': price, 'Condition': condition, 'Engine_capacity': engine_capacity, 'year_of_manufacture': year_of_manufacture, 'link': url2}
        vehicles.append(vehicle)

    # print(json.dumps(vehicles, indent=4))

    return vehicles


# Calling the fuction to print the Top Ads
print("######### Top Ads ###########")
top_ads = ikman_vehicle_details('honda vezel', 'top-ads-container--1Jeoq gtm-top-ad', 10)

# Calling the fuction to print the Normal Ads
print("######### Normal Ads ############")
normal_ads = ikman_vehicle_details('honda vezel','normal--2QYVk gtm-normal-ad', 10 - len(top_ads))

print("######### All Ads ############")
all_ads = top_ads + normal_ads
print(json.dumps(all_ads, indent=4))
