import csv
import re


def load_data(filename, csv_fieldnames):
	with open(filename, mode='r', newline='', encoding='utf-8') as csv_fd:
		reader = csv.DictReader(csv_fd, fieldnames=csv_fieldnames)
		return [row for row in reader]


def write_row(row, filename, csv_fieldnames):
	with open(filename, mode='a', newline='', encoding='utf-8') as csv_fd:
		writer = csv.DictWriter(csv_fd, fieldnames=csv_fieldnames)
		writer.writerow(row)


def load_json(url):
	import urllib.request, json
	with urllib.request.urlopen(url) as url:
		return json.loads(url.read().decode())


def get_price(row):
	"""
	Extract the price of a vehicle.
	Reject listings with no set price such as 'please call', 'free', 'swap/trade'.

	Vehicles from 2015 and up, sold for under $2000 are considered 'lease takeover'
	or 'salvage' and will be rejected.

	Vehicles sold for over $70000 are outliers and will be rejected as well.
	"""
	if re.search("^\$(\d{1,3},\d{3}|\d{1,3})(\.\d{2})?$", row['price']):
		# Allowed pattern: $(xxx,)xxx.xx | $(xxx,)xxx
		price = int(float(row['price'].replace('$', '').replace(',', '')))
		if get_year(row) >= 2015 and price <= 2000:
			raise AttributeError("price", "Rejected suspected lease-takeover listing.")
		elif price > 70000:
			raise AttributeError("price", "Rejected outlier.")
		else:
			return price
	raise AttributeError("price", "Invalid price field.")


def get_kilometers(row):
	"""
	Extract the mileage of a vehicle.

	I assume that vehicles with over two million kilometres are user input
	errors, and an extra zero was likely added, so this is correct.

	We assume that vehicles from 2015 and before with less than 1000 kilometres
	have had their mileage abbreviated.
	"""
	try:
		km = int(row['kilometres'].replace(',', ''))
		if km > 2_000_000:
			# suspected user input error - 3,500,000 km is likely 350,000 km
			return km/10
		elif km < 1_000 and get_year(row) <= 2015:
			# suspected abbreviated km - 200 km in a 2015 vehicle is likely 200_000 km
			return km * 1_000
		else:
			return km
	except ValueError:
		raise AttributeError("kilometres", "Invalid kilometres.")


def get_year(row):
	""" Year is a mandatory field and must be between 1978 and 2022 """
	try:
		year = int(row['year'])
		if 1978 <= year <= 2022:
			return year
	except ValueError:
		pass
	raise AttributeError("year", "Year is not between 1978 - 2022.")


def get_model(row):
	"""
	The vehicle's model is a mandatory field and for each row only one model
	can be set to 1. The remainder are all set to 0 by default.
	"""
	allowed_models = ['other', 'crosstour', 'fit', 'civic', 'ridgeline',
	                  'del sol', 'accord', 'passport', 'odyssey', 'insight',
	                  's2000', 'cr-z', 'accord crosstour', 'hr-v', 'element',
	                  'cr-v', 'prelude', 'pilot']
	if row['model'].lower() in allowed_models:
		return row['model'].lower()


def is_sport(row):
	""" Return 1 if the vehicle is confirmed to be a sports edition """
	keywords = ['si', 'sir', 'sr', 'sport', 'sports', 'vtec', 'turbo', '2.0t']
	for keyword in keywords:
		if re.search(f"( |-|\*|\||^){keyword}( |-|\.|\*|\||$)", row['trim'].lower()):
			# will match patterns where the keyword is surrounded by common
			# delimiters. eg: 'Si|sunroof|AWD' or '4dr-sedan-sports'
			return 1
	return 0


def is_leather(row):
	""" Has leather seats or not """
	fields = ['trim', 'description']
	for field in fields:
		if re.search("( |-|\*|\||^)leather( |-|\.|\*|\||$)", row[field].lower()):
			return 1
	return 0


def is_automatic(row):
	""" Has an automatic transmission. 1: automatic, 0: manual"""
	if row['transmission'].lower() == 'automatic':
		return 1
	elif row['transmission'].lower() == 'manual':
		return 0
	elif 'manual' in row['trim'].lower() or 'manual' in row['description'].lower():
		return 0
	return 1  # if not mentioned, assume automatic transmission


def is_awd(row):
	""" Has All-wheel-drive? AWD or 4x4: 1, FWD or RWD: 0"""
	TWD = ['front-wheel drive', 'rear-wheel drive', 'fwd', 'rwd']
	AWD = ['all-wheel drive', 'awd', '4x4', '4 x 4']
	search_sources = [row['drivetrain'].lower(), row['trim'].lower(), row['description'].lower()]
	for search_source in search_sources:
		for awd in AWD:
			if awd in search_source:
				return 1
		for twd in TWD:
			if twd in search_source:
				return 0
	return 0  # if not mentioned, assume two-wheel drive


if __name__ == '__main__':
	raw_csv_fields = ['link', 'price', 'make', 'model', 'year', 'kilometres',
	                  'body_type', 'drivetrain', 'transmission', 'fuel_type',
	                  'trim', 'colour', 'description']
	clean_csv_fields = ['price', 'kilometres', 'year',
	                    # models
	                    'other', 'crosstour', 'fit', 'civic', 'ridgeline',
	                    'del sol', 'accord', 'passport', 'odyssey', 'insight',
	                    's2000', 'cr-z', 'accord crosstour', 'hr-v', 'element',
	                    'cr-v', 'prelude', 'pilot',
	                    # other features
	                    'sport', 'leather', 'automatic', 'awd']

	raw_data = load_data('raw_data_utf8.csv', raw_csv_fields)
	rejected = set()
	accepted = []

	with open('clean_data.csv', mode='a', newline='', encoding='utf-8') as csv_fd:
		writer = csv.DictWriter(csv_fd, fieldnames=clean_csv_fields)
		for row in raw_data:
			try:
				clean_row = {field: 0 for field in clean_csv_fields}
				clean_row['price'] = get_price(row)
				clean_row['kilometres'] = get_kilometers(row)
				clean_row['year'] = get_year(row)
				clean_row[get_model(row)] = 1
				clean_row['sport'] = is_sport(row)
				clean_row['leather'] = is_leather(row)
				clean_row['automatic'] = is_automatic(row)
				clean_row['awd'] = is_awd(row)
				writer.writerow(clean_row)
			except AttributeError as err:
				rejected.add(f"Rejected field: '{err.args[0]}' with value: "
				             f"'{row[err.args[0]]}' (msg: '{err.args[1]}')")

	for rejected_row in sorted(rejected):
		print(rejected_row)