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


#webpage = "http://www.matweb.com/search/DataSheet.aspx?MatGUID=9d1e943f7daf49ef92e1d8261a8c6fc6"
webpage = "http://www.matweb.com/search/datasheet.aspx?MatGUID=1e1bb328dc144aa3b50d3eb9c39f8b8b"
browser.get(webpage)

header_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/th')
table_data = browser.find_elements_by_xpath('/html/body/form/div/div/table/tbody/tr/td')


results = {}
results['name'] = header_data[0].text

test_stuff = browser.find_elements_by_class_name('datarowSeparator')

for thing in test_stuff:
	other_stuff = thing.find_elements_by_xpath('td')
	results[other_stuff[0].text.strip()] = other_stuff[1].text.strip()


#table_id = browser.find_elements_by_xpath('/html/body/form/div/div/table')


print(results)
