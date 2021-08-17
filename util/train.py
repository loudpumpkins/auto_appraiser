import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing


if __name__ == '__main__':
	
	df = pd.read_json('https://auto-appraiser.loudpumpkins.com/data/clean')

	# split data 80/20 for training and testing
	train_features = df.sample(frac=0.8, random_state=0)
	test_features = df.drop(train_features.index)

	# remove the 'price' column as it is not part of given variables
	train_labels = train_features.pop('price')
	test_labels = test_features.pop('price')

	# normalized layer
	norm = preprocessing.Normalization(input_shape=[24, ])
	norm.adapt(np.array(train_features))

	# sequential model
	dnn_model = tf.keras.Sequential([
	    norm,
	    layers.Dense(units=24*2, activation='relu'),
	    layers.Dense(units=24*2, activation='relu'),
	    layers.Dense(units=1)
	])

	# configure training procedure
	dnn_model.compile(
	    optimizer=tf.optimizers.Adam(learning_rate=0.01),
	    loss='mean_absolute_error'
	)

	# train
	history = dnn_model.fit(
	    train_features, train_labels,
	    epochs=50,
	    # suppress logging
	    verbose=0,
	    # Calculate validation results on 20% of the training data
	    validation_split=0.2)

	# save model
	dnn_model.save('dnn_model')
