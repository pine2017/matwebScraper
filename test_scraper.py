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

def convert_to_dict(results):
	"""Takes in the raw string of the values and returns a dict of the value and units"""
	values = {}
	split_results = results.split()
	
	if len(split_results) == 1: # Assuming value
		try: 
			values['value'] = float(split_results[0])
		except:
			print('error with value conversion')
	elif len(split_results) == 2: # Assuming value, units
		try: 
			values['value'] = float(split_results[0])
			values['units'] = split_results[1]
		except:
			print('error with simple value/units conversion')
	elif len(split_results) == 3: # Assuming max value of materials
		try: 
			values['max'] = float(split_results[1])
			values['units'] = split_results[2]
		except:
			print('error with max material percentage')
	elif len(split_results) == 4: # Assuming range of material values
		try: 
			values['max'] = float(split_results[2])
			values['min'] = float(split_results[0])
			values['units'] = split_results[3]
		except:
			print('error with material percentage range')
	else:
		print('Other stuff is happening that Im not ready for')
	
	
	return values

def convert_list_to_dict(results_list):
	"""Takes in the raw string of the values and returns a dict of the value and units"""
	complete_list = []
	
	for results in results_list:
		values = {}
		
		split_results = results.split()
		
		if len(split_results) == 7: # Assuming max min of temp with list
			try: 
				values['value'] = float(split_results[0])
				values['units'] = split_results[1]
				values['max temp'] = float(split_results[3])
				values['min temp'] = float(split_results[5])
				values['temp units'] = split_results[6]
			except:
				print('error with 7 value temp dependent conversion')
		elif len(split_results) == 5: # Assuming list with with only max temp
			try: 
				values['value'] = float(split_results[0])
				values['units'] = split_results[1]
				values['max temp'] = float(split_results[3])
				values['temp units'] = split_results[4]
			except:
				print('error with 5 value temp dependent conversion')
		else:
			print('Other stuff is happening that Im not ready for')
			break
		
		complete_list.append(values)
		
	
	return complete_list




webpages = [
		"http://www.matweb.com/search/DataSheet.aspx?MatGUID=9d1e943f7daf49ef92e1d8261a8c6fc6",
		"http://www.matweb.com/search/datasheet.aspx?MatGUID=1e1bb328dc144aa3b50d3eb9c39f8b8b",
		"http://www.matweb.com/search/datasheet.aspx?MatGUID=dd9850edc3bc4dd589f89662e0028daa",
		]

for webpage in webpages:
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
		


	pass_list = ['name']

	for key in results.keys():
		if type(results[key]) is list:
			results[key] = convert_list_to_dict(results[key])
		elif key in pass_list:
			pass
		else:
			results[key] = convert_to_dict(results[key])

	print(results)
