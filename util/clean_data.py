import csv
import matplotlib.pyplot as plt
import re


def load_data(filename, csv_fieldnames):
	with open(filename, mode='r', newline='') as csv_fd:
		reader = csv.DictReader(csv_fd, fieldnames=csv_fieldnames)
		return [row for row in reader]


def write_row(row, filename, csv_fieldnames):
	with open(filename, mode='a', newline='') as csv_fd:
		writer = csv.DictWriter(csv_fd, fieldnames=csv_fieldnames)
		writer.writerow(row)


def load_json(url):
	import urllib.request, json
	with urllib.request.urlopen(url) as url:
		return json.loads(url.read().decode())


if __name__ == '__main__':
	csv_fieldnames = ['link', 'price', 'make', 'model', 'year', 'kilometres',
	                  'body_type', 'drivetrain', 'transmission', 'fuel_type',
	                  'trim', 'colour', 'description']
	data = load_data('raw_data.csv', csv_fieldnames)
	# data = load_json("http://localhost:8000/data/raw")

	rejected = set()
	prices = []
	for row in data:
		price = row['price']
		if re.search("^\$(\d{1,3},\d{3}|\d{1,3})(\.\d{2})?$", price):
			# Assumed pattern: $(xxx,)xxx.xx | $(xxx,)xxx
			row['price'] = int(float(price.replace('$', '').replace(',', '')))
			write_row(row, 'clean_data_price.csv', csv_fieldnames)
			# prices.append(int(float(price.replace('$', '').replace(',', ''))))
		else:
			rejected.add(price)

	fig = plt.figure(figsize=(3, 4))
	plt.boxplot(prices)
	plt.show()
	print(rejected)
