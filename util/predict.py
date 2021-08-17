import os
import tensorflow as tf


class Predictor(object):

	header = ['kilometres', 'year',
	          # models
	          'other', 'crosstour', 'fit', 'civic', 'ridgeline',
	          'del sol', 'accord', 'passport', 'odyssey', 'insight',
	          's2000', 'cr-z', 'accord crosstour', 'hr-v', 'element',
	          'cr-v', 'prelude', 'pilot',
	          # other features
	          'sport', 'leather', 'automatic', 'awd']
	model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
	                          'dnn_model')

	def __init__(self):
		self.dnn_model = tf.keras.models.load_model(self.model_path)

	def predict(self, year, kilometres, model, *args):
		vehicle = [0 for _ in range(len(self.header))]
		vehicle[self.header.index('year')] = int(year)
		vehicle[self.header.index('kilometres')] = int(kilometres)
		vehicle[self.header.index(model)] = 1
		for arg in args:
			vehicle[self.header.index(arg)] = 1

		prediction = self.dnn_model.predict([vehicle]).flatten()
		return prediction[0]
