import argparse
import cv2
import sys
import math
import numpy as np
import time  # time.time() to get time
import threading
from robot.drive import *

# read image in japanese direcotry
def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

class TempTracker:
    """
    input: image and descriptor

    """

    def __init__(self, image_width, image_height, temp, descriptor='ORB'):

        # switch detector and matcher
        self.detector = self.get_des(descriptor)
        self.bf = self.get_matcher(descriptor)  # self matcher

        if self.detector == 0:
            print("Unknown Descriptor! \n")
            sys.exit()

        if len(temp.shape) > 2:  # if color then convert BGR to GRAY
            temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)

        self.template = temp
        #self.imsize = np.shape(self.template)
        self.kp1, self.des1 = self.detector.detectAndCompute(
            self.template, None)
        self.kpb, self.desb = self.kp1, self.des1
        self.scalebuf = []
        self.scale = 0
        self.H = np.eye(3, dtype=np.float32)
        self.dH1 = np.eye(3, dtype=np.float32)
        self.dH2 = np.eye(3, dtype=np.float32)
        self.matches = []
        self.inliers = []
        self.good = []  # good matches

        self.loc_array = []
        self.image_width = image_width
        self.image_height = image_height
        self.found = False

    def get_des(self, name):
        return {
            'ORB': cv2.ORB_create(nfeatures=1000, scoreType=cv2.ORB_HARRIS_SCORE),
            'AKAZE': cv2.AKAZE_create(),
            'KAZE': cv2.KAZE_create(),
            'SIFT': cv2.xfeatures2d.SIFT_create(),
        }.get(name, 0)

    def get_matcher(self, name):  # Binary feature or not
        return {
            'ORB': cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False),
            'AKAZE': cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False),
            'KAZE': cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False),
            'SIFT': cv2.BFMatcher(),
        }.get(name, 0)

    def get_goodmatches(self, img):
        """
        input: image to compare with template
        output: matched features in each images and the number of matched features
        """
        if len(img.shape) > 2:  # if color then convert BGR to GRAY
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        self.kp2, self.des2 = self.detector.detectAndCompute(img, None)

        # if feature number is not enough then skip
        if len(self.kp2) < 5:
            return [], [], 0

        matches = self.bf.knnMatch(self.des1, self.des2, k=2)
        self.good = []
        pts1 = []
        pts2 = []

        count = 0
        for m, n in matches:
            if m.distance < 0.5*n.distance:
                self.good.append([m])
                pts2.append(self.kp2[m.trainIdx].pt)
                pts1.append(self.kp1[m.queryIdx].pt)
                count += 1

        pts1 = np.float32(pts1)
        pts2 = np.float32(pts2)
        return pts1, pts2, count

    def track(self, img):
        pts1, pts2, count = self.get_goodmatches(img)

        self.show = img
        self.matches.append(count)

        # homography extraction
        if count > 4:
            self.H, self.mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 3.0)
            if self.check_mask():
                self.found = True
                self.get_rect()
                drive(self)
        else:
            self.found = False

        cv2.imshow("detected", self.show)

    def get_pts(self):
        x1 = self.loc_array[0].tolist()[0][0]
        x2 = self.loc_array[2].tolist()[0][0]
        obj_width = x2 - x1
        return [x1, obj_width]

    def get_rect(self):
        h, w = self.template.shape
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1],
                          [w-1, 0]]).reshape(-1, 1, 2)
        self.rect = cv2.perspectiveTransform(pts, self.H)
        self.loc_array = np.int32(self.rect)
        # draw lines
        self.show = cv2.polylines(
            self.show, [np.int32(self.rect)], True, 255, 3, cv2.LINE_AA)

    def check_mask(self):
        self.inliner = np.count_nonzero(self.mask)
        #print("inliner : "+str(self.inliner)+" in "+str(len(self.mask)))
        #self.total = self.mask.size
        if self.inliner > len(self.mask)*0.4:
            return 1
        else:
            return 0

    def refresh(self, img):
        self.track(img)
        self.kpb, self.desb = self.kp1, self.des1

# main function for parser
def load_args():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '-f', '--file', help='input video file or video port', default=0)
    parser.add_argument('-t', '--template',
                        help='template filename', default="object.png")
    parser.add_argument('-d', '--descriptor',
                        help='feature descripter', default="ORB")

    args = parser.parse_args()

    # catch the input like "1"
    vfile = int(args.file) if args.file.isdigit() else args.file

    return vfile, args.template, args.descriptor


# Main Function
def start_sift_tracking():
    vfile, template, DES = [0, 'images/babyyoda.jpeg', 'SIFT']
    print(vfile)
    print("Using "+DES+" Detector! \n")

    # video reader
    video = cv2.VideoCapture(vfile)
    image_width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    image_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video!")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print("Cannot read video file")
        sys.exit()

    # read template: enable to read files with 2bytes chalactors
    temp = imread(template)
    #exit("can not open template!") if temp is None else cv2.imshow("template", temp)

    tracker = TempTracker(image_width, image_height, temp, DES)

    count = 0

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Tracking Object
        t1 = time.time()
        tracker.track(frame)
        t2 = time.time()
        print(t2-t1)
        count += 1
        print(count)
        if count >= 10 or tracker.found:
            drive(tracker)
            count = 0
        # T.check()

        # Exit if "Q" pressed
        k = cv2.waitKey(1) & 0xff
        if k == ord('q'):
            GPIO.cleanup()
            break
        if k == ord('s'):
            cv2.imwrite('result.png', tracker.show)
            break
        if k == ord('r'):
            tracker.refresh(frame)
