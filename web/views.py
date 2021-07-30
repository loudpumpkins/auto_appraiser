import csv
import json

from django.http import HttpResponse, HttpResponseNotFound

from web.models import Data


def index(request):
	pass


def get_data(request, file):
	csv_fieldnames = ['link', 'price', 'make', 'model', 'year', 'kilometres',
	                  'body_type', 'drivetrain', 'transmission', 'fuel_type',
	                  'trim', 'colour', 'description']
	csv_files = Data.objects.all().first()
	if file.lower() == 'raw':
		csv_file = csv_files.raw_csv.open(mode='r')
	elif file.lower() == 'clean':
		csv_file = csv_files.clean_csv.open(mode='r')
	else:
		return HttpResponseNotFound('<h1>Data not found</h1>')

	reader = csv.DictReader(csv_file, fieldnames=csv_fieldnames)
	json_pretty = json.dumps([row for row in reader], indent=4)
	return HttpResponse(json_pretty, content_type="application/json")
