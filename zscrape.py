import sys
sys.path.append('/anaconda3/lib/python3.7/site-packages/')

import requests
import re
import json
import sys
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

def get_query(page, regionID, min_price, max_price, sfh_only=True):

	query = json.dumps({
		"pagination": {"currentPage":page},
		"customRegionId": regionID,
		"filterState": {
		"isManufactured":{"value":"false"}, "isCondo":{"value":"false"},"isMultiFamily":{"value":"false"},
		"isApartment":{"value":"false"},"isLotLand":{"value":"false"}, "isTownhouse":{"value":"false"},
		"price":{"max":max_price,"min":min_price}}}).replace(' ', '').replace('\"', '')

	if page == 1:
		url = 'https://www.zillow.com/homes/for_sale/house_type/?searchQueryState=' + query
	else:
		url = 'https://www.zillow.com/homes/for_sale/house_type/{0}_p/?searchQueryState='.format(page) + query

	return url

def get_driver(location):
	chromedriver = location
	sys.path.append(chromedriver)
	chrome_options = Options()
	chrome_options.add_argument("user-data-dir=selenium")

	return webdriver.Chrome(options=chrome_options, executable_path = location)


def get_html(driver, url):
	driver.get(url)
	return driver.page_source

def extract_json(html):
	return (re.search('\"listResults\":\[([\s\S]*?)],\"hasListResults\"', html).group(1))

def extract_rc(html):
	return int(re.search('<span class="result-count">(\d+,\d+|\d+) results</span>', html).group(1).replace(',', ''))

def current_page(url):
	try:
		return int(re.search('/house_type/(\d+)_p/?', url).group(1))
	except AttributeError:
		return 1

def next_page(url, current_page):
	if current_page == 1:
		temp = re.sub('/house_type/\?searchQuery', '/house_type/2_p/?searchQuery', url)
		return re.sub('{currentPage:(\d*)}', '{currentPage:2}', temp)
	else:
		temp = re.sub('/house_type/(\d+)_p/', '/house_type/%d_p/' % (current_page + 1), url)
		return re.sub('{currentPage:(\d*)}', '{currentPage:%d}' % (current_page + 1), temp)

def output_csv(location, data):

	with open(location, 'a', encoding="utf-8") as output:
		size = os.path.getsize(os.getcwd() + '/' + location)
		output.write(data + '\n\n')
		print('writing json')

	print('%d bytes written' % (os.path.getsize(os.getcwd() + '/' + location) - size))

def scrape(driver, url):
	print(url)
	time.sleep(random.random() * 10)

	try:
		html = get_html(driver, url)
		rc = extract_rc(html)
	except AttributeError:
		captcha = input('Press any key + enter when captcha complete')
		time.sleep(random.random() * 10)
		html = get_html(driver, url)
		rc = extract_rc(html)

	if rc > 800:

		price_search = re.search('price:{max:(\d+),min:(\d+)}', url)
		max_price = int(price_search.group(1))
		min_price = int(price_search.group(2))
		interval = 1000

		for i in range(min_price-1 + interval, max_price, interval):
			next_url = re.sub('price:{max:(\d+),min:(\d+)}', 'price:{max:%d,min:%d}' % (i, i-999), url)
			scrape(driver, next_url)

		return

	if rc > (current_page(url) * 40):
		scrape(driver, next_page(url, current_page(url)))	

	output_csv('jsons2.txt', extract_json(html))

if __name__ == '__main__':
	url = "https://www.zillow.com/blaine-mn/luxury-homes/?searchQueryState={%22pagination%22:{},%22usersSearchTerm%22:%22Blaine,%20MN%22,%22mapBounds%22:{%22west%22:-93.29565952978515,%22east%22:-93.11369847021484,%22south%22:45.10022942668798,%22north%22:45.2302181267963},%22regionSelection%22:[{%22regionId%22:10428,%22regionType%22:6}],%22isMapVisible%22:true,%22mapZoom%22:12,%22filterState%22:{%22sortSelection%22:{%22value%22:%22priced%22},%22isPreMarketForeclosure%22:{%22value%22:false},%22isPreMarketPreForeclosure%22:{%22value%22:false}},%22isListVisible%22:true}"
	#get_query(1, "917c25dfd6X1-CR1nk482x6hl3zy_11m3tt", 50000, 350000)
	#scrape(get_driver("C:/Users/rami/Downloads/chromedriver_win32/chromedriver.exe"), url) ORIGINAL
	scrape(get_driver("/users/ramiqamhieh/Desktop/Programs/Program Apps/chromedriver"), url)


