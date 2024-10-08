import enum
from typing import List, NamedTuple
from daisykit.utils import get_asset_file, to_py_type
import numpy as np


class BodyPart(enum.Enum):
  """Enum representing human body keypoints detected by pose estimation models."""
  NOSE = 0
  LEFT_EYE = 1
  RIGHT_EYE = 2
  LEFT_EAR = 3
  RIGHT_EAR = 4
  LEFT_SHOULDER = 5
  RIGHT_SHOULDER = 6
  LEFT_ELBOW = 7
  RIGHT_ELBOW = 8
  LEFT_WRIST = 9
  RIGHT_WRIST = 10
  LEFT_HIP = 11
  RIGHT_HIP = 12
  LEFT_KNEE = 13
  RIGHT_KNEE = 14
  LEFT_ANKLE = 15
  RIGHT_ANKLE = 16


#use NamedTuple to avoid changing 
# the fields/elements of the object instances during operation
class Point(NamedTuple):
  """A point in 2D space."""
  x: float
  y: float


class Rectangle(NamedTuple):
  """A rectangle in 2D space."""
  start_point: Point
  end_point: Point


class KeyPoint(NamedTuple):
  """A detected human keypoint."""
  body_part: BodyPart
  coordinate: Point
  score: float


class Person(NamedTuple):
  """A pose detected by a pose estimation model."""
  keypoints: List[KeyPoint]
  bounding_box: Rectangle
  score: float
  id: int = None


def person_from_keypoints_with_scores(
    keypoints_with_scores: np.ndarray,
    image_height: float,
    image_width: float,
    keypoint_score_threshold: float = 0.1) -> Person:
  """Creates a Person instance from single pose estimation model output.

  Args:
    keypoints_with_scores: Output of the daisykit pose estimation model. A numpy
      array with shape [17, 3]. Each row represents a keypoint: [x, y, score].
    image_height: height of the image in pixels.
    image_width: width of the image in pixels.
    keypoint_score_threshold: Only use keypoints with above this threshold to
      calculate the person average score.

  Returns:
    A Person instance.
  """

  kpts_x = keypoints_with_scores[:, 0]
  kpts_y = keypoints_with_scores[:, 1]
  scores = keypoints_with_scores[:, 2]

  # Convert keypoints to the input image coordinate system.
  keypoints = [] #list of keypoints: list(Keypoint)
  for i in range(scores.shape[0]):
    keypoints.append(
        KeyPoint(
            BodyPart(i),
            Point(int(kpts_x[i]), int(kpts_y[i])),
            scores[i]))

  # Calculate bounding box 
  start_point = Point(
      int(np.amin(kpts_x) ), int(np.amin(kpts_y)))
  end_point = Point(
      int(np.amax(kpts_x)), int(np.amax(kpts_y)))
  bounding_box = Rectangle(start_point, end_point)

  # Calculate person score by averaging keypoint scores.
  scores_above_threshold = list(
      filter(lambda x: x > keypoint_score_threshold, scores))
  person_score = np.average(scores_above_threshold)

  return Person(keypoints, bounding_box, person_score)


class Category(NamedTuple):
  """A classification category."""
  label: str
  score: float

config = {
    "person_detection_model": {
        "model": get_asset_file(r"models/human_detection/ssd_mobilenetv2/ssd_mobilenetv2.param"),
        "weights": get_asset_file(r"models/human_detection/ssd_mobilenetv2/ssd_mobilenetv2.bin"),
        "input_width": 320,
        "input_height": 320,
        "use_gpu": False
    },
    "human_pose_model": {
        "model": get_asset_file(r"models/human_pose_detection/movenet/lightning.param"),
        "weights": get_asset_file(r"models/human_pose_detection/movenet/lightning.bin"),
        "input_width": 192,
        "input_height": 192,
        "use_gpu": False
    }
}

