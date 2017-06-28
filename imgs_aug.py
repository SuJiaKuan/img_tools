import cv2
import os
import sys

from imgaug import augmenters as iaa

# Store text to a file
def store_txt(file_path, txt):
    txt_file = open(file_path, 'w')
    txt_file.write(txt)
    txt_file.close()

# Store result images and groud truth
def store_result(output_dir, output_target_image, output_search_image, output_target_gt, output_search_gt):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cv2.imwrite(output_dir + '/target.jpg', output_target_image)
    cv2.imwrite(output_dir + '/search.jpg', output_search_image)
    store_txt(output_dir + '/target_gt.txt', output_target_gt)
    store_txt(output_dir + '/search_gt.txt', output_search_gt)

if len(sys.argv) < 2:
    print('Usage: Python ' + sys.argv[0] + ' folder')
    sys.exit(-1)

# Augment images by illumination variation.
# TODO: Support more augumentation instructions.
aug_iv = True

# Sequence of image augmentation instructions.
# Only support darking and brightening (for illumination variation) currently.
darken_seq = iaa.Sequential([
    iaa.Multiply(0.3)
])
brighten_seq = iaa.Sequential([
    iaa.Multiply(1.5)
])

# Find all subdirectories and sort by directory name.
root_dir = sys.argv[1]
dirs = os.listdir(root_dir)
dirs.sort()

# Augment all images.
for dir_path in dirs:
    # Get input images and groud truth.
    input_dir = root_dir + '/' + dir_path
    input_target_img = cv2.imread(input_dir + '/target.jpg')
    input_search_img = cv2.imread(input_dir + '/search.jpg')
    target_gt = open(input_dir + '/target_gt.txt').read()
    search_gt = open(input_dir + '/search_gt.txt').read()

    if aug_iv:
        # Darken and lighten the images.
        darken_target_img = darken_seq.augment_image(input_target_img)
        darken_search_img = darken_seq.augment_image(input_search_img)
        brighten_target_img = brighten_seq.augment_image(input_target_img)
        brighten_search_img = brighten_seq.augment_image(input_search_img)

        # Store the images in different combinations.
        output_dir_prefix = root_dir + '+IV/' + dir_path
        store_result(output_dir_prefix + '_normal_to_dark', input_target_img, darken_search_img, target_gt, search_gt)
        store_result(output_dir_prefix + '_normal_to_bright', input_target_img, brighten_search_img, target_gt, search_gt)
        store_result(output_dir_prefix + '_dark_to_normal', darken_target_img, input_search_img, target_gt, search_gt)
        store_result(output_dir_prefix + '_dark_to_bright', darken_target_img, brighten_search_img, target_gt, search_gt)
        store_result(output_dir_prefix + '_bright_to_normal', brighten_target_img, input_search_img, target_gt, search_gt)
        store_result(output_dir_prefix + '_bright_to_dark', brighten_target_img, darken_search_img, target_gt, search_gt)
