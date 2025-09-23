# version:1.0.2406.9261
import gxipy as gx
from gxipy.gxidef import *
import time
from ctypes import *


# Check whether all cameras support ActionCommand and PTP functions
def check_cam_parameters(cam_list):
    print("check is all device support ActionCommand and PTP")
    for cam, sn in cam_list:
        action_item_exist = False
        scheduled_action_item_exist = False
        ptp_item_exist = False
        remote_device_feature = cam.get_remote_device_feature_control()
        enum_list = remote_device_feature.get_enum_feature("GevSupportedOptionSelector").get_range()
        for item in enum_list:
            if item['symbolic'] == "Action":
                action_item_exist = True
            if item['symbolic'] == "ScheduledAction":
                scheduled_action_item_exist = True
            if item['symbolic'] == "Ptp":
                ptp_item_exist = True

        if action_item_exist and scheduled_action_item_exist and ptp_item_exist:
            remote_device_feature.get_enum_feature("GevSupportedOptionSelector").set("Action")
            action_support = remote_device_feature.get_bool_feature("GevSupportedOption").get()
            remote_device_feature.get_enum_feature("GevSupportedOptionSelector").set("ScheduledAction")
            scheduled_action_support = remote_device_feature.get_bool_feature("GevSupportedOption").get()
            remote_device_feature.get_enum_feature("GevSupportedOptionSelector").set("Ptp")
            ptp_support = remote_device_feature.get_bool_feature("GevSupportedOption").get()
            if action_support and scheduled_action_support and ptp_support:
                pass
            else:
                print("SN:", sn, " don't support ActionCommand or PTP")
                return False
        else:
            print("SN:", sn, " don't support ActionCommand or PTP")
            return False

    print("successful check, all device support ActionCommand and PTP")
    return True


# Set camera parameters and start acquisition
def set_cam_parameters_and_start_acquisition(cam_list):
    print("setting cam ActionCommand parameters")
    for cam, sn in cam_list:
        remote_device_feature = cam.get_remote_device_feature_control()
        # load default parameters
        remote_device_feature.get_enum_feature("UserSetSelector").set("Default")
        remote_device_feature.get_command_feature("UserSetLoad").send_command()
        # trigger setting
        remote_device_feature.get_enum_feature("TriggerMode").set("On")
        remote_device_feature.get_enum_feature("TriggerSource").set("Action0")
        remote_device_feature.get_int_feature("ActionDeviceKey").set(1)
        remote_device_feature.get_int_feature("ActionGroupKey").set(1)
        remote_device_feature.get_int_feature("ActionGroupMask").set(0xFFFFFFFF)
        # start acquisition
        cam.stream_on()
    print("setting success")


# Demonstrate ActionCommand function
def show_action_command(cam_list, device_manager):
    print("demonstrate issue_action_command function")

    # demonstrate issue_action_command function
    # broadcast_address support: Broadcast (255.255.255.255), subnet broadcast (192.168.42.255), unicast (192.168.42.42)
    ack_list = device_manager.issue_action_command(device_key=1, group_key=1, group_mask=0xFFFFFFFF,
                                                   broadcast_address="255.255.255.255", special_address="",
                                                   time_out=500, expect_ack_number_res=len(cam_list))
    # print ack
    for ack in ack_list:
        print("Ack Return ip:", ack["device_ip"], " status:", ack["status"])

    # get image
    for cam, sn in cam_list:
        img = cam.data_stream[0].dq_buf(1000)
        print("SN:", sn, " get image success, image status:",
              "complete frame" if img.get_status() == gx.GxFrameStatusList.SUCCESS else "incomplete frame")
        cam.data_stream[0].q_buf(img)


# Demonstrate the ScheduledActionCommand function
def show_scheduled_action_command(cam_list, device_manager):
    print("setting cam PTP parameters")

    for cam, sn in cam_list:
        remote_device_feature = cam.get_remote_device_feature_control()
        remote_device_feature.get_bool_feature("PtpEnable").set(True)

        # First, you should wait for the camera to assign the role, which takes about 8s,
        # and the judgment method is to read the PtpStatus cyclically until the value is Master or Slave,
        # the role assignment is completed.
        # Then carry out time calibration, accuracy to within 1us need time about 1~2min,
        # the judgment method is to continuously set the PtpDataSetLatch of the Slave camera and read the
        # PtpOffsetFromMaster, you can get the time deviation of the Slave relative to the Master,
        # when the PtpOffsetFromMaster absolute value is less than the user's desired time accuracy,
        # time calibration is complete.
        cam_ptp_status = remote_device_feature.get_enum_feature("PtpStatus").get()
        loops = 0
        status_ok = (cam_ptp_status[1] == "Master" or cam_ptp_status[1] == "Slave")
        while not status_ok and loops < 8:
            time.sleep(1)
            loops = loops + 1
            cam_ptp_status = remote_device_feature.get_enum_feature("PtpStatus").get()
            status_ok = (cam_ptp_status[1] == "Master" or cam_ptp_status[1] == "Slave")

        if not status_ok:
            raise Exception("PTP time calibration timeout")

    print("setting success")

    print("demonstrate issue_scheduled_action_command function")
    remote_device_feature.get_command_feature("TimestampLatch").send_command()
    timestamp = remote_device_feature.get_int_feature("TimestampLatchValue").get()
    timestamp = timestamp + 5000000000

    # demonstrate issue_scheduled_action_command function
    # broadcast_address support: Broadcast (255.255.255.255), subnet broadcast (192.168.42.255),
    # unicast (192.168.42.42)
    ack_list = device_manager.issue_scheduled_action_command(device_key=1, group_key=1, group_mask=0xFFFFFFFF,
                                                             action_time=timestamp, broadcast_address="255.255.255.255",
                                                             special_address="", time_out=500,
                                                             expect_ack_number_res=len(cam_list))
    # Waiting for the camera to execute
    time.sleep(10)

    # print ack
    for ack in ack_list:
        print("Ack Return ip:", ack["device_ip"], " status:", ack["status"])

    # get image
    for cam, sn in cam_list:
        img = cam.data_stream[0].dq_buf(1000)
        print("SN:", sn, " get image success, image status:",
              "complete frame" if img.get_status() == gx.GxFrameStatusList.SUCCESS else "incomplete frame")
        cam.data_stream[0].q_buf(img)


# Stop acquisition
def stop_acquisition(cam_list):
    for cam, _ in cam_list:
        try:
            cam.stream_off()
        except _:
            pass


def main():
    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list_ex(GxTLClassList.TL_TYPE_GEV)
    if dev_num < 1:
        print("Gige device less than 1!")
        return

    cam_list = []
    print("open device")

    try:
        index = 1
        for cam_info in dev_info_list:
            cam = device_manager.open_device_by_sn(cam_info["sn"])
            cam_list.append([cam, cam_info["sn"]])
            print("<idx:", index, "> <Model Name:", cam_info["model_name"],
                  "> <Serial Number:", cam_info["sn"], ">")
            index = index + 1

        # Check if all cameras support AcionCommand and ptp functions
        if not check_cam_parameters(cam_list):
            return
        # Setting cam parameters
        set_cam_parameters_and_start_acquisition(cam_list)
        # Demonstrate ActionCommand function
        show_action_command(cam_list, device_manager)
        # Demonstrate the ScheduledActionCommand command
        show_scheduled_action_command(cam_list, device_manager)
        # Stop Acquisition and close cam
        stop_acquisition(cam_list)

    finally:
        for cam, _ in cam_list:
            try:
                cam.close_device()
            except _:
                pass


if __name__ == "__main__":
    main()
