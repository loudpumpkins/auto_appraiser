import os
import tensorflow as tf


def predict_price(year, kilometres, model, *args):
	model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dnn_model')
	dnn_model = tf.keras.models.load_model(model_path)

	header = ['kilometres', 'year',
	           # models
	           'other', 'crosstour', 'fit', 'civic', 'ridgeline',
	           'del sol', 'accord', 'passport', 'odyssey', 'insight',
	           's2000', 'cr-z', 'accord crosstour', 'hr-v', 'element',
	           'cr-v', 'prelude', 'pilot',
	           # other features
	           'sport', 'leather', 'automatic', 'awd']

	vehicle = [0 for _ in range(len(header))]
	vehicle[header.index('year')] = int(year)
	vehicle[header.index('kilometres')] = int(kilometres)
	vehicle[header.index(model)] = 1
	for arg in args:
		vehicle[header.index(arg)] = 1

	prediction = dnn_model.predict([vehicle]).flatten()
	return prediction[0]
