import datetime
import numpy as np
import tensorflow as tf
from tensorflow import keras



model = tf.keras.models.Sequential([keras.Input(shape=(4, 30,)), keras.layers.Conv1D(filters=64, kernel_size=13, padding="same"), keras.layers.Conv1D(filters=64, kernel_size=9, padding="same"), keras.layers.Flatten(), keras.layers.Dense(32, activation='relu'), keras.layers.Dense(3, activation='relu')])


model.summary()
tf.keras.utils.plot_model(
    model,
    to_file="diagram_model.png",
    show_shapes=True)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss='categorical_crossentropy', metrics=['acc'])

early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', restore_best_weights=True, patience=30)
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(
    log_dir=log_dir, histogram_freq=1)



dataset = np.load("timeseries_dataset.npz")
print(dataset['x'])
print(dataset['y'])

model.fit(
    x=dataset['x'],
    y=dataset['y'],
    validation_split = 0.2,
    epochs=100,
    callbacks=[tensorboard_callback, early_stopping_callback])


model.save("trading_model.h5")



