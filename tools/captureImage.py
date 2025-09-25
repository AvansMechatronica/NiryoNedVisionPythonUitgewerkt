# import the opencv library
import keyboard  # load keyboard package

from libraries.vision.dahengCamera import dahengCamera
from libraries.vision.enums import *
import easygui
camera_index = 0
def main():

    print("Commands: ")
    print(" q --> Quit")
    print(" p --> Take Photo")
    print(" s --> Save Image")

    camera = dahengCamera(camera_index)
    image = None

    while True:
        if keyboard.is_pressed("q"):  # returns True if "q" is pressed
            camera.end();
            print("You pressed q")
            break

        if keyboard.is_pressed("p"):  # returns True if "p" is pressed
            image = camera.take_photo();

        if keyboard.is_pressed("s"):  # returns True if "p" is pressed
            if image is not None:
                save_title = "Save the image as..."
                file_type = "*.jpg"
                image_path = easygui.filesavebox(title=save_title, default=file_type)
                if image_path is not None:
                    cv2.imwrite(image_path, image)


if __name__ == "__main__":
    main()