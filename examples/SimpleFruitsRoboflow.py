"""
Author: Gerard Harkema
Date:   2025-09-19
Version: 1.00 (initial version)

This script performs object detection using the Roboflow Python SDK in "offline" mode.
Instead of using the cloud REST API, it loads a Roboflow model locally
and runs inference directly on frames captured from a Daheng camera.
"""

from PIL.ImageMath import imagemath_equal  # (unused import, can be removed)
from DahengAvansLibrary.DahengLibrary import dahengCamera
from roboflow import Roboflow
import cv2
import time
import numpy as np


class RoboflowDetector:
    """
    A detector class that:
    - Loads a trained Roboflow model using the SDK
    - Runs predictions locally
    - Draws bounding boxes and labels onto frames
    """

    def __init__(self):
        # Connect to Roboflow with your API key
        self.rf = Roboflow(api_key="K3sks4IiHf1jC7nMw6YN")
        # Load the "simplefruits" project
        self.project = self.rf.workspace().project("simplefruits")
        # Use version 1 of the trained model
        self.model = self.project.version(1).model

    def plot_boxes(self, image):
        """
        Run detection on the input frame and draw bounding boxes + labels.
        """
        # Perform prediction on the image (returns JSON with detections)
        predictions = self.model.predict(image, confidence=40, overlap=30).json()
        #print(predictions)

        # Loop through detected objects and draw results
        for prediction in predictions['predictions']:
            print(prediction['class'])
            # Convert Roboflow center-based coordinates to corner points
            x0 = prediction['x'] - prediction['width'] / 2
            x1 = prediction['x'] + prediction['width'] / 2
            y0 = prediction['y'] - prediction['height'] / 2
            y1 = prediction['y'] + prediction['height'] / 2

            # Define rectangle corners
            start_point = (int(x0), int(y0))
            end_point = (int(x1), int(y1))

            # Draw bounding box in blue
            cv2.rectangle(image, start_point, end_point, color=(255, 0, 0), thickness=1)

            # Draw label text above the box
            cv2.putText(
                image,
                prediction["class"],            # Object class name
                (int(x0), int(y0) - 10),          # Position slightly above box
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.6,
                color=(0, 255, 0),            # White text
                thickness=2
            )
        return image


# Example SDK usage:
# model.predict("your_image.jpg", confidence=40, overlap=30).save("prediction.jpg")
# print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())


def main():
    """
    Main loop:
    - Capture video frames from Daheng camera
    - Run Roboflow offline detection
    - Display annotated frames with FPS counter
    - Exit gracefully on 'q'
    """
    camera = dahengCamera(1, True)
    object_detector = RoboflowDetector()

    if not camera.isOpen():
        return

    print("Press [q] and then [Enter] to Exit the Program")
    camera.startStraem()

    start_time = time.perf_counter()

    while True:
        image = camera.grab_frame()
        if image is not None:
            # Run object detection
            image = object_detector.plot_boxes(image)

            # FPS calculation
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)

            # Draw FPS counter on top-left corner
            cv2.putText(image, f'FPS: {int(fps)}',
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, (0, 255, 0), 2)

            # Show image with detections
            cv2.imshow("Detected objects Image", image)

            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStraem()
                cv2.destroyAllWindows()
                return

            start_time = end_time  # Reset timer
        else:
            # Stop and cleanup if no frame
            camera.stopStraem()
            camera.close()
            cv2.destroyAllWindows()
            return


if __name__ == "__main__":
    main()
