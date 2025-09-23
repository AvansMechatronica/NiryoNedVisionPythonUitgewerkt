# version:1.0.2506.9201
import time
import ctypes
import gxipy as gx
from gxipy.FlatFieldCorrection import *
import msvcrt
import os
import numpy as np


# 平场校正类型
class FFC_TYPE:
    FFC_UNKNOWN = -1                # Undefined
    FFC_SOFTCAL_SOFTUSE = 0         # The first type of camera does not support flat field adjustment natively; it needs to be achieved through software.
    FFC_SOFTCAL_DEVICEUSE = 1       # The second type of camera does not calculate the flat-field correction coefficients by itself; it relies on software for this calculation (only the bright-field image data is required during the calculation process), but it can apply the flat-field correction coefficients.
    FFC_SOFTCAL_DEVICEUSE_3140 = 2  # The third type of camera cannot calculate the flat-field correction coefficient by itself; it requires software calculation (during the calculation, a bright-field image is needed, and an optional dark-field image can also be collected). However, the flat-field correction coefficient can still be applied.
    FFC_DEVICECAL_DEVICEUSE = 3     # The fourth type of camera is capable of calculating the flat-field correction coefficients by itself and applying these coefficients.

    def __int__(self):
        pass


# 平场校正参数
class GX_FFC_PARAM:
    def __init__(self, expected_gray: int , frame_count : int
                 ,coefficient : str , accuracy : str
                 ,block_size : int , enable_expectedgray : bool):

        self.expected_gray = expected_gray              # FFC expected gray value
        self.frame_count = frame_count                  # FFC Frame Count
        self.coefficient = coefficient                  # FFC Coefficient
        self.accuracy = accuracy                        # FFC Accuracy
        self.block_size = block_size                    # block size
        self.enable_expectedgray = enable_expectedgray  # Enable FFC expected gray value


class IFlatFieldCorrectionProcess:

    # Init
    def __init__(self, cam):
        self.cam = cam
        self.remote_device_feature = self.cam.get_remote_device_feature_control()
        self.block_size = 0
        self.expectedgray = 0
        self.coefficientsize = 0
        self.frame_count = 0
        self.coefficientbuffer = ctypes.create_string_buffer(self.coefficientsize)

    # Set the block size
    def set_blocksize(self, block_size : int):
        try:
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCBlockSize")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCBlockSize")

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_enum_feature("FFCBlockSize").set(block_size)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

        self.block_size = block_size

    # Set the expected gray value
    def set_expectedgray(self, expectedgray : int):
        try:
            # Obtain whether the node is supported and writable
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCExpectedGray")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCExpectedGray")

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_int_feature("FFCExpectedGray").set(expectedgray)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

        self.expectedgray = expectedgray

    #   Set the number of fusion frames
    def set_framecount(self, frame_count : int):
        try:
            gx.FlatFieldCorrection().set_frame_count(frame_count)

            # Obtain whether the node is supported and writable
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCFrameCount")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCFrameCount")

            strframecount = "FFCFrameCount_" + str(frame_count)

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_enum_feature("FFCFrameCount").set(strframecount)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    #  Get which type of flat-field correction the camera belongs to
    def get_ffctype(self):
        try:
            # Obtain whether the node is supported and writable
            issupport = self.cam.get_remote_device_feature_control().is_implemented("ShadingCorrectionMode")
            isread = self.cam.get_remote_device_feature_control().is_readable("ShadingCorrectionMode")

            if issupport is True and isread is True:
                strSupportType = self.remote_device_feature.get_enum_feature("ShadingCorrectionMode").get()[1]
                if "FlatFieldCorrection" == strSupportType:
                    type = FFC_TYPE.FFC_SOFTCAL_DEVICEUSE_3140
                elif "TailorFlatFieldCorrection" == strSupportType:
                    type = FFC_TYPE.FFC_SOFTCAL_DEVICEUSE
                elif "DeviceFlatFieldCorrection" == strSupportType:
                    type = FFC_TYPE.FFC_DEVICECAL_DEVICEUSE
                else:
                    print("< Unknown Device >")
                    type = FFC_TYPE.FFC_UNKNOWN
            else:
                type = FFC_TYPE.FFC_SOFTCAL_SOFTUSE

            return type

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

        return FFC_TYPE.FFC_UNKNOWN;

    # 设置FFCAccuracy
    def set_ffcaccuracy(self, ffcaccuracy : str):
        try:
            # 获取该节点是否支持以及是否可写
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCAccuracy")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCAccuracy")

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_enum_feature("FFCAccuracy").set(ffcaccuracy)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 设置期望灰度值使能
    def set_expectedgrayenable(self, expectedgrayenable : bool):
        try:
            # 获取该节点是否支持以及是否可写
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCExpectedGrayValueEnable")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCExpectedGrayValueEnable")

            if expectedgrayenable is True:
                value = "On"
            else:
                value = "Off"

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_enum_feature("FFCExpectedGrayValueEnable").set(value)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 设置平场校正系数选择
    def set_coefficient(self, coefficient : str):
        try:
            # 获取该节点是否支持以及是否可写
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCCoefficient")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCCoefficient")

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_enum_feature("FFCCoefficient").set(coefficient)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 计算平场并应用矫正系数
    def calculate(self, need_dark : bool):
        dq_raw_image = None
        start_snap = False
        try:
            # 流层开采
            self.cam.stream_on()
            self.cam.AcquisitionStart.send_command()
            start_snap = True
            dq_raw_image = self.cam.data_stream[0].dq_buf(5000)
            if dq_raw_image is None:
                print("Getting image failed.")
                self.cam.AcquisitionStop.send_command()
                self.cam.stream_off()
                return False
            param = gx.FlatFieldCorrectionParameter()

            param.bright_buf = dq_raw_image.frame_data.image_buf
            type = self.get_ffctype()
            if FFC_TYPE.FFC_SOFTCAL_DEVICEUSE == type:
                param.dark_buf = None
            else:
                if need_dark:
                    print("Dark field acquisition will start. Please cover the lens and press enter key to continue.")
                    input()

                    # 确保得到的是新图
                    time.sleep(1)
                    raw_image = self.cam.data_stream[0].get_image(2000)
                    if raw_image is None:
                        print("Getting image failed.")
                        self.cam.data_stream[0].q_buf(dq_raw_image)
                        self.cam.AcquisitionStop.send_command()
                        self.cam.stream_off()
                        return False
                    param.dark_buf = raw_image.frame_data.image_buf
                else:
                    param.dark_buf = None

            param.pixel_format = dq_raw_image.frame_data.pixel_format
            param.width = dq_raw_image.frame_data.width
            param.height = dq_raw_image.frame_data.height
            param.block_size = self.block_size
            param.expected_gray = self.expectedgray

            size = gx.FlatFieldCorrection().get_coefficients_size(param)

            self.coefficientbuffer = ctypes.create_string_buffer(size)
            self.coefficientsize = size

            gx.FlatFieldCorrection().calculate(param, ctypes.addressof(self.coefficientbuffer), self.coefficientsize)

            self.cam.data_stream[0].q_buf(dq_raw_image)
            self.cam.AcquisitionStop.send_command()
            self.cam.stream_off()

            return True

        except Exception as exception:

            if dq_raw_image is not None:
                self.cam.data_stream[0].q_buf(dq_raw_image)
            if start_snap is True:
                self.cam.AcquisitionStop.send_command()
                self.cam.stream_off()

            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 开启平场校正开关
    def enable_ffc_param(self, enable: bool):
        try:
            # 获取该节点是否支持以及是否可写
            issupport = self.cam.get_remote_device_feature_control().is_implemented("FlatFieldCorrection")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FlatFieldCorrection")
            if enable is True:
                value = "On"
            else:
                value = "Off"

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_enum_feature("FlatFieldCorrection").set(value)

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    def create_ffc_process(self):
        try:
            emFFCType = self.get_ffctype()

            if FFC_TYPE.FFC_SOFTCAL_SOFTUSE == emFFCType:
                pFFCObj = CGXSoftCalSoftUseFFC(self.cam)
            elif FFC_TYPE.FFC_SOFTCAL_DEVICEUSE_3140 == emFFCType:
                pFFCObj = CGXSoftCalDeviceUseFFC(self.cam)
            elif FFC_TYPE.FFC_DEVICECAL_DEVICEUSE == emFFCType:
                pFFCObj = CGXDeviceCalDeviceUseFFC(self.cam)
            else:
                pFFCObj = None

            return pFFCObj

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 设置平场参数
    def set_ffc_param(self, param: GX_FFC_PARAM):
        return

    # 对图像应用平场系数，需先计算系数后应用系数
    def get_ffc_image(self):
        return

    # 导出平场系数
    def save_pcffc(self, path : str):
        try:
            if 0 == self.coefficientsize:
                return False

            with open(path, 'wb') as file:
                file.write(self.coefficientbuffer)
                print("<Save FFC parameters to '%s' file successfully.>" % path)
            return True
        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 导入平场系数
    def load_pcffc(self, path : str):
        try:
            # 获取文件大小
            self.coefficientsize = os.path.getsize(path)
            if 0 == self.coefficientsize:
                return False

            self.coefficientbuffer = ctypes.create_string_buffer(self.coefficientsize)
            with open(path, 'rb') as file:
                self.coefficientbuffer = file.read(self.coefficientsize)
                print("<Successfully loaded FFC configuration file %s.>" % path)
            return True
        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 导出平场系数
    def save_ffc(self, path):
        return

    # 导入平场系数
    def load_ffc(self, path):
        return

    # 导出平场系数
    def save_device_ffc(self, path : str):
        try:
            issupport_size = self.cam.get_remote_device_feature_control().is_implemented("FFCCoefficientsSize")
            isread_size = self.cam.get_remote_device_feature_control().is_readable("FFCCoefficientsSize")

            issupport_valueall = self.cam.get_remote_device_feature_control().is_implemented("FFCValueAll")
            iswrite_valueall = self.cam.get_remote_device_feature_control().is_writable("FFCValueAll")

            if (issupport_size is not True
                    or isread_size is not True
                    or issupport_valueall is not True
                    or iswrite_valueall is not True):
                print("<The device does not support saving FFC parameters to device.>")
                return False

            size = self.cam.get_remote_device_feature_control().get_int_feature("FFCCoefficientsSize").get()
            buffer = self.cam.FFCValueAll.get_buffer()
            with open(path, 'wb') as file:
                file.write(buffer.get_data())
            return True

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 导入平场系数
    def load_device_ffc(self, path : str):
        try:
            issupport_size = self.cam.get_remote_device_feature_control().is_implemented("FFCCoefficientsSize")
            isread_size = self.cam.get_remote_device_feature_control().is_readable("FFCCoefficientsSize")

            issupport_valueall = self.cam.get_remote_device_feature_control().is_implemented("FFCValueAll")
            iswrite_valueall = self.cam.get_remote_device_feature_control().is_writable("FFCValueAll")

            if (issupport_size is not True
                    or isread_size is not True
                    or issupport_valueall is not True
                    or iswrite_valueall is not True):
                print("<The device does not support loading FFC parameters to device.>")
                return False

            # 获取文件大小
            size = os.path.getsize(path)
            if 0 == self.coefficientsize:
                return False

            # 从文件中读取
            with open(path, 'rb') as file:
                buffer = file.read(size)
            self.cam.FFCValueAll.set_buffer(Buffer(create_string_buffer(buffer,len(buffer))))
            return True

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False


# 第一类相机，相机本身不支持平场需通过软件实现
class CGXSoftCalSoftUseFFC(IFlatFieldCorrectionProcess):

    # 初始化
    def __init__(self, cam):
        super().__init__(cam)
        self.enable_ffc = False

    # 设置平场参数
    def set_ffc_param(self, param : GX_FFC_PARAM):
        self.block_size = -1
        if param.enable_expectedgray is True:
            self.expectedgray = param.expected_gray
        else:
            self.expectedgray = -1

        self.set_framecount(param.frame_count)

    # 对图像应用平场系数，需先计算系数后应用系数
    def get_ffc_image(self):
        start_snap = False
        try:
            # 开启相机采集
            self.cam.stream_on()
            self.remote_device_feature.get_command_feature("AcquisitionStart").send_command()
            start_snap = True
            raw_image = self.cam.data_stream[0].get_image(5000)
            if raw_image is None:
                print("Getting image failed.")
                self.cam.AcquisitionStop.send_command()
                self.cam.stream_off()
                return
            # 如果用户启用平场则应用平场系数
            if self.enable_ffc:
                gx.FlatFieldCorrection().flat_field_correction(raw_image.frame_data.image_buf,
                                                               raw_image.frame_data.image_buf
                                                               , gx.DxActualBits().BITS_8, raw_image.frame_data.width,
                                                               raw_image.frame_data.height,
                                                               ctypes.addressof(self.coefficientbuffer),
                                                               self.coefficientsize)
            # 停止采集
            self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
            self.cam.stream_off()

            return raw_image

        except Exception as exception:

            if start_snap is True:
                # 停止采集
                self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
                self.cam.stream_off()

            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 开启平场校正开关
    def enable_ffc_param(self, enable):
        self.enable_ffc = enable

    # 导出平场系数
    def save_ffc(self, path):
        return self.save_pcffc(path)

    # 导入平场系数
    def load_ffc(self, path):
        return self.load_pcffc(path)


# 第二类相机，相机本身不能计算平场系数需要依靠软件计算
class CGXSoftCalDeviceUseFFC(IFlatFieldCorrectionProcess):

    # 初始化
    def __init__(self, cam):
        super().__init__(cam)

    # 设置平场参数
    def set_ffc_param(self, param):

        # 设置blocksize
        self.set_blocksize(param.block_size)
        # 设置期望灰度值
        self.set_expectedgray(param.expected_gray)
        # 设置融合帧数
        self.set_framecount(param.frame_count)
        # 设置期望灰度值使能
        self.set_expectedgrayenable(param.enable_expectedgray)

    # 对图像应用平场系数，需先计算系数后应用系数
    def get_ffc_image(self):
        start_snap = False
        try:

            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCValueAll")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCValueAll")
            if issupport is True and iswrite is True:
                self.cam.FFCValueAll.set_buffer(gx.Buffer(self.coefficientbuffer))

            # 开启相机采集
            self.cam.stream_on()
            self.remote_device_feature.get_command_feature("AcquisitionStart").send_command()
            start_snap = True

            raw_image = self.cam.data_stream[0].get_image(5000)
            if raw_image is None:
                print("Getting image failed.")
                self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
                self.cam.stream_off()
                return

            # 停止采集
            self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
            self.cam.stream_off()
            return raw_image

        except Exception as exception:

            if start_snap is True:
                # 停止采集
                self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
                self.cam.stream_off()

            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 导出平场系数
    def save_ffc(self, path):

        try:
            if path != "":
                return self.save_device_ffc(path)
            else:
                issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCFlashSave")
                iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCFlashSave")

                if issupport is True and iswrite is True:
                    self.remote_device_feature.get_command_feature("FFCFlashSave").send_command()
                    return True
                else:
                    return False

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # 导入平场系数
    def load_ffc(self, path):

        try:
            if path != "":
                return self.load_device_ffc(path)
            else:
                issupport_size = self.cam.get_remote_device_feature_control().is_implemented("FFCCoefficientsSize")
                isread_size = self.cam.get_remote_device_feature_control().is_writable("FFCCoefficientsSize")
                issupport_load = self.cam.get_remote_device_feature_control().is_implemented("FFCFlashLoad")
                iswrite_load = self.cam.get_remote_device_feature_control().is_writable("FFCFlashLoad")
                issupport_valueall = self.cam.get_remote_device_feature_control().is_implemented("FFCValueAll")
                iswrite_valueall = self.cam.get_remote_device_feature_control().is_readable("FFCValueAll")
                issupport_ffccoefficientssize = issupport_size and isread_size
                issupport_ffcflashload = issupport_load and iswrite_load
                issupport_ffcvalueall = issupport_valueall and iswrite_valueall

                if issupport_ffccoefficientssize is not True or issupport_ffcflashload is not True or issupport_ffcvalueall is not True:
                    return False

                self.coefficientsize = self.cam.get_remote_device_feature_control().get_int_feature(
                    "FFCCoefficientsSize").get()
                self.coefficientbuffer = ctypes.create_string_buffer(self.coefficientsize)
                self.cam.FFCFlashLoad.send_command()
                self.coefficientbuffer = self.cam.FFCValueAll.get_buffer()
                return True
        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False


# The third type of camera cannot calculate the flat-field correction coefficient by itself;
# it requires software calculation
# (during the calculation, a bright-field image is needed,
# and an optional dark-field image can also be collected).
# However, the flat-field correction coefficient can still be applied.
class CGXDeviceCalDeviceUseFFC(IFlatFieldCorrectionProcess):

    # 初始化
    def __init__(self, cam):
        super().__init__(cam)

    # Set the flat-field correction parameters
    def set_ffc_param(self, param):

        # Set block size
        self.set_blocksize(param.block_size)
        # Set the expected gray value
        self.set_expectedgray(param.expected_gray)
        # Set the frame count
        self.set_framecount(param.frame_count)
        # Set the ExpectedGrayEnable
        self.set_expectedgrayenable(param.enable_expectedgray)
        # Set the flat field correction coefficient
        self.set_coefficient(param.coefficient)
        # Set the accuracy of the flat-field correction algorithm
        self.set_ffcaccuracy(param.accuracy)

    # Calculate the flat field correction coefficient
    def calculate(self, need_dark):
        start_snap = False
        try:
            # Send the command to start the acquisition.
            self.cam.stream_on()
            self.remote_device_feature.get_command_feature("AcquisitionStart").send_command()
            start_snap = True

            issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCGenerate")
            iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCGenerate")

            if issupport is True and iswrite is True:
                self.remote_device_feature.get_command_feature("FFCGenerate").send_command()

            # Send the command to stop the acquisition.
            self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
            self.cam.stream_off()
            return True

        except Exception as exception:
            if start_snap is True:
                # 停止采集
                self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
                self.cam.stream_off()

            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # Obtain the image after flat-field correction
    def get_ffc_image(self):
        start_snap = False
        try:
            # Send the command to start the acquisition
            self.cam.stream_on()
            self.remote_device_feature.get_command_feature("AcquisitionStart").send_command()
            start_snap = True

            raw_image = self.cam.data_stream[0].get_image(5000)
            if raw_image is None:
                print("Getting image failed.")
                self.cam.AcquisitionStop.send_command()
                self.cam.stream_off()
                return

            # Send the command to stop the acquisition
            self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
            self.cam.stream_off()
            return raw_image

        except Exception as exception:
            if start_snap is True:
                # Send the command to stop the acquisition
                self.remote_device_feature.get_command_feature("AcquisitionStop").send_command()
                self.cam.stream_off()

            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # Export the flat-field correction coefficients
    def save_ffc(self, path : str):

        try:
            if path != "":
                print("<Saveing flat-field coefficients, please wait...>")
                return self.save_device_ffc(path)
            else:
                issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCFlashSave")
                iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCFlashSave")

                if issupport is True and iswrite is True:
                    self.remote_device_feature.get_command_feature("FFCFlashSave").send_command()
                    return True
                else:
                    return False

        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False

    # Import flat-field correction coefficients
    def load_ffc(self, path : str):

        try:
            if path != "":
                print("<Loading flat-field coefficients, please wait...>")
                return self.load_device_ffc(path)
            else:
                issupport = self.cam.get_remote_device_feature_control().is_implemented("FFCFlashLoad")
                iswrite = self.cam.get_remote_device_feature_control().is_writable("FFCFlashLoad")

                if issupport is True and iswrite is True:
                    self.remote_device_feature.get_command_feature("FFCFlashLoad").send_command()
                    return True
                else:
                    return False
        except Exception as exception:
            # If an AttributeError exception is reported,
            # it indicates that the interface library does not actually support this attribute
            if isinstance(exception, AttributeError):
                print(f"[Print Error Information： %s" % exception)
                assert False
            else:
                assert False


def main():
    create_device = False
    cam = None
    try:
        # Create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_all_device_list()
        if dev_num == 0:
            print("No device!")
            return

        # Open the first camera device
        cam = device_manager.open_device_by_index(1)
        remote_device_feature = cam.get_remote_device_feature_control()
        create_device = True

        # Load parameter group
        remote_device_feature.get_enum_feature("UserSetSelector").set("Default")
        remote_device_feature.get_command_feature("UserSetLoad").send_command()

        print("***********************************************")
        print(f"<Vendor Name:   {dev_info_list[0]['vendor_name']}>")
        print(f"<Model Name:    {dev_info_list[0]['model_name']}>")
        print(f"<Serial Number:    {dev_info_list[0]['sn']}>")
        print("***********************************************")

        # 1.Create an FFC processing object
        pFFCObj = IFlatFieldCorrectionProcess(cam).create_ffc_process()
        if pFFCObj is None:
            if create_device is True:
                # close device
                cam.close_device()
            print("<create flat field correction process error, App exit!>")
            return

        # 2.Set flat field correction parameters
        stFFCParam = GX_FFC_PARAM(0,0,"","",0,False)
        stFFCParam.expected_gray = 127
        stFFCParam.frame_count = 1

        issupport = cam.get_remote_device_feature_control().is_implemented("FFCCoefficient")
        isread = cam.get_remote_device_feature_control().is_readable("FFCCoefficient")
        if issupport is True and isread is True:
            value = cam.get_remote_device_feature_control().get_enum_feature("FFCCoefficient").get()
            stFFCParam.coefficient = value[1]

        issupport = cam.get_remote_device_feature_control().is_implemented("FFCAccuracy")
        isread = cam.get_remote_device_feature_control().is_readable("FFCAccuracy")
        if issupport is True and isread is True:
            value = cam.get_remote_device_feature_control().get_enum_feature("FFCAccuracy").get()
            stFFCParam.accuracy = value[1]

        issupport = cam.get_remote_device_feature_control().is_implemented("FFCBlockSize")
        isread = cam.get_remote_device_feature_control().is_readable("FFCBlockSize")
        if issupport is True and isread is True:
            value = cam.get_remote_device_feature_control().get_enum_feature("FFCBlockSize").get()
            stFFCParam.block_size = int(value[0])

        stFFCParam.enable_expectedgray = True
        pFFCObj.set_ffc_param(stFFCParam)

        # 3.Calculate the flat field correction coefficient. false indicates no dark field collection, and true indicates dark field collection.,
        # Only FFC SOFTCAL SOFTUSE and FFC SOFTCAL DEVICEUSE 3140 types are supported
        bcal = pFFCObj.calculate(False)
        if bcal is False:
            if create_device is True:
                # close device
                cam.close_device()
            print("<Calculate flat field correction error, App exit!>")
            return

        # 4.enable the flat field correction
        benable = True
        pFFCObj.enable_ffc_param(benable)
        print("<Enable flat-field correction.>")

        # 5.Obtain the image after flat-field correction
        raw_image = pFFCObj.get_ffc_image()
        if raw_image is not None:
            if benable is True:
                print("<App get FFC Image Success!>")
            else:
                print("<App get normal Image Success!>")

        # 6.Optionally save the flat field correction coefficient and load the flat field correction coefficient
        # Note that when the "FFCAccuracy" of the FFC DEVICECAL DEVICEUSE class camera is set to PixelLevel, the saving time is relatively long
        # When the save path is passed empty, if the camera supports it,
        # the flat field coefficient will be saved inside the camera, and the return value is whether it was successful or not
        
        # Recommended to run as administrator to avoid save failures due to insufficient permissions when the app is on the system drive.
        bsave = pFFCObj.save_ffc("FlatFieldCorrectionProcess.ffc")
        bload = pFFCObj.load_ffc("FlatFieldCorrectionProcess.ffc")

        # close device
        cam.close_device()

    except Exception as exception:
        if create_device is True:
            # close device
            cam.close_device()

        # If an AttributeError exception is reported,
        # it indicates that the interface library does not actually support this attribute
        if isinstance(exception, AttributeError):
            print(f"[Print Error Information： %s" % exception)
            assert False
        else:
            assert False

    print("<App exit!>")
    return

if __name__ == "__main__":
    main()
