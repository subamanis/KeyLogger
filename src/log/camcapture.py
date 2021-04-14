import cv2
from decorators.decorators import benchmark
from log import namegenerator


@benchmark("cam capture")
def capture_cam_frame():
    cam:cv2.VideoCapture = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        print('failed to grab frame')
        return
    cv2.imwrite(namegenerator.get_cam_capture_name(), frame)
    cam.release()
