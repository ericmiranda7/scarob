import argparse
import cv2
import sys
import math
import numpy as np
import time  # time.time() to get time

#from robot.motor import *

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

    def __init__(self, temp, descriptor='ORB'):

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
        self.findHomography = False  # homography estimated flag
        self.scalebuf = []
        self.scale = 0
        self.H = np.eye(3, dtype=np.float32)
        self.dH1 = np.eye(3, dtype=np.float32)
        self.dH2 = np.eye(3, dtype=np.float32)
        self.matches = []
        self.inliers = []
        self.good = []  # good matches

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

    def draw_matches(self, img):
        _, _, count = self.get_goodmatches(img)

        if count:
            matched_images = cv2.drawMatchesKnn(
                self.template, self.kp1, img, self.kp2, self.good, None, flags=2)
            cv2.imshow("matched", matched_images)

        cv2.imshow("current", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

    def track(self, img):
        pts1, pts2, count = self.get_goodmatches(img)

        self.findHomography = False
        self.show = img
        self.matches.append(count)

        # homography extraction
        if count > 4:
            self.H, self.mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 3.0)
            if self.check_mask():
                self.get_rect()
                self.get_scale()
                self.findHomography = True

        if self.findHomography:
            self.scalebuf.append(self.scale)
            self.inliers.append(self.inliner)
        else:
            self.scalebuf.append(0)
            self.inliers.append(0)

        cv2.imshow("detected", self.show)

    def get_pts(self, loc_array):
        x1 = loc_array[0].tolist()[0][0]
        x2 = loc_array[2].tolist()[0][0]
        obj_width = x2 - x1
        return [x1, obj_width]

    def get_rect(self):
        global loc_array
        h, w = self.template.shape
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1],
                          [w-1, 0]]).reshape(-1, 1, 2)
        self.rect = cv2.perspectiveTransform(pts, self.H)
        loc_array = np.int32(self.rect)
        self.drive()
        # draw lines
        self.show = cv2.polylines(
            self.show, [np.int32(self.rect)], True, 255, 3, cv2.LINE_AA)

    def drive(self):
        [x, obj_width] = self.get_pts(loc_array)
        object_x = x + (obj_width / 2)
        center_image_x = image_width / 2

        if object_x > (center_image_x + (image_width / 5)):
            print("right")
            right(turn_speed)
        elif object_x < (center_image_x - (image_width / 5)):
            print("left")
            left(turn_speed)
        else:
            print("forward")
            forward(forward_speed)
            time.sleep(0.2)

    def check_mask(self):
        self.inliner = np.count_nonzero(self.mask)
        #print("inliner : "+str(self.inliner)+" in "+str(len(self.mask)))
        #self.total = self.mask.size
        if self.inliner > len(self.mask)*0.4:
            return 1
        else:
            return 0

    def get_scale(self):
        sq = self.H[0:1, 0:1]*self.H[0:1, 0:1]
        self.scale = math.sqrt(sq.sum()/2)

    def show_scale(self):
        pass

    def refresh(self, img):
        self.track(img)
        self.kpb, self.desb = self.kp1, self.des1

# Minor change


class ContinuousTempTracker(TempTracker):
    """
    Update template when get good matchings
    """

    def ctrack(self, img):
        if len(img.shape) > 2:  # if color then convert BGR to GRAY
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # print(len(self.kp1))
        kp2, des2 = self.detector.detectAndCompute(img, None)
        if len(kp2) < 5:
            return

        # match with buff image
        matches = self.bf.knnMatch(self.desb, des2, k=2)
        good = []
        pts1 = []
        pts2 = []
        gdes2 = []
        count = 0
        for m, n in matches:
            if m.distance < 0.6*n.distance:
                good.append(kp2[m.trainIdx])
                pts2.append(kp2[m.trainIdx].pt)
                gdes2.append(des2[m.trainIdx])
                pts1.append(self.kpb[m.queryIdx].pt)
                count += 1
        pts1_ = np.float32(pts1)
        pts2_ = np.float32(pts2)
        gdes2 = np.array(gdes2)

        self.matches.append(count)
        self.findHomography = False
        self.show = img

        if count > 4:
            self.dH2, self.mask = cv2.findHomography(
                pts1_, pts2_, cv2.RANSAC, 3.0)
            if self.check_mask():
                self.H = np.dot(self.dH2, self.H)
                self.dH = np.dot(self.dH2, self.dH1)
                self.get_rect()
                self.get_scale()
                self.findHomography = True
                self.getnewtemp(img)
        if self.findHomography:
            self.scalebuf.append(self.scale)
            self.inliers.append(self.inliner)
        else:
            self.scalebuf.append(0)
            self.inliers.append(0)

        cv2.imshow("detected", self.show)

    def getnewtemp(self, img):
        hei, wid = self.show.shape
        ymin = max(math.floor(self.rect[:, 0, 1].min()), 0)
        ymax = min(math.floor(self.rect[:, 0, 1].max()), hei-1)
        xmin = max(math.floor(self.rect[:, 0, 0].min()), 0)
        xmax = min(math.floor(self.rect[:, 0, 0].max()), wid-1)
        temp = img[ymin:ymax, xmin:xmax]
        self.dH1 = np.eye(3, dtype=np.float32)
        self.dH1[0, 2] = -xmin
        self.dH1[1, 2] = -ymin
        self.H = np.dot(self.dH1, self.H)
        self.kpb, self.desb = self.detector.detectAndCompute(temp, None)
        cv2.imshow("template", temp)


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
if __name__ == '__main__':
    global image_width
    global image_height
    global gui

    print("Opencv Version is...")
    print(cv2.__version__)

    vfile, template, DES = load_args()
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

    tracker = TempTracker(temp, DES)

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Tracking Object
        tracker.track(frame)
        # T.check()

        # Exit if "Q" pressed
        k = cv2.waitKey(1) & 0xff
        if k == ord('q'):
            break
        if k == ord('s'):
            cv2.imwrite('result.png', tracker.show)
            break
        if k == ord('r'):
            tracker.refresh(frame)
