# import the opencv library
import cv2
import logging
import threading
import time
import numpy as np
from PIL import ImageEnhance
from PIL import Image as pil_image
from DahengAvansLibrary.DahengLibrary import dahengCamera as daheng_camera

class dahengCamera:
    abort = False

    def __init__(self, cameraIndex = 1, display_stream = True, frame_name = "Stream", rotate_frame = False):

        self.camera = daheng_camera(cameraIndex, True)


        if not self.camera.isOpen():
            return

        print("Press [q] and then [Enter] to Exit the Program")
        self.camera.startStraem()


        self.stream_frame_name = frame_name
        self.display_stream = display_stream
        self.rotate_frame = rotate_frame

        self.brightness = 1.0
        self.contrast = 1.0
        self.saturation = 1.0

        self.thread = threading.Thread(target=self.thread_func)
        self.thread.start()
        self.abort = False
        self.abort_ready = False

        self.display_crosshair = False
        time.sleep(0.5) # Wait a while for starting te thread

    def thread_func(self):
        while not self.abort:
            time.sleep(0.1)
            self.orig_frame = self.camera.grab_frame()
            if self.orig_frame is not None:
                if self.rotate_frame:
                    self.orig_frame = cv2.rotate(self.orig_frame, cv2.ROTATE_180)
                self.frame = self.adjust_image(self.orig_frame)
                if self.display_stream:
                    if self.display_crosshair:
                        height = self.frame.shape[0]
                        width = self.frame.shape[1]
                        cv2.line(self.frame, (int(width/2), 0), (int(width/2), height-1), (0, 255, 0), 1)
                        cv2.line(self.frame, (0, int(height/2)), (width-1, int(height/2)), (0, 255, 0), 1)
                    cv2.imshow(self.stream_frame_name, self.frame)
                    cv2.waitKey(1)

        self.abort_ready = True

    def enable_crosshair(self, enable):
        self.display_crosshair = enable

    def end(self):
        #self.x.join()
        self.abort = True;
        while not self.abort_ready:
            time.sleep(0.1)
        # Destroy all the windows
        cv2.destroyAllWindows()
        self.camera.close()

    def take_photo(self, display_photo = True, frame_name = "Photo"):
        self.photo = self.frame.copy()
        if display_photo:
            cv2.imshow(frame_name, self.photo)
            cv2.waitKey(1)
        return self.photo

    def display_photo(self, frame_name = "Photo"):
        if self.photo != None:
            cv2.imshow(frame_name, self.photo)
            cv2.waitKey(1)

    def adjust_image(self, img):
        if self.brightness == self.contrast == self.saturation == 1.:
            return img

        im_pil = PILImage.fromarray(img)

        if self.brightness != 1.:
            brightness_filter = ImageEnhance.Brightness(im_pil)
            im_pil = brightness_filter.enhance(self.brightness)

        if self.contrast != 1.:
            contrast_filter = ImageEnhance.Contrast(im_pil)
            im_pil = contrast_filter.enhance(self.contrast)

        if self.saturation != 1.:
            color_filter = ImageEnhance.Color(im_pil)
            im_pil = color_filter.enhance(self.saturation)

        # For reversing the operation:
        im_np = np.asarray(im_pil)
        return im_np

    def set_brightness(self, brightness):
        self._brightness = brightness

    def set_contrast(self, contrast):
        self._contrast = contrast

    def set_saturation(self, saturation):
        self._saturation = saturation