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

import json
import string
import time

import logging
logger = logging.getLogger('scraper')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s: %(message)s')
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler('scraper.log', mode='w')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)


class Webpage:
	"""Takes a url for a matweb web page and creates a json file of all its info"""
	def __init__(self, url, directory):
		self.results = {}
		self.removal_char = [["\xb0", ''], ['\xB5', 'u']]
		self.prev_key = None
		self.pass_list = ['name']
		self.directory = directory
		self.scrape_page(url)
	
	def clean_data(self, some_text):
		"""Cleans the data for saving"""
		return some_text.strip()

	def clean_key(self, some_key):
		"""Cleans the key for the dict"""
		return some_key.strip()
	
	def clean_units(self, units):
		"""Removes all the Unicode characters from units"""
		for char in self.removal_char:
			units = units.replace(char[0], char[1])
		return units

	def more_data(self, more_text):
		"""Appends new data to the prev thing list"""
		if type(self.results[self.prev_key]) is list:
			listed_data = self.results[self.prev_key] + [self.clean_data(more_text)]
		else:
			listed_data = [self.results[self.prev_key], self.clean_data(more_text)]
		return listed_data

	def convert_static_value(self, str_results):
		"""Takes in the raw string of the values and returns a dict of the value and units"""
		values = {}
		split_results = str_results.split()
		
		if len(split_results) == 1: # Assuming value
			try: 
				values['value'] = float(split_results[0])
			except:
				logger.error('Error with value conversion {}'.format(split_results))
		elif len(split_results) == 2: # Assuming value, units
			try: 
				values['value'] = float(split_results[0])
				values['units'] = self.clean_units(split_results[1])
			except:
				logger.error('Error with simple value/units conversion {}'.format(split_results))
		elif len(split_results) == 3: # Assuming max value of materials
			try: 
				values['max'] = float(split_results[1])
				values['units'] = self.clean_units(split_results[2])
			except:
				logger.error('Error with max material percentage {}'.format(split_results))
		elif len(split_results) == 4: # Assuming range of material values
			try: 
				values['max'] = float(split_results[2])
				values['min'] = float(split_results[0])
				values['units'] = self.clean_units(split_results[3])
			except:
				logger.error('Error with material percentage range {}'.format(split_results))
		else:
			logger.error('Other stuff is happening that Im not ready for {}'.format(split_results))
		
		
		return values

	def convert_temp_dep(self, str_results):
		"""Takes in the raw string of the values and returns a dict of the value and units"""
		values = {}
		split_results = str_results.split()
		
		if len(split_results) == 7: # Assuming max min of temp with list
			try: 
				values['value'] = float(split_results[0])
				values['units'] = self.clean_units(split_results[1])
				values['max temp'] = float(split_results[3])
				values['min temp'] = float(split_results[5])
				values['temp units'] = self.clean_units(split_results[6])
			except:
				logger.error('error with 7 value temp dependent conversion {}'.format(split_results))
		elif len(split_results) == 5: # Assuming list with with only max temp
			try: 
				values['value'] = float(split_results[0])
				values['units'] = self.clean_units(split_results[1])
				values['max temp'] = float(''.join(c for c in split_results[3] if c.isdigit()))
				values['temp units'] = self.clean_units(split_results[4])
			except:
				logger.error('error with 5 value temp dependent conversion {}'.format(split_results))
		else:
			logger.error('Other stuff is happening in lists that Im not ready for {}'.format(split_results))
		
		return values

	def scrape_page(self, webpage):
		"""Gets all the data from a particular url"""
		browser.get(webpage)
		
		header_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/th')
		table_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/td')
		
		self.results['name'] = header_data[0].text
		logger.info("Processing material - {}".format(self.results['name']))
		
		material_info = browser.find_elements_by_class_name('datarowSeparator')
		
		#getting all the stuff and putting it into a usable format
		self.prev_key = None
		for row in material_info:
			row_data = row.find_elements_by_xpath('td')
			this_key = self.clean_key(row_data[0].text)
			
			if len(this_key) > 1: #string is not empty
				logger.debug("Converting - {}".format(this_key))
				self.results[this_key] = self.clean_data(row_data[1].text)
				self.prev_key = this_key
			else: #empty string means this is a continuation of previous thing
				logger.debug("No title found, appending to - {}".format(self.prev_key))
				self.results[self.prev_key] = self.more_data(row_data[1].text)
		
		#cleaning all the strings and converting them into usable stuff
		for key in self.results.keys():
			if type(self.results[key]) is list:
				self.results[key] = [self.convert_temp_dep(data_point) for data_point in self.results[key]]
			elif key in self.pass_list:
				pass
			else:
				if "@Temperature" in self.results[key]:
					self.results[key] = self.convert_temp_dep(self.results[key])
				else:
					self.results[key] = self.convert_static_value(self.results[key])
			logger.info("Found - {}:{}".format(key, self.results[key]))
		
		json_file = self.directory + '/' + self.results['name'] +'.json'
		with open(json_file, 'w', encoding='utf-8') as f:
			json.dump(json.dumps(self.results), f)


class LinkFollower:
	"""Finds all the links on a matweb group page and follows them and dumps them to json"""
	def __init__(self, base_url, directory):
		self.directory = directory
		self.url = base_url
		self.pass_list = ['[Prev Page]', '[Next Page]']
		
		self.materials = {}
		self.find_urls()
		
		
		
	def find_urls(self):
		browser.get(self.url)
		
		link_list = browser.find_elements_by_xpath('/html/body/form/div/table/tbody/tr/td/div/table/tbody/tr/td/a')
		
		for thing in link_list:
			next_mat = thing.text
			next_link = thing.get_attribute('href')
			
			if next_link is not None and next_mat not in self.pass_list:
				logger.info("Found new material - {}:{}".format(next_mat, next_link))
				self.materials[next_mat] = next_link
			
			time.sleep(1) #put this in here so we don't overload their servers
	#use this to click on to the next page
	#driver.find_element_by_partial_link_text('Next Page').click()




########################### HERE'S WHERE ALL THE WORK BEGINS ####################################
webpages = [
		"http://www.matweb.com/search/DataSheet.aspx?MatGUID=9d1e943f7daf49ef92e1d8261a8c6fc6",
		"http://www.matweb.com/search/datasheet.aspx?MatGUID=1e1bb328dc144aa3b50d3eb9c39f8b8b",
		"http://www.matweb.com/search/datasheet.aspx?MatGUID=dd9850edc3bc4dd589f89662e0028daa",
		"http://www.matweb.com/search/DataSheet.aspx?MatGUID=0f02241c8c6c4659ba637c63928d50ac",
		]


ferrous_group = "http://www.matweb.com/Search/MaterialGroupSearch.aspx?GroupID=176"
directory = 'materialData'

LinkFollower(ferrous_group, directory)


#for webpage in webpages:
	#Webpage(webpage)
