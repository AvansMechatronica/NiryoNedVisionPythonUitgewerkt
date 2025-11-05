from pyniryo import *

class ONE:
    pass

class NED:
    # NED default poses
    OBSERVATION_POSE = PoseObject(
        x=0.15, y=0.0, z=0.4,
        roll=-1.571, pitch=1.571, yaw=-1.571
    )

    OBSERVATION_POSE_TCP_OFFSET = PoseObject(
        x=-0.038, y=0.0, z=0.038,
        roll=0.0, pitch=0.0, yaw=0.0
    )

    HOME_POSE = PoseObject(
        x=0.25, y=-0.0, z=0.4,
        roll=0.0, pitch=0.0, yaw=0.0
    )
    # Tool Centre Point offsets
    FINGER_GRIPPER_TCP_OFFSET = PoseObject(
        x=0.085, y=-0.0, z=0.0,
        roll=0.0, pitch=0.0, yaw=0.0
    )
    ADAPTIVE_GRIPPER_TCP_OFFSET = PoseObject(
        x=0.1215, y=-0.0, z=0.0,
        roll=0.0, pitch=0.0, yaw=0.0
    )
    VACUUM_GRIPPER_TCP_OFFSET = PoseObject(
        x=0.0, y=-0.0, z=0.0,
        roll=0.0, pitch=0.0, yaw=0.0
    )


class NED2:
    # NED2 poses ar the sam as the NED
    OBSERVATION_POSE = NED.OBSERVATION_POSE
    OBSERVATION_POSE_TCP_OFFSET = NED.OBSERVATION_POSE_TCP_OFFSET
    HOME_POSE = NED.HOME_POSE
    FINGER_GRIPPER_TCP_OFFSET = NED.FINGER_GRIPPER_TCP_OFFSET
    VACUUM_GRIPPER_OFFSET = NED.VACUUM_GRIPPER_TCP_OFFSET
    ADAPTIVE_GRIPPER_TCP_OFFSET = NED.ADAPTIVE_GRIPPER_TCP_OFFSET
