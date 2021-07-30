from django.db import models


class Data(models.Model):
	raw_csv = models.FileField(upload_to='csv_files', null=True, blank=True)
	clean_csv = models.FileField(upload_to='csv_files', null=True, blank=True)
