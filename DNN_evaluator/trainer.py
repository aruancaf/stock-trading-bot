import datetime
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os

model = tf.keras.models.Sequential()
model.add(keras.Input(shape=(4, 30,)))
# model.add(keras.layers.Conv1D(filters=32, kernel_size=13, padding="same"))
# model.add(keras.layers.Conv1D(filters=64, kernel_size=9, padding="same"))

'''
an example: if I'm observing the amount of rain and the temperature each hour for 24h in order to predict the weather (1 = good, 0 = bad), and I do that for 365 days, I will have 365 samples, each of which will have 24 timesteps, and 2 variables (one for rain, one for temperature), so my input is going to have the shape (365, 24, 2), and input_shape = (24, 2).
'''

model.add(keras.layers.LSTM(30, input_shape=(30, 4), return_sequences=True))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(15, return_sequences=True))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(5, return_sequences=False))
model.add(keras.layers.Dropout(0.2))
# model.add(keras.layers.Dense(32, activation='relu'))
model.add(keras.layers.Dense(3, activation='relu'))


model.summary()
tf.keras.utils.plot_model(
    model,
    to_file="diagram_model.png",
    show_shapes=True)

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['acc'])

early_stopping_callback = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', restore_best_weights=True, patience=9)
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(
    log_dir=log_dir, histogram_freq=1)


dataset = np.load("timeseries_dataset.npz")
print(dataset['x'])
print(dataset['y'])
print(np.shape(dataset['x'][0]))

model.fit(
    x=dataset['x'],
    y=dataset['y'],
    validation_split=0.2,
    epochs=100,
    callbacks=[tensorboard_callback, early_stopping_callback])

vers = []
model_name = "trading_modelV"
for i in os.listdir():
    if model_name in i:
        vers.append(int(i.replace(model_name, "").replace(".h5", "")))

model.save(model_name + str(max(vers) + 1) + ".h5")
