import cv2
import numpy as np


def img2blur(image, ksize=3):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred_img = cv2.GaussianBlur(image, (ksize, ksize), 0)
#    blurred_img = cv2.medianBlur(image, ksize)

    return blurred_img


def img2clahe(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img = cv2.equalizeHist(image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)

    return img


def img2threshold(image, thresh=128):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if thresh == -1:
        _, img = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    else:
        _, img = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)

    return img


def img2adaptive(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 10)
#    img = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)
#    img = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
#    img = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return img


def img2laplacian(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = cv2.GaussianBlur(image, (3, 3), 0)
    # Filter the image using filter2D, which has inputs: (grayscale image, bit-depth, kernel)
    filtered_image = cv2.Laplacian(image, ksize=3, ddepth=cv2.CV_16S)
    # converting back to uint8
    filtered_image = cv2.convertScaleAbs(filtered_image)

    return filtered_image


def img2sobel(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sobel_x_image = cv2.Sobel(image, cv2.CV_16SC1, 1, 0, ksize=3)
    sobel_y_image = cv2.Sobel(image, cv2.CV_16SC1, 0, 1, ksize=3)
    sobel_img = sobel_x_image + sobel_y_image
    sobel_img = cv2.convertScaleAbs(sobel_img)

    return sobel_img


def img2sobelX(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sobel_x_image = cv2.Sobel(image, cv2.CV_8U, 1, 0, ksize=3)
    sobel_img = cv2.convertScaleAbs(sobel_x_image)

    return sobel_img


def img2sketch(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred_img = cv2.GaussianBlur(image, (21, 21), 0)
    sketch_image = cv2.divide(image, blurred_img, scale=256)

    return sketch_image


def squaring(image):
    h, w = image.shape[:2]
    if w > h:
        offset = (w - h) // 2
        image = image[0:h, offset:(w - offset)]
    else:
        offset = (h - w) // 2
        image = image[offset:(h - offset), 0:w]

    return image


def img2pencilSketch(image):
    bw_sketch, _ = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.3, shade_factor=0.1)
    return bw_sketch


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

    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


def img2segments(image):
    # http://amroamroamro.github.io/mexopencv/opencv/lsd_lines_demo.html
    # image = cv2.medianBlur(image, 7)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_NONE)
    lines = lsd.detect(image)[0]
    # TODO: Compare by lsd1.compareSegments([w,h], lines1, lines2)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    segmented_image = lsd.drawSegments(img, lines)

    return segmented_image


def img2fastFeatures(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    fast = cv2.FastFeatureDetector_create(1400)
    # fast.setNonmaxSuppression(0)
    kp1 = fast.detect(image, None)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    img2 = cv2.drawKeypoints(img, kp1, None, color=(255, 0, 0))

    return img2


def img2goodFeatures(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # GFTTDetector
    corners = cv2.goodFeaturesToTrack(image, 200, 0.01, 10)
    # corners = cv2.goodFeaturesToTrack(gray_image, maxCorners=50, qualityLevel=0.02, minDistance=20)
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
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = np.float32(image)

    # Applying the function
    dst = cv2.cornerHarris(image, blockSize=2, ksize=3, k=0.04)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    # dilate to mark the corners
    dst = cv2.dilate(dst, None)
    img[dst > 0.01 * dst.max()] = 0

    return img


def img2orientedBRIEF(image, nfeatures=2000):
    # https://www.geeksforgeeks.org/feature-detection-and-matching-with-opencv-python/
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Applying the function
    orb = cv2.ORB_create(nfeatures=nfeatures)
    kp = orb.detect(image)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

    # Drawing the keypoints
    kp_image = cv2.drawKeypoints(img, kp, None, color=(0, 255, 0))

    return kp_image


def img2sift(image, nfeatures=2000):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Applying the function
    orb = cv2.SIFT_create(nfeatures=nfeatures)
    kp = orb.detect(image)

    height, width = image.shape
    img = np.zeros([height, width, 1], dtype=np.uint8)
    img.fill(255)

#    for kp in kp:
#        x, y = kp.pt
#        cv2.circle(img, (int(x), int(y)), 2, (0, 0, 0))

    # Drawing the keypoints
    kp_image = cv2.drawKeypoints(img, kp, None, color=(0, 255, 0))

    return kp_image
