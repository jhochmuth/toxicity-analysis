from keras_preprocessing.sequence import pad_sequences
import numpy as np
import pickle
import torch
from toxicity_analysis.app.__main__ import NeuralNet


def create_model():
    files = list()
    files.append('models/model_1.pt')
    files.append('models/model_2.pt')
    files.append('models/model_3.pt')
    files.append('models/model_4.pt')
    files.append('models/model_5.pt')

    with open('models/models.pt', 'wb') as outfile:
        for file in files:
            with open(file, 'rb') as infile:
                outfile.write(infile.read())


def create_embeddings():
    files = list()
    files.append('embedding_matrix/embedding_matrix_1.npy')
    files.append('embedding_matrix/embedding_matrix_2.npy')
    files.append('embedding_matrix/embedding_matrix_3.npy')
    files.append('embedding_matrix/embedding_matrix_4.npy')
    files.append('embedding_matrix/embedding_matrix_5.npy')
    files.append('embedding_matrix/embedding_matrix_6.npy')
    files.append('embedding_matrix/embedding_matrix_7.npy')
    files.append('embedding_matrix/embedding_matrix_8.npy')
    files.append('embedding_matrix/embedding_matrix_9.npy')
    files.append('embedding_matrix/embedding_matrix_10.npy')

    with open('embedding_matrix/embedding_matrix.npy', 'wb') as outfile:
        for file in files:
            with open(file, 'rb') as infile:
                outfile.write(infile.read())


def create_tokenizer():
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    return tokenizer


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# Note: models was trained when caps_vs_length feature was always 0.
def get_features(texts):
    features = list()
    for text in texts:
        text = text.lower()
        length = len(text)
        capitals = sum(1 for c in text if c.isupper())
        caps_vs_length = capitals / length
        num_words = len(text.split())
        num_unique_words = len(set(text.lower().split()))
        words_vs_unique = num_unique_words / num_words
        features.append([caps_vs_length, words_vs_unique])
    return features


def standardize_features(features):
    with open('scalar.pickle', 'rb') as handle:
        ss = pickle.load(handle)
    features = ss.transform(features)
    return features


def predict_toxicity(text):
    try:
        model = torch.load('models/toxicity_model.pt')
    except FileNotFoundError:
        create_model()
        model = torch.load('models/toxicity_model.pt')

    model.eval()

    tokenizer = create_tokenizer()
    texts = list()
    for _ in range(2):
        texts.append(text)
    x = tokenizer.texts_to_sequences(texts)
    x = pad_sequences(x, maxlen=70)
    x = torch.tensor(x, dtype=torch.long)

    features = get_features(texts)
    features = standardize_features(features)

    pred = model([x, features]).detach()
    result = sigmoid(pred.numpy())
    classification = 'Toxic' if result[0][0] > .4 else 'Not toxic'
    return result[0][0], classification


def predict_identity_hate(text):
    try:
        model = torch.load('models/identity_model.pt')
    except FileNotFoundError:
        create_model()
        model = torch.load('models/identity_model.pt')

    model.eval()

    tokenizer = create_tokenizer()
    texts = list()
    for _ in range(2):
        texts.append(text)
    x = tokenizer.texts_to_sequences(texts)
    x = pad_sequences(x, maxlen=70)
    x = torch.tensor(x, dtype=torch.long)

    features = get_features(texts)
    features = standardize_features(features)

    pred = model([x, features]).detach()
    result = sigmoid(pred.numpy())
    classification = 'Identity hate' if result[0][0] > .4 else 'Not identity hate'

    return result[0][0], classification


def predict_toxicities(texts):
    try:
        model = torch.load('models/toxicity_model.pt')
    except FileNotFoundError:
        create_model()
        model = torch.load('models/toxicity_model.pt')

    model.eval()

    tokenizer = create_tokenizer()

    x = tokenizer.texts_to_sequences(texts)
    x = pad_sequences(x, maxlen=70)
    x = torch.tensor(x, dtype=torch.long)

    features = get_features(texts)
    features = standardize_features(features)

    preds = model([x, features]).detach()
    preds = [round(pred[0], 3) for pred in sigmoid(preds.numpy())]
    classifications = [pred > .4 for pred in preds]

    return preds, classifications
