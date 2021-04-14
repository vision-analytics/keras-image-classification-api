import os

import cv2
import numpy as np
import tensorflow as tf

from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.xception import preprocess_input

from . import utilities


class Classifier:

    def __init__(self):
        """ Generic class for classifier
    
        Attributes:
            
        """
        print("initializing classifier..")

        self.model_path = utilities.get_config(section_name="CLASSIFIER", key="model_path")
        self.category_class_list = utilities.get_config(section_name="CLASSIFIER", key="class_list").split(',')
        
        self.model = None

        self.img_size = int(utilities.get_config(section_name="CLASSIFIER", key="img_size"))
        self.memory_limit = float(utilities.get_config(section_name="GPU", key="memory_limit"))

        self.prepare_model()

    def preprocess_image(self, frame):
        """Function to prepare image for prediction
        Args: 
            image: numpy.ndarray. BGR image
        Returns: 
            numpy.ndarray. expanded_dims (1, x, x, 3) rgb
        """
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert to rgb
        frame = cv2.resize(frame, (self.img_size, self.img_size)) # resize
        np_arr = img_to_array(frame)
        np_arr = np.expand_dims(np_arr, axis=0)
        np_arr = preprocess_input(np_arr)

        return np_arr

    def prepare_model(self):
        """Function to prepare model
        Args: 
        
        Returns: 
        """

        # limit gpu usage
        gpus = tf.config.experimental.list_physical_devices('GPU')
        print(f"gpu devices: {gpus}")
        if gpus:
            print("limit for gpu usage: {}MB".format(self.memory_limit))
            try:
                tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=self.memory_limit)])
            except RuntimeError as e:
                print(f"unable to limit gpu.. {e}")
                pass

        print("loading classifier model...")
        try:
            self.model = load_model(self.model_path, custom_objects={"tf": tf}, compile=False)
        except Exception as e:
            print(f"unable to load model for classifier! {e}")
            raise Exception(f'unable to load model for classifier! {e}')


    def predict(self, image):
        """Function to predict class of given image
        Args: 
            image: numpy.ndarray. BGR image
        
        Returns: 
            dict: pred_results
        """
        print("running prediction...")
        data = {}
        data["predictions"] = []
 
        processed_image = self.preprocess_image(image)

        try:
            predictions = self.model.predict(processed_image)
        except Exception as e:
            print(f"ClassifierError {e}")
            raise Exception(f'classifier error! {e}')
      
        for label, prob in zip(self.category_class_list, predictions[0]):
            r = {"label": label, "probability": round(float(prob),4)}
            data["predictions"].append(r)

        #print(data)
        
        return data