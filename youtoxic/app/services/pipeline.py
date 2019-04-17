"""Contains implementation of the Pipeline object."""

import pickle

from fastai.text.transform import Tokenizer

from keras_preprocessing.sequence import pad_sequences

import numpy as np

import torch
from torch.autograd.variable import Variable

from youtoxic.app.utils.feature_engineering import get_features, standardize_features
from youtoxic.app.utils.functions import sigmoid, softmax
from youtoxic.app.utils.load_files import load_mappings, load_model
from youtoxic.app.utils.neural_net import NeuralNet


class Pipeline:
    """This object loads all models and makes the actual predictions."""

    def __init__(self):
        """Initializes pipeline object by loading models and tokenizer."""
        self.toxicity_model = NeuralNet()
        self.identity_model = NeuralNet()
        self.obscenity_model = NeuralNet()
        self.insult_model = NeuralNet()

        self.mappings = load_mappings("youtoxic/app/models/mappings.pkl")
        self.ulm_toxicity_model = load_model(
            len(self.mappings), "youtoxic/app/models/ulm_toxicity_model.h5"
        )

        self.toxicity_model.load_state_dict(
            torch.load("youtoxic/app/models/toxicity_model_state.pt")
        )
        self.identity_model.load_state_dict(
            torch.load("youtoxic/app/models/identity_model_state.pt")
        )
        self.obscenity_model.load_state_dict(
            torch.load("youtoxic/app/models/obscenity_model_state.pt")
        )
        self.insult_model.load_state_dict(
            torch.load("youtoxic/app/models/insult_model_state.pt")
        )

        self.toxicity_model.eval()
        self.identity_model.eval()
        self.obscenity_model.eval()
        self.insult_model.eval()

        self.threshold = 0.4

        with open("youtoxic/app/utils/tokenizer.pickle", "rb") as handle:
            self.tokenizer = pickle.load(handle)

    def predict_insult(self, text):
        """Predicts if a text is an insult.

        Parameters
        ----------
        text: str
            The text to make a prediction for.

        Returns
        -------
        float
            The numeric prediction.

        str
            'Insult' if prediction > threshold, 'Not an insult' otherwise.

        """
        x = self.tokenizer.texts_to_sequences([text])
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features([text])
        features = standardize_features(features)

        pred = self.insult_model([x, features]).detach()
        result = sigmoid(pred.numpy())
        classification = "Insult" if result[0][0] > self.threshold else "Not an insult"
        return round(result[0][0], 3), classification

    def predict_insult_multiple(self, texts):
        """Predicts if each text in a list is an insult.

        Parameters
        ----------
        texts: List
            A list of texts to make predictions for.

        Returns
        -------
        List
            Contains the numeric prediction for each text.

        List
            For each text, contains 'Insult' if prediction > threshold, 'Not an insult' otherwise.

        """
        x = self.tokenizer.texts_to_sequences(texts)
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features(texts)
        features = standardize_features(features)

        preds = self.insult_model([x, features]).detach()
        preds = [round(pred[0], 3) for pred in sigmoid(preds.numpy())]
        classifications = [
            "Insult" if pred > self.threshold else "Not an insult" for pred in preds
        ]
        return preds, classifications

    def predict_obscenity(self, text):
        """Predicts if a text contains obscenity.

        Parameters
        ----------
        text: str
            The text to make a prediction for.

        Returns
        -------
        float
            The numeric prediction.

        str
            'Obscene' if prediction > threshold, 'Not obscene' otherwise.

        """
        x = self.tokenizer.texts_to_sequences([text])
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features([text])
        features = standardize_features(features)

        pred = self.obscenity_model([x, features]).detach()
        result = sigmoid(pred.numpy())
        classification = "Obscene" if result[0][0] > self.threshold else "Not obscene"
        return round(result[0][0], 3), classification

    def predict_obscenity_multiple(self, texts):
        """Predicts if each text in a list contains obscenity.

        Parameters
        ----------
        texts: List
            A list of texts to make predictions for.

        Returns
        -------
        List
            Contains the numeric prediction for each text.

        List
            For each text, contains 'Obscene' if prediction > threshold, 'Not obscene' otherwise.

        """
        x = self.tokenizer.texts_to_sequences(texts)
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features(texts)
        features = standardize_features(features)

        preds = self.obscenity_model([x, features]).detach()
        preds = [round(pred[0], 3) for pred in sigmoid(preds.numpy())]
        classifications = [
            "Obscene" if pred > self.threshold else "Not obscene" for pred in preds
        ]
        return preds, classifications

    def predict_prejudice(self, text):
        """Predicts if a text contains prejudice/identity hate.

        Parameters
        ----------
        text: str
            The text to make a prediction for.

        Returns
        -------
        float
            The numeric prediction.

        str
            'Prejudice' if prediction > threshold, 'Not prejudice' otherwise.

        """
        x = self.tokenizer.texts_to_sequences([text])
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features([text])
        features = standardize_features(features)

        pred = self.identity_model([x, features]).detach()
        result = sigmoid(pred.numpy())
        classification = (
            "Prejudice" if result[0][0] > self.threshold else "Not prejudice"
        )
        return round(result[0][0], 3), classification

    def predict_prejudice_multiple(self, texts):
        """Predicts if each text in a list contains prejudice/identity hate.

        Parameters
        ----------
        texts: List
            A list of texts to make predictions for.

        Returns
        -------
        List
            Contains the numeric prediction for each text.

        List
            For each text, contains 'Prejudice' if prediction > threshold, 'Not prejudice' otherwise.

        """
        x = self.tokenizer.texts_to_sequences(texts)
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features(texts)
        features = standardize_features(features)

        preds = self.identity_model([x, features]).detach()
        preds = [round(pred[0], 3) for pred in sigmoid(preds.numpy())]
        classifications = [
            "Prejudice" if pred > self.threshold else "Not prejudice" for pred in preds
        ]
        return preds, classifications

    def predict_toxicity(self, text):
        """Predicts if a text contains general toxicity.

        Parameters
        ----------
        text: str
            The text to make a prediction for.

        Returns
        -------
        float
            The numeric prediction.

        str
            'Toxic' if prediction > threshold, 'Not toxic' otherwise.

        """
        x = self.tokenizer.texts_to_sequences([text])
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features([text])
        features = standardize_features(features)

        pred = self.toxicity_model([x, features]).detach()
        result = sigmoid(pred.numpy())
        classification = "Toxic" if result[0][0] > self.threshold else "Not toxic"
        return round(result[0][0], 3), classification

    def predict_toxicity_multiple(self, texts):
        """Predicts if each text in a list contains general toxicity.

        Parameters
        ----------
        texts: List
            A list of texts to make predictions for.

        Returns
        -------
        preds: List
            Contains the numeric prediction for each text.

        classifications: List
            For each text, contains 'Toxic' if prediction > threshold, 'Not toxic' otherwise.

        """
        x = self.tokenizer.texts_to_sequences(texts)
        x = pad_sequences(x, maxlen=70)
        x = torch.tensor(x, dtype=torch.long)

        features = get_features(texts)
        features = standardize_features(features)

        preds = self.toxicity_model([x, features]).detach()
        preds = [round(pred[0], 3) for pred in sigmoid(preds.numpy())]
        classifications = [
            "Toxic" if pred > self.threshold else "Not toxic" for pred in preds
        ]
        return preds, classifications

    def predict_text_ulm(self, model, text):
        """Handles calculation of predictions using any ULMFiT model.

        Parameters
        ----------
        model: SequentialRNN
            The ULMFiT model to use for getting predictions.

        text: str
            The text to analyze.

        Returns
        -------
        float
            The prediction.

        """
        texts = [text]
        tok = Tokenizer().process_all(texts)
        encoded = [self.mappings[p] for p in tok[0]]

        ary = np.reshape(np.array(encoded), (-1, 1))
        tensor = torch.from_numpy(ary)
        variable = Variable(tensor)

        predictions = model(variable)
        numpy_preds = predictions[0].data.numpy()
        return softmax(numpy_preds[0])[0]

    def predict_toxicity_ulm(self, text):
        """Predicts if a text contains general toxicity using a ULMFiT model.

        Parameters
        ----------
        text: str
            The text to make a prediction for.

        Returns
        -------
        float
            The numeric prediction.

        str
            'Toxic' if prediction > threshold, 'Not toxic' otherwise.

        """
        pred = self.predict_text_ulm(self.ulm_toxicity_model, text)[1]
        classification = "Toxic" if pred > self.threshold else "Not toxic"
        return pred, classification

    def predict_toxicity_ulm_multiple(self, texts):
        """Predicts if each text in a list contains general toxicity using a ULMFiT model.

        Parameters
        ----------
        texts: List
            A list of texts to make predictions for.

        Returns
        -------
        List
            Contains the numeric prediction for each text.

        List
            For each text, contains 'Toxic' if prediction > threshold, 'Not toxic' otherwise.

        """
        preds, classifications = [None] * len(texts), [None] * len(texts)
        for i, text in enumerate(texts):
            preds[i], classifications[i] = self.predict_toxicity_ulm(text)
        return preds, classifications
