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

camera_index = 1

def main():

    camera = dahengCamera(camera_index, rotate_frame= True)

    workspace = Workspace()

    with open('../workspace.json') as inputfile:
        workspace.from_json(inputfile.read())

    robot = NiryoRobot("10.10.10.10")
    #robot.arm.reset_calibration()
    if 0:
        robot.arm.request_new_calibration()
    robot.arm.calibrate_auto()
    robot.arm.set_learning_mode(False)
    robot.tool.enable_tcp(False)


    print("To observation")
    robot.arm.move_pose(Niryo.NED.OBSERVATION_POSE)

    if 1:
        print("Enable TCP")
        robot.tool.set_tcp(Niryo.NED.FINGER_GRIPPER_TCP_OFFSET)
        robot.tool.enable_tcp(True)


    image = camera.take_photo()
    detector = ObjectDetector(
        obj_type=ObjectType.ANY, obj_color=ColorHSVPrime.RED,
        workspace_ratio=1.0,
        ret_image_bool=True,
    )

    status, result_pose, obj_type, obj_color, im_draw = detector.extract_object_with_hsv(image)
    if status:
        print("result pose: " + str(result_pose))
        print("object type: " + str(obj_type))
        print("object color: " + str(obj_color))
        cv2.imshow("Result", im_draw)
        cv2.waitKey(1) # Forse display images

        realworld_pose = workspace.get_pose(result_pose.x, result_pose.y, result_pose.yaw)
        print(realworld_pose)


        z_offset = 0.03

        print("Orgin realworld: " + str(realworld_pose))

        realworld_pose.z += z_offset
        print("New realworld: " + str(realworld_pose))
        time.sleep(1)
        robot.arm.move_pose(realworld_pose)
        print("Ready")

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            robot.tool.enable_tcp(False)
            robot.arm.move_pose(Niryo.NED.HOME_POSE)
            robot.arm.move_to_home_pose()
            robot.arm.set_learning_mode(True)
            camera.end()
            robot.end()
            time.sleep(1)
            break


if __name__ == "__main__":
    main()