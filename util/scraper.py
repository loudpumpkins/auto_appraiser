import csv
import os
from selenium.common.exceptions import (NoSuchElementException,
                                        ElementNotInteractableException)

from selenium2 import Browser


def links_generator():
	"""
	Navigate through www.kijiji.ca to find as many ads for Hondas as possible in
	Ontario. Yields one unique link at a time.
	"""
	processed_links = set()
	driver = Browser('ff')
	driver.goto('https://www.kijiji.ca/b-cars-trucks/ontario/honda-new__used/c174l9004a54a49')

	while True:
		links = driver.find_elements('//a[@class="title "]')
		for link in links:
			if link.get_attribute('href') not in processed_links:
				processed_links.add(link.get_attribute('href'))
				yield link.get_attribute('href')

		try:
			# go to the next page for more links
			driver.find_element('//a[@title="Next"]').click()
		except NoSuchElementException:
			break


def get_processed_links(filename, csv_fieldnames):
	"""
	Go through the 'raw_data.csv' file to find all the links that have already
	been processed.
	"""
	with open(filename, mode='r', newline='') as csv_fd:
		reader = csv.DictReader(csv_fd, fieldnames=csv_fieldnames)
		return {row['link'] for row in reader}


if __name__ == '__main__':
	"""
	Go to 'kijiji.ca', a Canadian classified ads website, to fetch live ads of 
	vehicles for sell in Ontario.
	"""
	csv_fieldnames = ['link', 'price', 'make', 'model', 'year', 'kilometres',
	                  'body_type', 'drivetrain', 'transmission', 'fuel_type',
	                  'trim', 'colour', 'description']

	raw_data_filename = 'raw_data.csv'
	if not os.path.exists(raw_data_filename):
		with open(raw_data_filename, 'w'):
			pass

	browser = Browser('ff')
	processed_links = get_processed_links(raw_data_filename, csv_fieldnames)
	for link in links_generator():
		if link in processed_links:
			continue
		processed_links.add(link)
		browser.goto(link)
		row = dict()
		row['link'] = link
		try:
			more_btn = browser.find_element(
				"//button[starts-with(@class, 'showMoreButton')]")
			browser.driver.execute_script("arguments[0].scrollIntoView(false);",
			                              more_btn)
			more_btn.click()
		except (ElementNotInteractableException, NoSuchElementException):
			pass

		fields = {
			'price': '//span[@itemprop="price"]',  # '$38,940.00'
			'body_type': '//dd[@itemprop="bodyType"]/a',  # 'Sedan'
			'drivetrain': '//dd[@itemprop="driveWheelConfiguration"]',  # 'Front-wheel drive (FWD)'
			'transmission': '//dd[@itemprop="vehicleTransmission"]',  # 'Automatic'
			'fuel_type': '//dd[@itemprop="fuelType"]',  # 'Other'
			'kilometres': '//dd[@itemprop="mileageFromOdometer"]',  # '151,543'
			'year': '//dd[@itemprop="vehicleModelDate"]/a',  # '2013'
			'make': '//dd[@itemprop="brand"]/a',  # 'Honda'
			'model': '//dd[@itemprop="model"]/a',  # 'Civic'
			'trim': '//dd[@itemprop="vehicleConfiguration"]',  # Trim; 'El'
			'colour': '//dd[@itemprop="color"]',  # 'White'
			'description': '//div[@itemprop="description"]',  # ''
		}

		for key, value in fields.items():
			try:
				row[key] = browser.find_element(value).text
			except NoSuchElementException:
				row[key] = 'None'
			except UnicodeEncodeError:
				row[key] = 'Unicode Error'

		with open(raw_data_filename, mode='a', newline='') as csv_fd:
			try:
				writer = csv.DictWriter(csv_fd, fieldnames=csv_fieldnames)
				writer.writerow(row)
			except UnicodeEncodeError:
				print(row)
