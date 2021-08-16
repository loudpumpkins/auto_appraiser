import csv
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from web.models import Data


def index(request):
	pass


def get_data(request, file):
	csv_files = Data.objects.all().first()
	if file.lower() == 'raw':
		file_path = settings.MEDIA_ROOT / csv_files.raw_csv.path
		csv_fieldnames = ['link', 'price', 'make', 'model', 'year',
		                  'kilometres', 'body_type', 'drivetrain',
		                  'transmission', 'fuel_type', 'trim', 'colour',
		                  'description']
	elif file.lower() == 'clean':
		file_path = settings.MEDIA_ROOT / csv_files.clean_csv.path
		csv_fieldnames = ['price', 'kilometres', 'year', 'other', 'crosstour',
		                  'fit', 'civic', 'ridgeline', 'del sol', 'accord',
		                  'passport', 'odyssey', 'insight', 's2000', 'cr-z',
		                  'accord crosstour', 'hr-v', 'element', 'cr-v',
		                  'prelude', 'pilot', 'sport', 'leather', 'automatic',
		                  'awd']
	else:
		return HttpResponseNotFound('<h1>Data not found</h1>')

	with open(file_path, mode='r', encoding='utf-8') as fd:
		reader = csv.DictReader(fd, fieldnames=csv_fieldnames)
		json_pretty = json.dumps([row for row in reader], indent=4)
	return HttpResponse(json_pretty, content_type="application/json")
