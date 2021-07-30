from django.urls import path

from web import views

app_name = 'web'
urlpatterns = [
	path('', views.index),
	path('data/<str:file>', views.get_data)
]