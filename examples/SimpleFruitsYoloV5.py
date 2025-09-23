"""
Author: Gerard Harkema
Date:   2025-09-19
Version: 1.00 (initial version)
"""

import torch
import numpy as np
import cv2
import time
from DahengAvansLibrary.DahengLibrary import dahengCamera


class YoloV5Detector:
    """
    A YOLOv5-based object detection class that handles:
    - Model loading
    - Frame scoring (inference)
    - Drawing bounding boxes on detected objects
    """

    def __init__(self):
        # Load the YOLOv5 model
        self.model = self.load_model()
        # Store the class labels (from the model)
        self.classes = self.model.names
        # Use GPU if available, otherwise fallback to CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:", self.device)

    def load_model(self):
        """
        Load the YOLOv5 model with custom weights.
        - Uses a pre-trained model from ultralytics/yolov5 via torch.hub
        - Loads the trained weights from 'support/SimpleFruitsv1iyolov5pytorch.pt'
        - Sets detection confidence and NMS IoU thresholds
        """
        model = torch.hub.load(
            'ultralytics/yolov5',  # Repository
            'custom',              # Load a custom model
            path='support/SimpleFruitsv1iyolov5pytorch.pt',  # Path to weights
            force_reload=False     # Don’t reload if already cached
        )

        model.conf = 0.50  # Minimum confidence threshold for detections
        model.iou = 0.65   # IoU threshold for Non-Maximum Suppression
        return model

    def score_frame(self, frame):
        """
        Runs inference on a single frame and returns:
        - Detected labels (class IDs)
        - Bounding box coordinates (normalized)
        """
        # Move model to the selected device (CPU/GPU)
        self.model.to(self.device)

        # YOLOv5 expects input as a list of images
        frame = [frame]
        results = self.model(frame)

        # Print raw detection results to console
        results.print()
        print(results.xyxy[0])             # Bounding boxes (absolute pixel coords)
        print(results.pandas().xyxy[0])    # Results in Pandas DataFrame format

        # Extract labels and coordinates (normalized 0–1)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        """
        Convert a numerical class ID into the corresponding class label string.
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Draws bounding boxes and labels onto the frame.
        - Only draws boxes if confidence score ≥ 0.2
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]  # Image dimensions

        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:  # Confidence score filter
                # Convert normalized coordinates back to pixel values
                x1, y1, x2, y2 = (
                    int(row[0] * x_shape),
                    int(row[1] * y_shape),
                    int(row[2] * x_shape),
                    int(row[3] * y_shape),
                )
                bgr = (0, 255, 0)  # Green bounding box
                # Draw rectangle around object
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                # Draw class label text
                cv2.putText(frame, self.class_to_label(labels[i]),
                            (x1, y1), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, bgr, 2)

        return frame


def main():
    """
    Main function to:
    - Initialize the camera
    - Run YOLOv5 detector on live stream frames
    - Display results with bounding boxes and FPS
    - Exit gracefully on 'q' key press
    """
    camera = dahengCamera(1, True)  # Initialize Daheng camera
    object_detector = YoloV5Detector()  # Initialize YOLOv5 detector

    if not camera.isOpen():  # Check if camera opened successfully
        return
    print("Press [q] and then [Enter] to Exit the Program")
    camera.startStraem()  # Start video stream

    start_time = time.perf_counter()
    while True:
        image = camera.grab_frame()  # Capture a frame
        if image is not None:
            # Run detection
            results = object_detector.score_frame(image)
            image = object_detector.plot_boxes(results, image)

            # Calculate FPS (time between frames)
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)

            # Overlay FPS on image
            cv2.putText(image, f'FPS: {int(fps)}',
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, (0, 255, 0), 2)

            # Show the processed frame
            cv2.imshow("Detected objects Image", image)

            # Quit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStraem()
                cv2.destroyAllWindows()
                return

            start_time = end_time  # Reset timer
        else:
            # If no frame is captured, stop and clean up
            camera.stopStraem()
            camera.close()
            cv2.destroyAllWindows()
            return


if __name__ == "__main__":
    main()
