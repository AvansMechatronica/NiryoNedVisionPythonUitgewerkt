import time

from pyniryo import *
import cv2
# import the opencv library
import keyboard  # load keyboard package
from libraries.vision.markers_detection import *
from libraries.vision.usbCamera import usbCamera
import libraries.niryo.NiryoSupport as Niryo
from libraries.vision.enums import *

camera_index = 0
# The pose from where the image processing happens

camera = usbCamera(camera_index, rotate_frame= True)
def takePhoto():
    image = camera.take_photo()
    result, crop_image = extract_img_markers(image, workspace_ratio=1.0)
    if result:
        cv2.imshow("Crop", crop_image)
    else:
        print("Unable to extract image markers")

    result, marker_image = draw_markers(image, workspace_ratio=1.0)
    if result:
        cv2.imshow("Marker", marker_image)
    else:
        print("Unable to draw image markers")
    cv2.waitKey(1)

def main():
    print("Commands: ")
    print(" q --> Quit")
    print(" o --> Goto to observation-pose")
    print(" r --> Goto resting-pose")
    print(" p --> Take Photo")
    print(" s --> Save Image")

    robot = NiryoRobot("10.10.10.10")
    #robot.reset_calibration()
    #robot.request_new_calibration()
    robot.calibrate_auto()

    robot.set_learning_mode(False)

    #print("Enable TCP")

    robot.enable_tcp(False)
    #robot.reset_tcp()

    print("To home pose")
    robot.move_pose(Niryo.NED.HOME_POSE)

    print("To observation")
    robot.move_pose(Niryo.NED.OBSERVATION_POSE)

    print("Take photo")
    takePhoto()

    print("Disable TCP")

    robot.set_tcp(Niryo.NED.FINGER_GRIPPER_TCP_OFFSET)
    robot.enable_tcp(True)

    test_pose = PoseObject(
        x=0.15, y=-0.1, z=0.10,
        roll=-1.57, pitch=1.5, yaw=-1.57
    )

    print("To test pose with tcp")
    robot.move_pose(test_pose)

    print("Disable TCP")
    robot.enable_tcp(False)
    robot.reset_tcp()

    print("To test pose without tcp")
    robot.move_pose(test_pose)

    print("To home pose")
    robot.move_pose(Niryo.NED.HOME_POSE)

    print("To resting pose")
    robot.move_to_home_pose()

    print("Ready")
    robot.set_learning_mode(True)

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            robot.move_to_home_pose()
            robot.set_learning_mode(True)
            camera.end();
            robot.end()
            time.sleep(0.5)
            break
        if keyboard.is_pressed("o"):  # returns True if "o" is pressed
            print("To observation")
            robot.set_learning_mode(False)
            robot.move_pose(Niryo.NED.OBSERVATION_POSE)
            camera.enable_crosshair(True)
            time.sleep(0.5)
        if keyboard.is_pressed("r"):  # returns True if "o" is pressed
            print("To resting pose")
            robot.move_to_home_pose()
            robot.set_learning_mode(True)
            time.sleep(0.5)
        if keyboard.is_pressed("p"):  # returns True if "o" is pressed
            print("Take photo")
            takePhoto()
            time.sleep(0.5)

if __name__ == "__main__":
    main()