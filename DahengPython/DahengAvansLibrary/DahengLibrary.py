#!/usr/bin/python
# purpose: Library for Daheng cameras
# auteur: Gerard Harkema
# date: 2024-06-17
# version: 1.00 initial version
#

import os

# zet de omgevingsvariabelen voor de Daheng Galaxy SDK
os.environ["GALAXY_GENICAM_ROOT"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenICam"
os.environ["GENICAM_GENTL64_PATH"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# voeg de paden toe aan de PATH variabele
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenICam\bin\Win64_x64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\"Win64"

# import de benodigde modules
import gxipy as gx
from ctypes import *
from gxipy.gxidef import *
import numpy
from gxipy.ImageFormatConvert import *
import cv2


class dahengCamera:
    """
    Wrapper class for Daheng cameras using the Galaxy SDK.

    Provides methods to:
    - Initialize and open a Daheng camera
    - Configure acquisition and image processing settings
    - Start/stop image streaming
    - Grab frames and convert them to OpenCV-compatible BGR format
    - Close and release the camera safely
    """

    def __init__(self, device_index, debug=False):
        """Initialize the Daheng camera interface and open the given device index."""
        self.debug = debug
        if self.debug:
            print("<DahangDamera: init camera>")
        self.device_manager = gx.DeviceManager()

        self.image_convert = self.device_manager.create_image_format_convert()
        self.image_process = self.device_manager.create_image_process()

        self.frame_counter = 0

        self.open(device_index)

    def open(self, device_index):
        """Open a Daheng camera by index, configure acquisition and image quality settings."""
        dev_num, self.dev_info_list = self.device_manager.update_all_device_list()
        if dev_num == 0:
            if self.debug:
                print("<DahangDamera: No camera found>")
            self.open = False
            return

        # open the first device
        self.cam = self.device_manager.open_device_by_index(device_index)
        self.remote_device_feature = self.cam.get_remote_device_feature_control()

        # get image improvement obj
        image_process_config = self.cam.create_image_process_config()
        image_process_config.enable_color_correction(False)

        # exit when the camera is a mono camera
        pixel_format_value, pixel_format_str = self.remote_device_feature.get_enum_feature("PixelFormat").get()
        if Utility.is_gray(pixel_format_value):
            if self.debug:
                print("<DahangDamera: This sample does not support mono camera.>")
            self.cam.close_device()
            return

        # set continuous acquisition
        trigger_mode_feature = self.remote_device_feature.get_enum_feature("TriggerMode")
        trigger_mode_feature.set("Off")

        # get param of improving image quality
        if self.remote_device_feature.is_readable("GammaParam"):
            gamma_value = self.remote_device_feature.get_float_feature("GammaParam").get()
            image_process_config.set_gamma_param(gamma_value)
        else:
            image_process_config.set_gamma_param(1)
        if self.dev_info_list[0].get("device_class") == gx.GxDeviceClassList.USB2:
            pass
        else:
            if self.remote_device_feature.is_readable("ContrastParam"):
                contrast_value = self.remote_device_feature.get_int_feature("ContrastParam").get()
                image_process_config.set_contrast_param(contrast_value)
            else:
                image_process_config.set_contrast_param(0)

        if 1:
            # Restore default parameter group
            if self.dev_info_list[0].get("device_class") == gx.GxDeviceClassList.USB2:
                pass
            else:
                self.remote_device_feature.get_enum_feature("UserSetSelector").set("Default")

        else:
            # Deze methode werkt niet goed
            if remote_device_feature.is_implemented("UserSetSelector") and remote_device_feature.is_writable("UserSetSelector"):
                print("UserSetSelector bestaat")
                remote_device_feature.get_enum_feature("UserSetSelector").set("Default")
            else:
                print("UserSetSelector bestaat niet")
                remote_device_feature.get_enum_feature("UserSetSelector").set("Default")

        self.remote_device_feature.get_command_feature("UserSetLoad").send_command()

        if self.debug:
            print("<DahangDamera: ***********************************************>")
            print(f"<Vendor Name:   {self.dev_info_list[0]['vendor_name']}>")
            print(f"<Model Name:    {self.dev_info_list[0]['model_name']}>")
            print("<DahangDamera: ***********************************************>")
        self.open = True

    def isOpen(self):
        """Return True if the camera is open, False otherwise."""
        return self.open

    def setSoftwareTriggerMode(self):
        """Set software trigger mode."""
        trigger_mode_feature = self.remote_device_feature.get_enum_feature("TriggerMode")
        if self.dev_info_list[0].get("device_class") == gx.GxDeviceClassList.USB2:
            # set trigger mode
            trigger_mode_feature.set("On")
            print("Trigger mode: USB2")
        else:
            # set trigger mode and trigger source
            trigger_mode_feature.set("On")
            print("Trigger mode: Other")

            trigger_source_feature = self.remote_device_feature.get_enum_feature("TriggerSource")
            trigger_source_feature.set("Software")

    def softwareTrigger(self):
        # send software trigger command
        trigger_software_command_feature = self.remote_device_feature.get_command_feature("TriggerSoftware")
        trigger_software_command_feature.send_command()

    def startStraem(self):
        """Start continuous streaming from the camera."""
        self.cam.stream_on()

    def stopStraem(self):
        """Stop continuous streaming from the camera."""
        self.cam.stream_off()

    def get_best_valid_bits(self, pixel_format):
        """Return the optimal valid bit range for the given pixel format."""
        valid_bits = DxValidBit.BIT0_7
        if pixel_format in (GxPixelFormatEntry.MONO8,
                            GxPixelFormatEntry.BAYER_GR8, GxPixelFormatEntry.BAYER_RG8,
                            GxPixelFormatEntry.BAYER_GB8, GxPixelFormatEntry.BAYER_BG8,
                            GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8,
                            GxPixelFormatEntry.R8, GxPixelFormatEntry.B8, GxPixelFormatEntry.G8):
            valid_bits = DxValidBit.BIT0_7
        elif pixel_format in (GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.MONO10_P,
                              GxPixelFormatEntry.BAYER_GR10, GxPixelFormatEntry.BAYER_RG10,
                              GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_BG10,
                              GxPixelFormatEntry.BAYER_GR10_P, GxPixelFormatEntry.BAYER_RG10_P,
                              GxPixelFormatEntry.BAYER_GB10_P, GxPixelFormatEntry.BAYER_BG10_P,
                              GxPixelFormatEntry.BAYER_GR10_PACKED, GxPixelFormatEntry.BAYER_RG10_PACKED,
                              GxPixelFormatEntry.BAYER_GB10_PACKED, GxPixelFormatEntry.BAYER_BG10_PACKED):
            valid_bits = DxValidBit.BIT2_9
        elif pixel_format in (GxPixelFormatEntry.MONO12, GxPixelFormatEntry.MONO12_PACKED, GxPixelFormatEntry.MONO12_P,
                              GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_RG12,
                              GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_BG12,
                              GxPixelFormatEntry.BAYER_GR12_P, GxPixelFormatEntry.BAYER_RG12_P,
                              GxPixelFormatEntry.BAYER_GB12_P, GxPixelFormatEntry.BAYER_BG12_P,
                              GxPixelFormatEntry.BAYER_GR12_PACKED, GxPixelFormatEntry.BAYER_RG12_PACKED,
                              GxPixelFormatEntry.BAYER_GB12_PACKED, GxPixelFormatEntry.BAYER_BG12_PACKED):
            valid_bits = DxValidBit.BIT4_11
        elif pixel_format in (GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO14_P,
                              GxPixelFormatEntry.BAYER_GR14, GxPixelFormatEntry.BAYER_RG14,
                              GxPixelFormatEntry.BAYER_GB14, GxPixelFormatEntry.BAYER_BG14,
                              GxPixelFormatEntry.BAYER_GR14_P, GxPixelFormatEntry.BAYER_RG14_P,
                              GxPixelFormatEntry.BAYER_GB14_P, GxPixelFormatEntry.BAYER_BG14_P,
                              ):
            valid_bits = DxValidBit.BIT6_13
        elif pixel_format in (GxPixelFormatEntry.MONO16,
                              GxPixelFormatEntry.BAYER_GR16, GxPixelFormatEntry.BAYER_RG16,
                              GxPixelFormatEntry.BAYER_GB16, GxPixelFormatEntry.BAYER_BG16):
            valid_bits = DxValidBit.BIT8_15
        return valid_bits

    def convert_to_RGB(self, raw_image):
        """Convert a raw image from the camera into RGB format."""
        self.image_convert.set_dest_format(GxPixelFormatEntry.RGB8)
        valid_bits = self.get_best_valid_bits(raw_image.get_pixel_format())
        self.image_convert.set_valid_bits(valid_bits)

        # create out put image buffer
        buffer_out_size = self.image_convert.get_buffer_size_for_conversion(raw_image)
        output_image_array = (c_ubyte * buffer_out_size)()
        output_image = addressof(output_image_array)

        # convert to rgb
        self.image_convert.convert(raw_image, output_image, buffer_out_size, False)
        if output_image is None:
            if self.debug:
                print("<DahangDamera: : Failed to convert RawImage to RGBImage>")
            return

        return output_image_array, buffer_out_size

    def grab_frame(self, timeout = 1000):
        """Capture a single frame, convert it to BGR (OpenCV format), and return it as a NumPy array."""
        self.frame_counter += 1
        if self.debug:
            print(f"<DahangDamera: grab_frame {self.frame_counter}>")
        if not self.open:
            if self.debug:
                print("<DahangDamera: : camera not open>")
            return None
        try:
            raw_image = self.cam.data_stream[0].get_image(timeout)
            if raw_image is None:
                if self.debug:
                    print("<DahangDamera: Getting image failed.>")
                return None

            # get RGB image from raw image
            image_buf = None
            if raw_image.get_pixel_format() != GxPixelFormatEntry.RGB8:
                rgb_image_array, rgb_image_buffer_length = self.convert_to_RGB(raw_image)
                if rgb_image_array is None:
                    return None
                numpy_image = numpy.frombuffer(rgb_image_array, dtype=numpy.ubyte,
                                               count=rgb_image_buffer_length).reshape(
                    raw_image.frame_data.height,
                    raw_image.frame_data.width,
                    3
                    )
                image_buf = addressof(rgb_image_array)
            else:
                numpy_image = raw_image.get_numpy_array()
                image_buf = raw_image.frame_data.image_buf

                rgb_image = GxImageInfo()
                rgb_image.image_width = raw_image.frame_data.width
                rgb_image.image_height = raw_image.frame_data.height
                rgb_image.image_buf = image_buf
                rgb_image.image_pixel_format = GxPixelFormatEntry.RGB8

                # improve image quality
                self.image_process.image_improvement(rgb_image, image_buf, self.image_process_config)

                if numpy_image is None:
                    return None

            # Convert RGB to BGR for OpenCV
            bgr_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

            return bgr_image

        except Exception as ex:
            if self.debug:
                print(f"Error: {str(ex)}>")
            return None

    def close(self):
        """Close the Daheng camera and release resources."""
        if self.debug:
            print("<DahangDamera: Close camera>")
        #self.cam.close_device()
        self.cam.close()
        self.open = False
        pass

    def __del__(self):
        """Ensure the camera is closed when the object is deleted."""
        self.close()
