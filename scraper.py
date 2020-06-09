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


######################## ALL THE STUFF FOR AN INDIVIDUAL WEBPAGE ############################

class Webpage:
	def __init__(self, url):
		self.results = {}
		self.removal_char = [["\xb0", ''], ['\xB5', 'u']]
		self.prev_key = None
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

	def convert_to_dict(self, str_results):
		"""Takes in the raw string of the values and returns a dict of the value and units"""
		values = {}
		split_results = str_results.split()
		
		if len(split_results) == 1: # Assuming value
			try: 
				values['value'] = float(split_results[0])
			except:
				print('error with value conversion')
		elif len(split_results) == 2: # Assuming value, units
			try: 
				values['value'] = float(split_results[0])
				values['units'] = self.clean_units(split_results[1])
			except:
				print('error with simple value/units conversion')
		elif len(split_results) == 3: # Assuming max value of materials
			try: 
				values['max'] = float(split_results[1])
				values['units'] = self.clean_units(split_results[2])
			except:
				print('error with max material percentage', split_results)
		elif len(split_results) == 4: # Assuming range of material values
			try: 
				values['max'] = float(split_results[2])
				values['min'] = float(split_results[0])
				values['units'] = self.clean_units(split_results[3])
			except:
				print('error with material percentage range')
		else:
			print('Other stuff is happening that Im not ready for')
		
		
		return values

	def convert_list_to_dict(self, results_list):
		"""Takes in the raw string of the values and returns a dict of the value and units"""
		complete_list = []
		
		for interm_results in results_list:
			values = {}
			
			split_results = interm_results.split()
			
			if len(split_results) == 7: # Assuming max min of temp with list
				try: 
					values['value'] = float(split_results[0])
					values['units'] = self.clean_units(split_results[1])
					values['max temp'] = float(split_results[3])
					values['min temp'] = float(split_results[5])
					values['temp units'] = self.clean_units(split_results[6])
				except:
					print('error with 7 value temp dependent conversion')
			elif len(split_results) == 5: # Assuming list with with only max temp
				try: 
					values['value'] = float(split_results[0])
					values['units'] = self.clean_units(split_results[1])
					values['max temp'] = float(''.join(c for c in split_results[3] if c.isdigit()))
					values['temp units'] = self.clean_units(split_results[4])
				except:
					print('error with 5 value temp dependent conversion')
					print(split_results[3])
					print(split_results[3][2:])
					print(split_results)
			else:
				print('Other stuff is happening that Im not ready for')
				break
			
			complete_list.append(values)
			
		
		return complete_list

	def scrape_page(self, webpage):
		"""Gets all the data from a particular url"""
		browser.get(webpage)
		
		header_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/th')
		table_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/td')
		

		self.results['name'] = header_data[0].text

		test_stuff = browser.find_elements_by_class_name('datarowSeparator')

		self.prev_key = None
		for thing in test_stuff:
			other_stuff = thing.find_elements_by_xpath('td')
			this_key = self.clean_key(other_stuff[0].text)
			if len(this_key) > 1:
				self.results[this_key] = self.clean_data(other_stuff[1].text)
				self.prev_key = this_key
			else:
				self.results[self.prev_key] = self.more_data(other_stuff[1].text)
			

		pass_list = ['name']

		for key in self.results.keys():
			if type(self.results[key]) is list:
				self.results[key] = self.convert_list_to_dict(self.results[key])
			elif key in pass_list:
				pass
			else:
				self.results[key] = self.convert_to_dict(self.results[key])
		
		json_file = directory + '/' + self.results['name'] +'.json'
		with open(json_file, 'w', encoding='utf-8') as f:
			json.dump(json.dumps(self.results), f)

########################### THIS IS THE STUFF TO NAVIGATE THROUGH THEIR TREE ####################



########################### HERE'S WHERE ALL THE WORK BEGINS ####################################
webpages = [
		"http://www.matweb.com/search/DataSheet.aspx?MatGUID=9d1e943f7daf49ef92e1d8261a8c6fc6",
		"http://www.matweb.com/search/datasheet.aspx?MatGUID=1e1bb328dc144aa3b50d3eb9c39f8b8b",
		"http://www.matweb.com/search/datasheet.aspx?MatGUID=dd9850edc3bc4dd589f89662e0028daa",
		"http://www.matweb.com/search/DataSheet.aspx?MatGUID=0f02241c8c6c4659ba637c63928d50ac",
		]


ferrous_group = "http://www.matweb.com/Search/MaterialGroupSearch.aspx?GroupID=176"
directory = 'materialData'




for webpage in webpages:
	Webpage(webpage)
