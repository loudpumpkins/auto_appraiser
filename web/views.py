import csv
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.template.response import TemplateResponse

from web.apps import WebConfig
from web.models import Data


def index(request):

	message = False
	form = {
		'model': False,
		'year': False,
		'kilometres': False,
		'transmission': False,
		'drivetrain': False,
		'sport': False,
		'leather': False,
	}

	if request.method == 'POST':
		form['model'] = request.POST['model']
		form['year'] = request.POST['year']
		form['kilometres'] = request.POST['kilometres']
		form['transmission'] = request.POST['transmission']
		form['drivetrain'] = request.POST['drivetrain']
		form['sport'] = request.POST.get('sport', False)
		form['leather'] = request.POST.get('leather', False)

		args = []
		if form['transmission'] == 'automatic':
			args.append('automatic')
		if form['drivetrain'] == 'awd':
			args.append('awd')
		if form['sport']:
			args.append('sport')
		if form['leather']:
			args.append('leather')

		value = WebConfig.predictor.predict(form['year'], form['kilometres'],
		                                    form['model'], *args)
		message = '${:,.2f} CAD'.format(value)

	return TemplateResponse(request, 'index.html', {
		'message': message,
		'form': form,
	})


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
