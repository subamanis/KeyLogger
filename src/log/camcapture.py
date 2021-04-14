import cv2
from decorators.decorators import benchmark


@benchmark("cam capture")
def capture_cam_frame():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        return
    cv2.imwrite("opencv_frame_.png", frame)
    cam.release()
