from pyniryo import *
import time

def main():
    robot = NiryoRobot("10.10.10.10")

    pose = robot.get_pose()

    print(pose)

    robot.end()
    time.sleep(1)

if __name__ == "__main__":
    main()