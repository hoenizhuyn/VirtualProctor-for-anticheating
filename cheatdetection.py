import cv2
import numpy as np
from daisykit.utils import to_py_type
from daisykit import HumanPoseMoveNetFlow
from sklearn.preprocessing import normalize  # Example for normalization
import pandas as pd
from typing import List
from utils import person_from_keypoints_with_scores, config, BodyPart
from posedetector import posedetector
from tensorflow.keras.models import load_model
from train import landmarks_to_embedding
import tensorflow as tf
# # Specify the path to your model
model_path = "/home/huyn/anticheating/weights.best.keras"
# # Load the model
# model = load_model(model_path)
# # Print model summary to verify it's loaded correctly
# model.summary()

class CheatDetection:
    def __init__(self, config, model_path):
        # Initialize pose detector
        self.detector = posedetector(config, many_pose=True)
        
        # Load pre-trained classification model (replace with your model)
        self.model = load_model(model_path)

    def detect_cheating(self, image):
        persons = self.detector.detect(image)
        cheating_detected = False
        if not persons:
            return image, cheating_detected

        for person in persons:
            keypoints_array = np.array([[kp.coordinate.x, kp.coordinate.y, kp.score] for kp in person.keypoints],
                                dtype=np.float32)
            # Normalize keypoints or process as needed
            keypoints_dataframe = pd.DataFrame(keypoints_array.flatten()).T
            keypoints_dataframe.columns= [f'{bp.name}_{coord}' for bp in BodyPart for coord in ['x', 'y', 'score']]
            embedding = landmarks_to_embedding(tf.reshape(tf.convert_to_tensor(keypoints_dataframe), (1, 51)))
            processed_embedding=tf.convert_to_tensor(embedding)
            # Predict cheating behavior
            prediction = self.model.predict(processed_embedding)
            prediction = np.squeeze(prediction,0)
            if prediction[0] == np.max(prediction):
                if prediction[0] >= 10000*prediction[1]:
                    predicted_class = 0
                else:
                    predicted_class = 1
            else:
                predicted_class = 2

            # If classified as cheating, draw bounding box
            if predicted_class == 0:  
                cheating_detected = True
                start_point = (int(person.bounding_box.start_point.x), int(person.bounding_box.start_point.y))
                end_point = (int(person.bounding_box.end_point.x), int(person.bounding_box.end_point.y))
                image = cv2.rectangle(image, start_point, end_point, (0, 0, 255), 2)  # Red box for cheating
                #input start_point: point tuple
        return image, cheating_detected



