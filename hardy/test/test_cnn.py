import keras
import unittest

import numpy as np

from hardy.recognition import cnn
from hardy.handling.to_catalogue import learning_set, test_set

# define variables to use for the following test:

path = './hardy/test/test_image/'
split = 0.1
classes = ['class_1', 'class_2']
batch_size = 1


class TestSimulationTools(unittest.TestCase):

    def test_build_model(self):
        train, val = learning_set(path, split=split, classes=classes,
                                  iterator_mode=None)
        model, history = cnn.build_model(train, val,
                                         config_path='./hardy/recognition/')
        assert isinstance(train, keras.preprocessing.image.DirectoryIterator),\
            'the training set should be an image iterator type of object'
        assert isinstance(val, keras.preprocessing.image.DirectoryIterator),\
            'the validation set should be an image iterator type of object'
        assert isinstance(model, keras.engine.sequential.Sequential),\
            'the CNN model should be a keras sequential model'
        assert isinstance(history, keras.callbacks.callbacks.History), \
            'the history should be the output of a allback function'

    def test_evaluate_model(self):
        # define the sets and the model to use for the rest of the testing
        train, val = learning_set(path, split=split, classes=classes,
                                  iterator_mode=None)
        testing = test_set(path, batch_size=batch_size, classes=classes,
                           iterator_mode=None)
        model, history = cnn.build_model(train, val,
                                         config_path='./hardy/recognition/')
        results = cnn.evaluate_model(model, testing)
        assert isinstance(results, list), \
            'model performance should be store in a list'
        assert results[1] <= 1,\
            'the accuracy should be a number smaller than 1'

    def test_report_on_metrics(self):
        train, val = learning_set(path, split=split, classes=classes,
                                  iterator_mode=None)
        testing = test_set(path, batch_size=batch_size, classes=classes,
                           iterator_mode=None)
        model, history = cnn.build_model(train, val,
                                         config_path='./hardy/recognition/')
        conf_matrix, report = cnn.report_on_metrics(
                                model, testing,
                                target_names=['noisy', 'not_noisy'])
        assert isinstance(conf_matrix, np.ndarray), \
            'the confusion matrix should be contained in a numpy array'
        assert isinstance(report, str), 'the report should be a string'