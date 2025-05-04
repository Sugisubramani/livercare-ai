import socket
import struct
import pickle
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import pathlib 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random
import os 

CLIENT_ID = 1
SERVER_ADDRESS = ('localhost', 5000)
BATCH_SIZE = 32
TRAIN_DATASET_PATH = f"federated_data/client_1/train"
VALIDATION_DATASET_PATH = f"federated_data/client_1/valid"


train_datagen = ImageDataGenerator(rescale=1/255.,
                                rotation_range=20, 
                                width_shift_range=0.2,
                                height_shift_range=0.2,
                                zoom_range=0.2,
                                horizontal_flip=True)

valid_datagen = ImageDataGenerator(rescale=1/255.)

def load_data():
    train_data = train_datagen.flow_from_directory(
        TRAIN_DATASET_PATH, target_size=(224, 224), batch_size=32, class_mode='categorical')
    
    valid_data = valid_datagen.flow_from_directory(
        VALIDATION_DATASET_PATH, target_size=(224, 224), batch_size=32, class_mode='categorical')

    return train_data, valid_data

def recvall(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            break
        data += packet
    return data

def request_model():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(SERVER_ADDRESS)
        sock.sendall("REQUEST_MODEL".encode('utf-8'))
        raw_msglen = recvall(sock, 4)
        msglen = struct.unpack('!I', raw_msglen)[0]
        data = recvall(sock, msglen)
        return pickle.loads(data)

def train_local_model():
    model_info = request_model()
    model = tf.keras.models.model_from_json(model_info['model_arch'])
    model.set_weights(model_info['weights'])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    train_data, valid_data = load_data()
    model.fit(train_data, epochs=5, steps_per_epoch=len(train_data), validation_data=valid_data, validation_steps=len(valid_data))

    return [w.numpy() for w in model.weights]

def send_update(update):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(SERVER_ADDRESS)
        sock.sendall("UPDATE_MODEL".encode('utf-8'))
        data = pickle.dumps(update)
        sock.sendall(struct.pack('!I', len(data)) + data)
        response = sock.recv(1024)
        print(f"Client {CLIENT_ID}: Update sent successfully!")

for round_num in range(5):
    print(f"Client {CLIENT_ID} - Training Round {round_num+1}")
    local_update = train_local_model()
    send_update(local_update)