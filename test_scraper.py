from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
opts = Options()
opts.set_headless()
assert opts.headless  # Operating in headless mode
browser = Firefox(executable_path='./geckodriver', options=opts)


def clean_data(some_text):
	"""Cleans the data for saving"""
	return some_text.strip()

def clean_key(some_key):
	"""Cleans the key for the dict"""
	return some_key.strip()

def more_data(more_text):
	"""Appends new data to the prev thing list"""
	if type(results[prev_key]) is list:
		#print('its a list')
		#print(results[prev_key] + [clean_data(more_text)])
		listed_data = results[prev_key] + [clean_data(more_text)]
	else:
		#print('its not a list')
		listed_data = [results[prev_key], clean_data(more_text)]
	return listed_data
	
#webpage = "http://www.matweb.com/search/DataSheet.aspx?MatGUID=9d1e943f7daf49ef92e1d8261a8c6fc6"
webpage = "http://www.matweb.com/search/datasheet.aspx?MatGUID=1e1bb328dc144aa3b50d3eb9c39f8b8b"
browser.get(webpage)

header_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/th')
table_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/td')


results = {}
results['name'] = header_data[0].text

test_stuff = browser.find_elements_by_class_name('datarowSeparator')

prev_key = None
for thing in test_stuff:
	other_stuff = thing.find_elements_by_xpath('td')
	this_key = clean_key(other_stuff[0].text)
	if len(this_key) > 1:
		results[this_key] = clean_data(other_stuff[1].text)
		prev_key = this_key
	else:
		results[prev_key] = more_data(other_stuff[1].text)
	



print(results)
