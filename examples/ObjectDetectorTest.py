import cv2
# import the opencv library
import keyboard  # load keyboard package
from libraries.vision.dahengCamera import dahengCamera
from libraries.vision.markers_detection import *
from libraries.vision.ObjectDetector import ObjectDetector
from libraries.vision.Workspace import Workspace
from libraries.vision.enums import *
import time

camera_index = 1

def main():
    camera = dahengCamera(camera_index)

    workspace = Workspace()

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            camera.end();
            break

        if keyboard.is_pressed("p"):  # returns True if "q" is pressed
            image = camera.take_photo()
            detector = ObjectDetector(
                obj_type=ObjectType.ANY, obj_color=ColorHSVPrime.RED,
                workspace_ratio=1.0,
                ret_image_bool=True,
            )
            all = False
            if all:
                status, cx_rel_list, cy_rel_list, list_size, angle_list, color_list, object_type_list = detector.extract_all_object_with_hsv(image)
            else:
                status, result_pose, obj_type, obj_color, im_draw = detector.extract_object_with_hsv(image)
                if status:
                    print(result_pose)
                    print(obj_type)
                    print(obj_color)
                    cv2.imshow("Result", im_draw)
                    cv2.waitKey(1)
                    #realword_pose = workspace.get_pose(result_pose.x, result_pose.y, result_pose.yaw)
                    #print(realword_pose)
            time.sleep(1)


if __name__ == "__main__":
    main()