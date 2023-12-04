import cv2
import numpy as np


def img2sketch(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_gray_image = 255 - gray_image
    blurred_img = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
    inverted_blurred_img = 255 - blurred_img
    pencil_sketch_IMG = cv2.divide(gray_image, inverted_blurred_img, scale=256.0)
#        pencil_sketch_IMG = cv2.equalizeHist(pencil_sketch_IMG)
#        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#        pencil_sketch_IMG = clahe.apply(pencil_sketch_IMG)
#        (thresh, pencil_sketch_IMG) = cv2.threshold(pencil_sketch_IMG, 127, 255, cv2.THRESH_BINARY)
    return pencil_sketch_IMG


def img2countours(image):
    # https://habr.com/ru/articles/676838/
    filterd_image = cv2.medianBlur(image, 7)
    gray_image = cv2.cvtColor(filterd_image, cv2.COLOR_BGR2GRAY)

    thresh = 100

    # get threshold image
    _, thresh_img = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)
#    thresh_img = cv2.Canny(gray_image, thresh, thresh * 2)

    # find the contours
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # create an empty image for contours
    img_contours = np.uint8(np.zeros((image.shape[0], image.shape[1])))

    # draw contour
    img_contours = cv2.drawContours(img_contours, contours, -1, (255, 255, 255), 2)

    return img_contours


def img2countoursCanny(image):
    # https://amroamroamro.github.io/mexopencv/opencv/hough_lines_demo.html
#    image = cv2.medianBlur(image, 7)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
#   edges = cv2.Canny(gray_image, 127, 127 * 2)

    return edges


def img2segments(image):
    # http://amroamroamro.github.io/mexopencv/opencv/lsd_lines_demo.html
    # image = cv2.medianBlur(image, 7)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_NONE)
    lines = lsd.detect(gray_image)[0]
    # TODO: Compare by lsd1.compareSegments([w,h], lines1, lines2)

    height, width, _ = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    pencil_sketch_IMG = lsd.drawSegments(img, lines)

    return pencil_sketch_IMG
