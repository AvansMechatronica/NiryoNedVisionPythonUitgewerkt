import cv2
# import the opencv library
import keyboard  # load keyboard package
from libraries.vision.dahengCamera import dahengCamera
from libraries.vision.ObjectDetector import ObjectDetector
from libraries.vision.Workspace import Workspace
from libraries.vision.enums import *
import time
from pyniryo2 import *
import libraries.niryo.NiryoSupport as Niryo


camera_index = 0
def main():
    camera = dahengCamera(camera_index)

    workspace = Workspace()

    with open('../workspace.json') as inputfile:
        workspace.from_json(inputfile.read())

    robot = NiryoRobot("10.10.10.10")
    robot.arm.calibrate_auto()
    robot.arm.set_learning_mode(False)

    robot.arm.move_pose(Niryo.NED.HOME_POSE)


    '''
    Put your own code here
    '''

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            robot.tool.enable_tcp(False)
            robot.arm.move_to_home_pose()
            robot.arm.set_learning_mode(True)
            camera.end()
            robot.end()
            time.sleep(1)
            break


if __name__ == "__main__":
    main()