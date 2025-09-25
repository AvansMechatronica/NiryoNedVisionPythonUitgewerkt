import cv2
# import the opencv library
import keyboard  # load keyboard package
from libraries.vision.dahengCamera import dahengCamera
from libraries.vision.enums import ColorHSV
from libraries.vision.image_functions import *
from libraries.vision.enums import *
import time

camera_index = 0

display_hsv_channels = False

def nothing(dummy):
    pass

def threshold_hsv(frame_hsv, list_min_hsv, list_max_hsv, reverse_hue=False):
    """
    Take BGR image (OpenCV imread result) and return thresholded image
    according to values on HSV (Hue, Saturation, Value)
    Pixel will worth 1 if a pixel has a value between min_v and max_v for all channels

    :param img: image BGR if rgb_space = False
    :type img: numpy.array
    :param list_min_hsv: list corresponding to [min_value_H,min_value_S,min_value_V]
    :type list_min_hsv: list[int]
    :param list_max_hsv: list corresponding to [max_value_H,max_value_S,max_value_V]
    :type list_max_hsv: list[int]
    :param use_s_prime: True if you want to use S channel as S' = S x V else classic
    :type use_s_prime: bool
    :param reverse_hue: Useful for Red color cause it is at both extremum
    :type reverse_hue: bool
    :return: threshold image
    :rtype: numpy.array
    """


    if not reverse_hue:
        return cv2.inRange(frame_hsv, list_min_hsv, list_max_hsv)
    else:
        list_min_v_c = list_min_hsv
        list_max_v_c = list_max_hsv
        lower_bound_red, higher_bound_red = sorted([list_min_v_c[0], list_max_v_c[0]])
        list_min_v_c[0], list_max_v_c[0] = 0, lower_bound_red
        low_red_im = cv2.inRange(frame_hsv, list_min_v_c, list_max_v_c)
        list_min_v_c[0], list_max_v_c[0] = higher_bound_red, 179
        high_red_im = cv2.inRange(frame_hsv, list_min_v_c, list_max_v_c)
        return cv2.addWeighted(low_red_im, 1.0, high_red_im, 1.0, 0)


def main():
    print("Commands: ")
    print(" q --> Quit")
    print(" s --> Enable streaming(default)")
    print(" p --> Take photo/Disable streaming")

    camera = dahengCamera(camera_index)

    time.sleep(2)

    stream = True

    window_name = 'HSV Threshold'
    cv2.namedWindow(window_name) # Create a window named 'Colorbars'

    # assign strings for ease of coding
    hh = 'Hue High'
    hl = 'Hue Low'
    rh = 'Revers HUE (for RED colors)'
    sh = 'Saturation High'
    sl = 'Saturation Low'
    vh = 'Value High'
    vl = 'Value Low'

    lower_blue = np.array([60, 35, 140])
    upper_blue = np.array([180, 255, 255])

    # Begin Creating trackbars for each
    cv2.createTrackbar(hl, window_name, 0, 179, nothing)
    cv2.setTrackbarPos(hl, window_name, 60)
    cv2.createTrackbar(hh, window_name, 0, 179, nothing)
    cv2.setTrackbarPos(hh, window_name, 179)
    cv2.createTrackbar(rh, window_name, 0, 1, nothing)
    cv2.setTrackbarPos(rh, window_name, 0)
    cv2.createTrackbar(sl, window_name, 0, 255, nothing)
    cv2.setTrackbarPos(sl, window_name, 35)
    cv2.createTrackbar(sh, window_name, 0, 255, nothing)
    cv2.setTrackbarPos(sh, window_name, 255)
    cv2.createTrackbar(vl, window_name, 0, 255, nothing)
    cv2.setTrackbarPos(vl, window_name, 140)
    cv2.createTrackbar(vh, window_name, 0, 255, nothing)
    cv2.setTrackbarPos(vh, window_name, 255)

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            #cv2.destroyAllWindows()
            camera.end()
            break

        if keyboard.is_pressed("p"):  # returns True if "q" is pressed
            image = camera.take_photo(display_photo = False);
            stream = False

        if keyboard.is_pressed("s"):  # returns True if "q" is pressed
            stream = True

        if stream:
            image = camera.take_photo(display_photo = False);


        # read trackbar positions for each trackbar
        hul = cv2.getTrackbarPos(hl, window_name)
        huh = cv2.getTrackbarPos(hh, window_name)
        revers_hue = cv2.getTrackbarPos(rh, window_name)
        sal = cv2.getTrackbarPos(sl, window_name)
        sah = cv2.getTrackbarPos(sh, window_name)
        val = cv2.getTrackbarPos(vl, window_name)
        vah = cv2.getTrackbarPos(vh, window_name)

        # make array for final values
        list_min_hsv = np.array([hul, sal, val])
        list_max_hsv = np.array([huh, sah, vah])


        # convert from a BGR stream to an HSV stream
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = threshold_hsv(hsv, list_min_hsv, list_max_hsv, revers_hue)

        #mask = cv2.inRange(hsv, list_min_hsv, list_max_hsv)

        # The black region in the mask has the value of 0,
        # so when multiplied with original image removes all non-blue regions
        hsv_threshold = cv2.bitwise_and(image, image, mask=mask)

        cv2.imshow("HSV", hsv)
        cv2.imshow(window_name, hsv_threshold)

        if display_hsv_channels:
            h_img, s_img, v_img = cv2.split(hsv)
            cv2.imshow("Hue", h_img)
            cv2.imshow("Saturation", s_img)
            cv2.imshow("Value", v_img)


        cv2.waitKey(1)


if __name__ == "__main__":
    main()
