###############################################################################
#   NeuralNetMaster.py: top-level class for a neural network
###############################################################################
import os
import sys
import time
from abc import ABC, abstractmethod

import tensorflow as tf

import astroNN
from astroNN.config import keras_import_manager, cpu_gpu_check
from astroNN.shared.nn_tools import folder_runnum

keras = keras_import_manager()
get_session, epsilon, plot_model = keras.backend.get_session, keras.backend.epsilon, keras.utils.plot_model


class NeuralNetMaster(ABC):
    """Top-level class for a neural network"""

    def __init__(self):
        """
        NAME:
            __init__
        PURPOSE:
            To define astroNN neural network
        HISTORY:
            2017-Dec-23 - Written - Henry Leung (University of Toronto)
            2018-Jan-05 - Update - Henry Leung (University of Toronto)
        """
        self.name = None
        self._model_type = None
        self._model_identifier = self.__class__.__name__  # No effect, will do when save
        self._implementation_version = None
        self._python_info = sys.version
        self._astronn_ver = astroNN.__version__
        self._keras_ver = keras.__version__  # Even using tensorflow.keras, this line will still be fine
        self._tf_ver = tf.VERSION
        self.currentdir = os.getcwd()
        self.folder_name = None
        self.fullfilepath = None
        self.batch_size = 64
        self.autosave = False

        # Hyperparameter
        self.task = None
        self.lr = None
        self.max_epochs = None
        self.val_size = None
        self.val_num = None

        # optimizer parameter
        self.beta_1 = 0.9  # exponential decay rate for the 1st moment estimates for optimization algorithm
        self.beta_2 = 0.999  # exponential decay rate for the 2nd moment estimates for optimization algorithm
        self.optimizer_epsilon = epsilon()  # a small constant for numerical stability for optimization algorithm
        self.optimizer = None

        # Keras API
        self.verbose = 2
        self.keras_model = None
        self.keras_model_predict = None
        self.history = None
        self.metrics = None

        self.input_normalizer = None
        self.labels_normalizer = None
        self.training_generator = None
        self.validation_generator = None

        self.input_norm_mode = None
        self.labels_norm_mode = None
        self.input_mean = None
        self.input_std = None
        self.labels_mean = None
        self.labels_std = None

        self.input_shape = None
        self.labels_shape = None

        self.num_train = None
        self.targetname = None
        self.history = None
        self.virtual_cvslogger = None
        self.hyper_txt = None

        cpu_gpu_check()

    @abstractmethod
    def train(self, *args):
        raise NotImplementedError

    @abstractmethod
    def test(self, *args):
        raise NotImplementedError

    @abstractmethod
    def model(self):
        raise NotImplementedError

    @abstractmethod
    def post_training_checklist_child(self):
        raise NotImplementedError

    def pre_training_checklist_master(self, input_data, labels):
        if self.val_size is None:
            self.val_size = 0
        self.val_num = int(input_data.shape[0] * self.val_size)
        self.num_train = input_data.shape[0] - self.val_num

        # Assuming the convolutional layer immediately after input layer
        # only require if it is new, no need for fine-tuning
        if self.input_shape is None:
            if input_data.ndim == 1:
                self.input_shape = (1,1,)
            elif input_data.ndim == 2:
                self.input_shape = (input_data.shape[1], 1,)
            elif input_data.ndim == 3:
                self.input_shape = (input_data.shape[1], input_data.shape[2], 1,)
            elif input_data.ndim == 4:
                self.input_shape = (input_data.shape[1], input_data.shape[2], input_data.shape[3],)

            if labels.ndim == 1:
                self.labels_shape = 1
            elif labels.ndim == 2:
                self.labels_shape = labels.shape[1]
            elif labels.ndim == 3:
                self.labels_shape = (labels.shape[1], labels.shape[2])
            elif labels.ndim == 4:
                self.labels_shape = (labels.shape[1], labels.shape[2], labels.shape[3])

        print(f'Number of Training Data: {self.num_train}, Number of Validation Data: {self.val_num}')

    def pre_testing_checklist_master(self):
        pass

    def post_training_checklist_master(self):
        pass

    def save(self, name=None, model_plot=False):
        # Only generate a folder automatically if no name provided
        if self.folder_name is None and name is None:
            self.folder_name = folder_runnum()
        else:
            if name is not None:
                self.folder_name = name
        # if foldername provided, then create a directory
        if not os.path.exists(os.path.join(self.currentdir, self.folder_name)):
            os.makedirs(os.path.join(self.currentdir, self.folder_name))

        self.fullfilepath = os.path.join(self.currentdir, self.folder_name + '/')

        txt_file_path = self.fullfilepath + 'hyperparameter.txt'
        if os.path.isfile(txt_file_path):
            self.hyper_txt = open(txt_file_path, 'a')
            self.hyper_txt.write("\n")
            self.hyper_txt.write("======Another Run======")
        else:
            self.hyper_txt = open(txt_file_path, 'w')
        self.hyper_txt.write(f"Model: {self.name} \n")
        self.hyper_txt.write(f"Model Type: {self._model_type} \n")
        self.hyper_txt.write(f"astroNN identifier: {self._model_identifier} \n")
        self.hyper_txt.write(f"Python Version: {self._python_info} \n")
        self.hyper_txt.write(f"astroNN Version: {self._astronn_ver} \n")
        self.hyper_txt.write(f"Keras Version: {self._keras_ver} \n")
        self.hyper_txt.write(f"Tensorflow Version: {self._tf_ver} \n")
        self.hyper_txt.write(f"Folder Name: {self.folder_name} \n")
        self.hyper_txt.write(f"Batch size: {self.batch_size} \n")
        self.hyper_txt.write(f"Optimizer: {self.optimizer.__class__.__name__} \n")
        self.hyper_txt.write(f"Maximum Epochs: {self.max_epochs} \n")
        self.hyper_txt.write(f"Learning Rate: {self.lr} \n")
        self.hyper_txt.write(f"Validation Size: {self.val_size} \n")
        self.hyper_txt.write(f"Input Shape: {self.input_shape} \n")
        self.hyper_txt.write(f"Label Shape: {self.labels_shape} \n")
        self.hyper_txt.write(f"Number of Training Data: {self.num_train} \n")
        self.hyper_txt.write(f"Number of Validation Data: {self.val_num} \n")

        if model_plot is True:
            self.plot_model()

        self.post_training_checklist_child()

        self.virtual_cvslogger.savefile(folder_name=self.folder_name)

    def plot_model(self):
        try:
            if self.fullfilepath is not None:
                plot_model(self.keras_model, show_shapes=True, to_file=self.fullfilepath + 'model.png')
            else:
                plot_model(self.keras_model, show_shapes=True, to_file='model.png')
        except ImportError or ModuleNotFoundError:
            print('Skipped plot_model! graphviz and pydot_ng are required to plot the model architecture')
            pass

    def jacobian(self, x=None, mean_output=False):
        """
        NAME: jacobian
        PURPOSE: calculate jacobian of gradietn of output to input
        INPUT:
            x (ndarray): Input Data
            mean_output (boolean): False to get all jacobian, True to get the mean
        OUTPUT:
            (ndarray): Jacobian
        HISTORY:
            2017-Nov-20 Henry Leung
        """
        import numpy as np

        if x is None:
            raise ValueError('Please provide data to calculate the jacobian')

        x_data = np.array(x)
        x_data -= self.input_mean
        x_data /= self.input_std

        try:
            input_tens = self.keras_model_predict.get_layer("input").input
            input_shape_expectation = self.keras_model_predict.get_layer("input").input_shape
        except AttributeError:
            input_tens = self.keras_model.get_layer("input").input
            input_shape_expectation = self.keras_model.get_layer("input").input_shape

        start_time = time.time()

        if len(input_shape_expectation) == 3:
            x_data = np.atleast_3d(x_data)

            grad_list = []
            for j in range(self.labels_shape):
                grad_list.append(tf.gradients(self.keras_model.get_layer("output").output[0, j], input_tens))

            final_stack = tf.stack(tf.squeeze(grad_list))
            jacobian = np.ones((self.labels_shape, x_data.shape[1], x_data.shape[0]), dtype=np.float32)

            for i in range(x_data.shape[0]):
                x_in = x_data[i:i + 1]
                jacobian[:, :, i] = get_session().run(final_stack, feed_dict={input_tens: x_in})

        elif len(input_shape_expectation) == 4:
            monoflag = False
            if len(x_data.shape) < 4:
                monoflag = True
                x_data = x_data[:, :, :, np.newaxis]

            jacobian = np.ones((self.labels_shape, x_data.shape[1], x_data.shape[2], x_data.shape[3], x_data.shape[0]),
                               dtype=np.float32)

            grad_list = []
            for j in range(self.labels_shape):
                grad_list.append(tf.gradients(self.keras_model.get_layer("output").output[0, j], input_tens))

            final_stack = tf.stack(tf.squeeze(grad_list))

            for i in range(x_data.shape[0]):
                x_in = x_data[i:i + 1]
                if monoflag is False:
                    jacobian[:, :, :, :, i] = get_session().run(final_stack, feed_dict={input_tens: x_in})
                else:
                    jacobian[:, :, :, 0, i] = get_session().run(final_stack, feed_dict={input_tens: x_in})

        else:
            raise ValueError('Input data shape do not match neural network expectation')

        if mean_output is True:
            jacobian = np.mean(jacobian, axis=-1)

        print(f'Finished gradient calculation, {(time.time() - start_time):.{2}f} seconds elapsed')

        return jacobian
