#!/usr/bin/python
"""
Example: Using Daheng Camera in software trigger Mode
-----------------------------------------------------

This script demonstrates how to:
- Initialize and open a Daheng camera using the DahengAvansLibrary wrapper.
- Start image streaming.
- Capture frames and display them using OpenCV.
- Gracefully stop the stream and close the camera.

Controls:
- Press 'q' (and then Enter) while the OpenCV window is active to stop streaming and exit.

Requirements:
- Daheng Galaxy SDK installed
- gxipy Python package
- OpenCV (cv2)

Author: Gerard Harkema
Date:   2025-09-19
Version: 1.00 (initial version)
"""

# import the Daheng library
from DahengAvansLibrary.DahengLibrary import dahengCamera
import cv2
import time


def main():
    camera = dahengCamera(1, True)

    if not camera.isOpen():
        return
    camera.setSoftwareTriggerMode()
    print("Press [q] and then [Enter] to Exit the Program")
    camera.startStraem()

    while True:
        camera.softwareTrigger()
        image = camera.grab_frame()
        if image is not None:
            cv2.imshow("Acquired Image", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStraem()
                cv2.destroyAllWindows()
                return
        else:
            camera.stopStraem()
            camera.close()
            cv2.destroyAllWindows()
            return

        time.sleep(0.5)



if __name__ == "__main__":
    main()
