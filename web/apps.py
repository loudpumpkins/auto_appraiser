from django.apps import AppConfig

from util.predict import Predictor


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'
    predictor = Predictor()