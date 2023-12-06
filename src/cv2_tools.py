import cv2
import numpy as np
import imutils


def img2sketch(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_image, (21, 21), 0)
    pencil_sketch_IMG = cv2.divide(gray_image, blurred_img, scale=256)

    return pencil_sketch_IMG


def img2pencilSketch(image):
    mask, _ = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.3, shade_factor=0.1)
    return mask


def img2countours(image):
    # https://habr.com/ru/articles/676838/
    filterd_image = cv2.medianBlur(image, 7)
    gray_image = cv2.cvtColor(filterd_image, cv2.COLOR_BGR2GRAY)

    thresh = 100

    # get threshold image
    _, thresh_img = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)

    # find the contours
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # create an empty image for contours
    img_contours = np.uint8(np.zeros((image.shape[0], image.shape[1])))

    # draw contour
    img_contours = cv2.drawContours(img_contours, contours, -1, (255, 255, 255), 2)

    return img_contours


def img2canny(image):
    # https://github.com/PyImageSearch/imutils/tree/master#automatic-canny-edge-detection
    sigma = 0.33

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # compute the median of the single channel pixel intensities
    v = np.median(gray)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


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


def img2fastFeatures(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fast = cv2.FastFeatureDetector_create(1400)
    # fast.setNonmaxSuppression(0)
    kp1 = fast.detect(image, None)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)
    img2 = cv2.drawKeypoints(img, kp1, img, color=(255, 0, 0))

    return img2


def img2goodFeatures(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # GFTTDetector
    corners = cv2.goodFeaturesToTrack(image, 200, 0.01, 10)
    # corners = cv2.goodFeaturesToTrack(image, maxCorners=50, qualityLevel=0.02, minDistance=20)
    corners = np.int0(corners)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    for i in corners:
        x, y = i.ravel()
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

    return img


def img2cornerHarris(image):
    # https://www.geeksforgeeks.org/feature-detection-and-matching-with-opencv-python/
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray_image = np.float32(gray_image)

    # Applying the function
    dst = cv2.cornerHarris(gray_image, blockSize=2, ksize=3, k=0.04)

    height, width, _ = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    # dilate to mark the corners
    dst = cv2.dilate(dst, None)
    img[dst > 0.01 * dst.max()] = 0

    return img


def img2orientedBRIEF(image):
    # https://www.geeksforgeeks.org/feature-detection-and-matching-with-opencv-python/
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Applying the function
    orb = cv2.ORB_create(nfeatures=2000)
    kp = orb.detect(gray_image)

    height, width, _ = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    # Drawing the keypoints
    kp_image = cv2.drawKeypoints(img, kp, None, color=(0, 255, 0), flags=0)

    return kp_image


def img2sift(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Applying the function
    orb = cv2.SIFT_create(nfeatures=2000)
    kp = orb.detect(gray_image)

    height, width, _ = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

#    for kp in kp:
#        x, y = kp.pt
#        cv2.circle(img, (int(x), int(y)), 2, (0, 0, 0))

    # Drawing the keypoints
    kp_image = cv2.drawKeypoints(img, kp, None, color=(0, 255, 0), flags=0)

    return kp_image
