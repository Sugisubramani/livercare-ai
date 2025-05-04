import socket
import struct
import pickle
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator

TEST_DATASET_PATH = "test_data/"

test_datagen = ImageDataGenerator(rescale=1/255.)
test_data = test_datagen.flow_from_directory(
    TEST_DATASET_PATH, target_size=(224, 224), batch_size=32, class_mode='categorical'
    )

def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(4, activation='softmax')
    ])
    return model

def recvall(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            break
        data += packet
    return data

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5000))
server_socket.listen(4)

print("\n--- Server is waiting for clients to connect ---\n")

NUM_ROUNDS = 5
NUM_CLIENTS = 4

global_model = create_model()
global_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
global_weights = [w.numpy() for w in global_model.weights]

for round_num in range(1, NUM_ROUNDS + 1):
    print(f"\n--- Federated Training Round {round_num} ---")
    client_updates = []
    round_clients = 0
    
    while round_clients < NUM_CLIENTS:
        client_conn, addr = server_socket.accept()
        command = client_conn.recv(1024).decode('utf-8').strip()
        
        if command == "REQUEST_MODEL":
            model_info = pickle.dumps({
                'model_arch': global_model.to_json(),
                'weights': global_weights,
                'hyperparams': {'optimizer': 'adam', 'loss': 'categorical_crossentropy', 'metrics': ['accuracy']}
            })
            client_conn.sendall(struct.pack('!I', len(model_info)) + model_info)
            client_conn.close()
        
        elif command == "UPDATE_MODEL":
            raw_msglen = recvall(client_conn, 4)
            msglen = struct.unpack('!I', raw_msglen)[0]
            data = recvall(client_conn, msglen)
            client_update = pickle.loads(data)
            client_updates.append(client_update)
            client_conn.send(b"ACK")
            client_conn.close()
            round_clients += 1

    if len(client_updates) > 0:
        new_weights = [np.mean([update[i] for update in client_updates], axis=0) for i in range(len(client_updates[0]))]
        global_model.set_weights(new_weights)

    loss, acc = global_model.evaluate(test_data)
    print(f"Server Model Evaluation - Loss: {loss:.4f}, Accuracy: {acc:.4f}")

    global_model.save("global_model.keras")
    global_weights = [w.numpy() for w in global_model.weights]

server_socket.close()


