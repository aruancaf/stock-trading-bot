import tensorflow as tf
from training_input import TrainingInput
import numpy as np

model = tf.keras.models.load_model('trading_model.h5')


print(np.shape(TrainingInput(False, 0, 0, [0.01 * i for i in range(30)], 0, 0, [0]*30).get_serialized_input()))
# Test Case 1: Going Linearly Up

print("Going linearly up: ", TrainingInput.map(model.predict(TrainingInput(False, 0, 0, [0.01 * i for i in range(30)], 0, 0, [0]*30).get_serialized_input()), False))



# Test Case 2: Going Linearly Down 

print("Going linearly down: ", TrainingInput.map(model.predict(TrainingInput(False, 0, 0, [-0.01 * i for i in range(30)], 0, 0, [0]*30).get_serialized_input()), False))

# Test Case 3: No Movement 

print("No price movement: ", TrainingInput.map(model.predict(TrainingInput(False, 0, 0, [0.5]*30, 0, 0, [0]*30).get_serialized_input()), False))

