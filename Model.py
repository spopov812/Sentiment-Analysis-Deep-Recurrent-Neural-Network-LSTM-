from keras import Sequential
from keras.layers import Dense, LSTM, Dropout, Embedding, Flatten
from keras.layers import LeakyReLU
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.optimizers import adam
from keras.callbacks import TensorBoard, ModelCheckpoint
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

'''
Model creation.
Embedding layer, two LSTM layers with LeakyReLU activation.
'''


def build_model():
	model = Sequential()

	# Input layer
	model.add(Embedding(8000, 64, input_length=500))

	for _ in range(2):
		model.add(LSTM(32, return_sequences=True))
		model.add(LeakyReLU(alpha=.001))
		model.add(Dropout(.5))

	# Flatten to 2D from 3D matrix
	model.add(Flatten())

	# Voting activation function
	model.add(Dense(2, activation="softmax"))

	# Loss, optimizer
	model.compile(

		loss="categorical_crossentropy",
		optimizer=adam(lr=.001),
		metrics=["binary_accuracy", 'categorical_crossentropy', 'categorical_accuracy']
	)

	return model


'''
Initiates model training as well as partitions dataset into training and testing.
'''


def train_model(test_size):
	# Splitting data between training and testing
	x_train, x_test, y_train, y_test = split_dataset(test_size)

	# Saving data to be used later for testing
	np.save("XTesting_Data", x_test)
	np.save("YTesting_Data", y_test)

	# Compiles model
	model = build_model()

	callbacks = []

	# Enabling tensorboard
	callbacks.append(TensorBoard(log_dir='logs', histogram_freq=0, write_graph=True, write_images=True))

	# Saving model every Epoch if there is a decrease in the loss function
	callbacks.append(ModelCheckpoint("Epoch{epoch:02d}.h5",
									 monitor='categorical_crossentropy', verbose=0,
									 save_best_only=True, save_weights_only=False, mode='auto', period=1))

	# Training and saving model
	model.fit(x_train, y_train, epochs=5, batch_size=64, callbacks=callbacks)


'''
Loads dataset and splits into training and testing for both features and targets.
'''


def split_dataset(test_size, vocab_size=8000, max_review_length=500):
	# Loads dataframe
	data = pd.read_csv("CleanedReviews.csv")
	x_input = data['Text']
	y_input = data['Score']

	# One hot encodes reviews and pads them to appropriate length
	x_data = [one_hot(word, vocab_size) for word in x_input]
	x_data = pad_sequences(x_data, maxlen=max_review_length)

	y_data = []

	# one hot encodes output (sentiment)
	for val in y_input:

		if val == 1 or val == 2:
			y_data.append([1, 0])

		elif val == 4 or val == 5:
			y_data.append([0, 1])

		else:
			print("Error")
			exit(0)

	# conversion to numpy array
	Y_data = np.array(y_data)
	X_data = np.array(x_data)

	return train_test_split(X_data, Y_data, test_size=test_size)
