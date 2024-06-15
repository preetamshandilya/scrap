#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Initialize the Chrome driver
service = Service(executable_path='/usr/bin/chromedriver')


# service = Service(executable_path = '/usr/bin/chromedriver')

url = 'https://www.urbanoutfitters.com/'
driver = webdriver.Chrome(service=service)
driver.get(url)
time.sleep(3)

soup = BeautifulSoup(driver.page_source,'html.parser')
# print(soup.prettify())


# finding categories

navigation_outer_div = soup.find('div', class_='c-pwa-header-navigation-outer')

navigation_ul = navigation_outer_div.find('ul', class_='c-pwa-header-navigation')
categories = {}

for li in navigation_ul.find_all('li', class_='c-pwa-header-navigation__item'):
    toggle_div = li.find('div', class_='c-pwa-header-navigation__toggle')
    if toggle_div:
        anchor_tag = toggle_div.find('a')
        if anchor_tag:
            link = anchor_tag['href'].split('/')[-1] 
            category = anchor_tag.text.strip()
            if category not in ["Brands", "Vintage + ReMade"]:
                categories[category] = link 


print(categories)

# Function to extract product information
def get_product_info(soup):
    product_divs = soup.find_all('div', class_='o-pwa-product-tile')
    
    # Prepare lists to store product names, prices, and image links
    product_names = []
    product_prices = []
    product_images = []
    
    # Iterate over each product div to extract product names, prices, and image links
    for div in product_divs[:5]:  # Limiting to first 5 products
        price_span_tag = div.find('span', class_='c-pwa-product-price__current s-pwa-product-price__current')
        if price_span_tag:
            product_prices.append(price_span_tag.text.strip())
    
        name_tag = div.find('p', class_='o-pwa-product-tile__heading')
        if name_tag:
            product_names.append(name_tag.text.strip())
    
        picture_tag = div.find('picture', class_='o-pwa-image o-pwa-product-tile__media is-loaded')
        if picture_tag:
            img_tag = picture_tag.find('img')
            if img_tag and 'src' in img_tag.attrs:
                product_images.append(img_tag['src'])

    return product_names, product_prices, product_images

# Function to get all pagination links
def get_all_pagination_links(soup):
    pagination_links = []
    nav_tag = soup.find('nav', class_='o-pwa-pagination-outer')
    if nav_tag:
        ul_tag = nav_tag.find('ul', class_='o-pwa-pagination')
        if ul_tag:
            for li_tag in ul_tag.find_all('li'):
                a_tag = li_tag.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    pagination_links.append(a_tag['href'])
    return pagination_links

# Function to get the next unvisited pagination link
def get_next_unvisited_link(soup, base_url, visited_links):
    pagination_links = get_all_pagination_links(soup)
    for link in pagination_links:
        full_link = base_url + link
        if full_link not in visited_links:
            return full_link
    return None

base_url = 'https://www.urbanoutfitters.com/'
initial_url = base_url + 'womens-clothing'

driver = webdriver.Chrome(service=service)
driver.get(initial_url)
time.sleep(3)  

# Store all product information
all_product_names = []
all_product_prices = []
all_product_images = []

# List to store all the visited links
visited_links = set()

# Loop to visit unvisited pagination links
while True:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_names, product_prices, product_images = get_product_info(soup)
    
    all_product_names.extend(product_names)
    all_product_prices.extend(product_prices)
    all_product_images.extend(product_images)

    visited_links.add(driver.current_url)
    next_link = get_next_unvisited_link(soup, base_url, visited_links)
    
    if not next_link:
        break
    
    driver.get(next_link)
    time.sleep(3) 

print("Product Names:")
for name in all_product_names:
    print(name)

print("\nProduct Prices:")
for price in all_product_prices:
    print(price)

print("\nProduct Images:")
for image in all_product_images:
    print(image)

driver.quit()

