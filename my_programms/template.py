import cv2
# import the opencv library
import keyboard  # load keyboard package
from libraries.vision.dahengCamera import dahengCamera
from libraries.vision.ObjectDetector import ObjectDetector
from libraries.vision.Workspace import Workspace
from libraries.vision.enums import *
import time
from pyniryo import *
import libraries.niryo.NiryoSupport as Niryo


camera_index = 0
def main():
    camera = dahengCamera(camera_index)

    workspace = Workspace()

    with open('../workspace.json') as inputfile:
        workspace.from_json(inputfile.read())

    robot = NiryoRobot("10.10.10.10")
    robot.calibrate_auto()
    robot.set_learning_mode(False)

    robot.move_pose(Niryo.NED.HOME_POSE)


    '''
    Put your own code here
    '''

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            robot.enable_tcp(False)
            robot.move_to_home_pose()
            robot.set_learning_mode(True)
            camera.end()
            robot.end()
            time.sleep(1)
            break


if __name__ == "__main__":
    main()