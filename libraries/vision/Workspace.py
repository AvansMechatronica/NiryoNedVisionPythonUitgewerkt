from pyniryo import *
import json
import math
import numpy as np
from libraries.vision.transform_functions import *

from cv2 import *



class Workspace:

    def __init__(self):

        self.UpperLeftPose = PoseObject(x=-1000.0, y=-1000.0, z=0.1, roll=0, pitch=0, yaw=0) # 1
        self.UpperRightPose = PoseObject(x=1000.0, y=-1000.0, z=0.1, roll=0, pitch=0, yaw=0) # 2
        self.LowerRightPose = PoseObject(x=1000.0, y=500.0, z=0.1, roll=0, pitch=0, yaw=0) # 3
        self.LowerLeftPose = PoseObject(x=-1000.0, y=500.0, z=0.1, roll=0, pitch=0, yaw=0) # 4
        self.orgin = PoseObject(x=0, y=0, z=0, roll=0, pitch=1.57, yaw=0)
        #self.calculate_parameters();

    def calculate_parameters(self):
        self.orgin.x = self.UpperLeftPose.x
        self.orgin.y = self.UpperLeftPose.y
        a = self.UpperRightPose.x - self.UpperLeftPose.x
        b = self.UpperRightPose.y - self.UpperLeftPose.y
        self.width = math.sqrt((math.pow(a, 2) + math.pow(b, 2)))

        self.orgin.yaw = math.asin(a/self.width)
        #print("Width: " + str(self.width))
        #print("Yaw (graden): " + str(np.rad2deg(self.orgin.yaw)))

        a = self.LowerLeftPose.x - self.UpperLeftPose.x
        b = self.LowerLeftPose.y - self.UpperLeftPose.y

        self.height = math.sqrt((math.pow(a, 2) + math.pow(b, 2)))
        #print("Height: " + str(self.height))
        self.orgin.z = (self.UpperRightPose.z + self.UpperLeftPose.z + self.LowerRightPose.z + self.LowerLeftPose.z) / 4
        #print("Orgin: " + str(self.orgin))

    def set(self, _upper_left_pose, _upper_right_pose, _lower_right_pose, _lower_left_pose):
        self.LowerRightPose = _lower_right_pose
        self.LowerLeftPose = _lower_left_pose
        self.UpperRightPose = _upper_right_pose
        self.UpperLeftPose = _upper_left_pose
        self.calculate_parameters();

    def get(self):
        return self.UpperRightPose, self.UpperLeftPose, self.LowerRightPose, self.LowerLeftPose

    def to_json(self):
        poses_json = {}

        poses_json["UpperLeftPose"] = {}
        poses_json["UpperLeftPose"]['x'] = self.UpperLeftPose.x
        poses_json["UpperLeftPose"]['y'] = self.UpperLeftPose.y
        poses_json["UpperLeftPose"]['z'] = self.UpperLeftPose.z

        poses_json["UpperRightPose"] = {}
        poses_json["UpperRightPose"]['x'] = self.UpperRightPose.x
        poses_json["UpperRightPose"]['y'] = self.UpperRightPose.y
        poses_json["UpperRightPose"]['z'] = self.UpperRightPose.z


        poses_json["LowerRightPose"] = {}
        poses_json["LowerRightPose"]['x'] = self.LowerRightPose.x
        poses_json["LowerRightPose"]['y'] = self.LowerRightPose.y
        poses_json["LowerRightPose"]['z'] = self.LowerRightPose.z

        poses_json["LowerLeftPose"] = {}
        poses_json["LowerLeftPose"]['x'] = self.LowerLeftPose.x
        poses_json["LowerLeftPose"]['y'] = self.LowerLeftPose.y
        poses_json["LowerLeftPose"]['z'] = self.LowerLeftPose.z

        json_string = json.dumps(poses_json)
        return json_string

    def from_json(self, json_string):
        poses_json = json.loads(json_string)
        try:
            self.UpperRightPose.x = poses_json["UpperRightPose"]['x']
            self.UpperRightPose.y = poses_json["UpperRightPose"]['y']
            self.UpperRightPose.z = poses_json["UpperRightPose"]['z']

            self.UpperLeftPose.x = poses_json["UpperLeftPose"]['x']
            self.UpperLeftPose.y = poses_json["UpperLeftPose"]['y']
            self.UpperLeftPose.z = poses_json["UpperLeftPose"]['z']

            self.LowerRightPose.x = poses_json["LowerRightPose"]['x']
            self.LowerRightPose.y = poses_json["LowerRightPose"]['y']
            self.LowerRightPose.z = poses_json["LowerRightPose"]['z']

            self.LowerLeftPose.x = poses_json["LowerLeftPose"]['x']
            self.LowerLeftPose.y = poses_json["LowerLeftPose"]['y']
            self.LowerLeftPose.z = poses_json["LowerLeftPose"]['z']
            self.calculate_parameters();
        except KeyError as ke:
            print('Key Not Found in Poses Dictionary:', ke)
            return False
        return True

    if 1:
        def get_pose(self, x_rel, y_rel, yaw_rel, yaw_center=None):
            # simple way, better to implement vectors

            pose = PoseObject(x=0, y=0, z=0, roll=0, pitch=0, yaw=0)

            # x-direction
            rel_x_ws = self.height * x_rel
            print("rel x: " + str(rel_x_ws))
            abs_x_ws = self.orgin.x + rel_x_ws
            pose.x = abs_x_ws

            # y-direction
            rel_y_ws = self.width * y_rel
            print("rel y: " + str(rel_y_ws))
            abs_y_ws = self.orgin.y + rel_y_ws
            pose.y = abs_y_ws

            # x-direction
            pose.z = self.orgin.z
            pose.pitch = self.orgin.pitch
            pose.roll = self.orgin.roll

            # yaw-orientation
            pose.yaw = self.orgin.yaw + yaw_rel

            return pose
    else:

        def get_pose(self, x_rel, y_rel, yaw_rel, yaw_center=None):
            """
            !!! Not tested yet !!!!

            Transform the pose in the workspace to the world pose

            :param workspace: dict of the workspace which contains name, matrix, ratio
            :param x_rel: object base x position relative to workspace
            :param y_rel: object base y position relative to workspace
            :param yaw_rel: object base rotation on z relative to workspace
            :param yaw_center: Avoid over rotation
            """

            position_matrix = np.empty(shape=[0, 3])
            rotation_matrix = np.empty(shape=[0, 4])

            position_list = [self.UpperLeftPose, self.UpperRightPose, self.LowerLeftPose, self.LowerRightPose]
            for position in position_list:
                position_matrix = np.append(position_matrix, [[position.x, position.y, position.z]], axis=0)
                quaternion = quaternion_from_euler(position.roll, position.pitch, position.yaw)
                rotation_matrix = np.append(rotation_matrix, [[quaternion[0], quaternion[1], quaternion[2], quaternion[3]]],
                                            axis=0)

            print("position_matrix: ")
            print(position_matrix)
            print("rotation_matrix: ")
            print(rotation_matrix)
            position = np.dot(position_matrix, np.array([x_rel, y_rel, 1]))
            print("position: ")
            print(position)
            camera_rotation = euler_matrix(0, 0, yaw_rel)
            print("camera_rotation: ")
            print(camera_rotation)
            # Here we correct the object orientation to be similar to base_link if
            # the object in on the ground. Not neccessarily needed to be honest...
            convention_rotation = np.array([[0, -1, 0, 0],
                                            [-1, 0, 0, 0],
                                            [0, 0, -1, 0],
                                            [0, 0, 0, 1]])

            object_rotation = concatenate_matrices(
                rotation_matrix, camera_rotation, convention_rotation)
            roll, pitch, yaw = euler_from_matrix(object_rotation)

            # Correcting yaw to avoid out of reach targets
            if yaw_center is not None:
                if yaw < yaw_center - np.pi / 2:
                    yaw += np.pi
                elif yaw > yaw_center + np.pi / 2:
                    yaw -= np.pi

            q = quaternion_from_euler(roll, pitch, yaw)

            return position, [roll, pitch, yaw]
            return position, q
