import os
import sys
import cv2

class BoudingBox:
    # Init function
    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

    # Get reordered position of bouding box
    def __reorder(self):
        x1 = min(self.x1, self.x2)
        y1 = min(self.y1, self.y2)
        x2 = max(self.x1, self.x2)
        y2 = max(self.y1, self.y2)
        return x1, y1, x2, y2

    # Setter
    def set(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    # Draw bouding box on an image
    def draw(self, img, color):
        cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), color, 3)

    # Write bouding box to a file
    def write(self, file_path):
        file_bbox = open(file_path, 'w')
        x1, y1, x2, y2 = self.__reorder()
        file_bbox.write(str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2))
        file_bbox.close()

    # Convert the bouding box to text
    def toText(self):
        x1, y1, x2, y2 = self.__reorder()
        return '(' + str(x1) + ', ' + str(y1) + '), (' + str(x2) + ', ' + str(y2) + ')'

class Annotator:
    # Init function
    def __init__(self, img_path, gt_path):
        # The image path
        self.img_path = img_path

        # The path of file to store groud truth
        self.gt_path = gt_path

        # Read image
        self.img = cv2.imread(img_path)
        if self.img is None:
            print('The image ' + img_path + ' does not exist!')
            return

        # Read bouding box if it the ground truth file exists
        self.bbox = BoudingBox()
        if os.path.exists(gt_path):
            gt_file = open(gt_path, 'r')
            gt = gt_file.read().split(',')
            self.bbox.set(int(gt[0]), int(gt[1]), int(gt[2]), int(gt[3]))

        # State to indicate is drawing bounding box or not
        self.drawing = False

    # Mouse callback function
    def __set_bbox(self, event, x, y, flags, param):
        # Update state according the mouse event
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.bbox.set(x, y, x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.bbox.set(self.bbox.x1, self.bbox.y1, x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.bbox.set(self.bbox.x1, self.bbox.y1, x, y)
                self.bbox.write(self.gt_path)
                self.drawing = False

    def __draw_text(self, img, text, position):
        cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

    # Annotation function
    def annotate(self):
        # Set mouse callback function
        cv2.namedWindow('annotation')
        cv2.setMouseCallback('annotation', self.__set_bbox)

        # Draw and show image
        while True:
            # Draw bouding box and related information on a temporary image
            img_drawn = self.img.copy()
            self.bbox.draw(img_drawn, (0, 0, 255))
            self.__draw_text(img_drawn, self.img_path, (10, 30))
            self.__draw_text(img_drawn, self.bbox.toText(), (10, 70))
            self.__draw_text(img_drawn,  'Drawing' if self.drawing else 'Result Saved', (10, 110))
            self.__draw_text(img_drawn,  'Press "n" to continue' if not self.drawing else '', (10, 150))

            # Show the drawn image
            cv2.imshow('annotation', img_drawn)

            # Wait key
            key = cv2.waitKey(20) & 0xFF
            if (not self.drawing) and (key == ord('n')):
                break

if len(sys.argv) < 2:
    print('Usage: Python ' + sys.argv[0] + ' folder')
    sys.exit(-1)

# Find all subdirectories and sort by directory name
root_dir = sys.argv[1]
dirs = [x[0] for x in os.walk(root_dir)][1:]
dirs.sort()

# Annotate all images
for dir_path in dirs:
    Annotator(dir_path + '/target.jpg', dir_path + '/target_gt.txt').annotate()
    Annotator(dir_path + '/search.jpg', dir_path + '/search_gt.txt').annotate()
