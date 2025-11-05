import time
from pyniryo import *

def main():

    #define poses
    home_pose = PoseObject(
        x=0.25, y=0.0, z=0.4,
        roll=-1.571, pitch=1.571, yaw=-1.571
    )
    left_pose = PoseObject(
        x=0.25, y=-0.2, z=0.4,
        roll=-1.571, pitch=1.571, yaw=-1.571
    )
    right_pose = PoseObject(
        x=0.25, y=0.2, z=0.4,
        roll=-1.571, pitch=1.571, yaw=-1.571
    )
    poses = [home_pose, left_pose, right_pose, home_pose]

    print("Start")

    print("Connect to NiryoRobot")
    robot = NiryoRobot("10.10.10.10")
    #robot.reset_calibration()
    if 0:
        robot.request_new_calibration()
    print("Calibrate NiryoNED if necessary")
    robot.calibrate_auto()
    robot.set_learning_mode(False)
    robot.enable_tcp(False)

    print("Close gripper")
    robot.open_gripper(speed=300)

    print("Move NiryoNED along poses")
    for pose in poses:
        robot.move_pose(pose)

    print("Close gripper")
    robot.close_gripper(speed=300)
    time.sleep(2)
    print("Open gripper")


    print("Move NiryoNED 0.2 m down")
    new_pose = home_pose.copy_with_offsets(z_offset=-0.2)
    robot.move_pose(new_pose)
    time.sleep(2)
    print("Move NiryoNED to home position")
    robot.move_pose(home_pose)
    robot.end()

    print("Ready")

if __name__ == "__main__":
    main()