import argparse
import os
import time
from PIL import Image
import blockhash.core
import cv2
import imagehash
import numpy as np
from PySide6.QtCore import *
try:
    import pdqhash
    PDQHASH_AVAILABLE = True
except ModuleNotFoundError:
    PDQHASH_AVAILABLE = False

from cv2_tools import *


def file2img(file_name):
    return cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), cv2.IMREAD_COLOR)


def img2pil(image):
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def squaring(image):
    h, w = image.shape[:2]
    if w > h:
        offset = (w - h) // 2
        image = image[0:h, offset:(w - offset)]
    else:
        offset = (h - w) // 2
        image = image[offset:(h - offset), 0:w]

    return image


def resizing(image, side_len=512, interpolation=cv2.INTER_AREA):
    return cv2.resize(image, (side_len, side_len), interpolation=interpolation)


def calc_hash(image, method):
    if method == 'ahash':
        return imagehash.average_hash(img2pil(image))
    elif method == 'phash':
        return imagehash.phash(img2pil(image))
    elif method == 'dhash':
        return imagehash.dhash(img2pil(image))
    elif method == 'whash':
        return imagehash.whash(img2pil(image))
    elif method == 'colorhash':
        return imagehash.colorhash(img2pil(image))
    elif method == 'crop_resistant_hash':
        return imagehash.crop_resistant_hash(img2pil(image))
    elif method == 'ahash_cv':
        interpolation = cv2.INTER_AREA
        image = cv2.resize(image, (8, 8), interpolation=interpolation)
        hsh = cv2.img_hash.AverageHash_create()
        return hsh.compute(image)
    elif method == 'blockhash':
        interpolation = cv2.INTER_AREA
        image = cv2.resize(image, (255, 255), interpolation=interpolation)
        hsh = cv2.img_hash.BlockMeanHash_create()
        return hsh.compute(image)
    elif method == 'colorhash_cv':
        hsh = cv2.img_hash.ColorMomentHash_create()
        return hsh.compute(image)
    elif method == 'mhhash':
        hsh = cv2.img_hash.MarrHildrethHash_create()
        return hsh.compute(image)
    elif method == 'phash_cv':
        interpolation = cv2.INTER_AREA
        image = cv2.resize(image, (32, 32), interpolation=interpolation)
        hsh = cv2.img_hash.PHash_create()
        return hsh.compute(image)
    elif method == 'radialhash':
        hsh = cv2.img_hash.RadialVarianceHash_create()
        return hsh.compute(image)
    elif method == 'bhash':
        hash_ = blockhash.core.blockhash_even(img2pil(image))
        return imagehash.hex_to_hash(hash_)
    elif method == 'pdqhash':
        hash_, _ = pdqhash.compute(image)
        return imagehash.ImageHash(hash_)


def compare_hash(hash1, hash2, method):
    if method in ('ahash_cv', 'blockhash', 'colorhash_cv',
                  'mhhash', 'phash_cv', 'radialhash'):
        if method == 'ahash_cv':
            hsh = cv2.img_hash.AverageHash_create()
        elif method == 'blockhash':
            hsh = cv2.img_hash.BlockMeanHash_create()
        elif method == 'colorhash_cv':
            hsh = cv2.img_hash.ColorMomentHash_create()
        elif method == 'mhhash':
            hsh = cv2.img_hash.MarrHildrethHash_create()
        elif method == 'phash_cv':
            hsh = cv2.img_hash.PHash_create()
        elif method == 'radialhash':
            hsh = cv2.img_hash.RadialVarianceHash_create()

        distance = hsh.compare(hash1, hash2)

        if method == 'radialhash':
            distance = 1. - distance
    else:
        distance = hash1 - hash2

    return distance


def filtering(image, filters):
    for filter_ in filters.split('-'):
        if filter_ == 'sq':
            image = squaring(image)
        if filter_ == 'res':
            image = resizing(image)
        if filter_ == 'res512':
            image = resizing(image, 512)
        if filter_ == 'res256':
            image = resizing(image, 256)
        if filter_ == 'clahe':
            image = img2clahe(image)
        if filter_ == 'threshold':
            image = img2threshold(image)
        if filter_ == 'laplacian':
            image = img2laplacian(image)
        if filter_ == 'sobel':
            image = img2sobel(image)
        if filter_ == 'sobel_x':
            image = img2sobelX(image)
        if filter_ == 'sketch':
            image = img2sketch(image)
        if filter_ == 'pencil':
            image = img2pencilSketch(image)
        if filter_ == 'canny':
            image = img2canny(image)
        if filter_ == 'segments':
            image = img2segments(image)
        if filter_ == 'fast':
            image = img2fastFeatures(image)
        if filter_ == 'good':
            image = img2goodFeatures(image)
        if filter_ == 'corner':
            image = img2cornerHarris(image)
        if filter_ == 'orb':
            image = img2orientedBRIEF(image)
        if filter_ == 'sift':
            image = img2sift(image)

    return image


def scan(folder, except_files=[]):
    filters = ("*.jpg", "*.jpeg", "*.bmp", "*.png",
               "*.tif", "*.tiff", "*.gif", "*.webp")
    flags = QDirIterator.NoIteratorFlags

    it = QDirIterator(folder, filters, QDir.Files, flags)
    while it.hasNext():
        it.next()
        if it.filePath() not in except_files:
            yield it.fileName(), it.filePath()


def find_file(file_path, similar_files, folder, hash_method, filter_):
    start_time = time.process_time()

    comparison_results = []

    orig_file = file_path
    file_name = os.path.basename(file_path)

    image = file2img(orig_file)
    image = filtering(image, filter_)
    orig_hash = calc_hash(image, hash_method)

    target_folder = folder
    for fileName, filePath in scan(target_folder, [orig_file, ]):
        image = file2img(filePath)
        image = filtering(image, filter_)
        target_hash = calc_hash(image, hash_method)
        distance = compare_hash(orig_hash, target_hash, hash_method)

        comparison_results.append({'file': fileName, 'distance': distance})

    comparison_results = sorted(comparison_results, key=lambda x: x['distance'])

    done_time = time.process_time()

    result_count = 15
    last_distance = comparison_results[result_count - 1]['distance']
    for result_count in range(result_count, len(comparison_results)):
        if last_distance < comparison_results[result_count]['distance']:
            break

    result_str = ""
    results = []
    last_distance = 0
    for comparison_result in comparison_results[:result_count]:
        distance = comparison_result['distance']

        if distance != last_distance:
            if result_str:
                results.append(result_str)
                result_str = ""
            last_distance = distance

        if comparison_result['file'] in similar_files:
            result_str += "*"
        else:
            result_str += "-"
    results.append(result_str)

    similarity_points = 0
    point = 1
    for result_str in results:
        if '-' in result_str:
            fail_point = 0.17
            fail_point *= result_str.count('-') / len(result_str)
            point -= fail_point
            if point < 0:
                break
        similarity_points += point * result_str.count('*')

    hits_str = ''.join(results)
    hits_str_2 = '/'.join(results)
    hits = hits_str.count('*')
    comparison_count = len(comparison_results)

    print(f"{file_name}, {hash_method}, {filter_}, {hits}, {similarity_points:.2f}, {done_time - start_time:.2f}, {(done_time - start_time)*100/comparison_count:.2f}, {hits_str}, {hits_str_2}")

    return similarity_points


def compare_file(file_path, similar_files, folder, methods, filters=[]):
    if not filters:
        filters = ['', ]

    for filter_ in filters:
        for method in methods:
            find_file(file_path, similar_files, folder, method, filter_)


def compare_files(similar_files, folder, methods, filters=[]):
    for file_name in similar_files:
        file_path = os.path.join(folder, file_name)
        compare_file(file_path, similar_files, folder, methods, filters)


def print_header():
    print("file_name, hash, preprocess, hits, similarity_points, total_duration, ms per 100, hits_string, hits_string_2")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog='SimilarImageFinder CLI',
        epilog='Usage examples:\n'
        ' cli.py --similar_files "01.jpg" "02.jpg" --folder C:/SimilarImageFinder/ --hash phash --preprocess corner sq-rev-sketch\n'
        ' cli.py --similar_files "01.jpg" "02.jpg" --file C:/similar_image.jpg --folder C:/SimilarImageFinder/ --hash phash'
    )
    parser.add_argument(
        "--file",
        help="File for search"
    )
    parser.add_argument(
        "--similar_files", required=True, nargs='+',
        help="Group of similar image files in FOLDER"
    )
    parser.add_argument(
        "--folder", required=True,
        help="Folder for scan similarity images"
    )
    parser.add_argument(
        "--hash", nargs='+', required=True,
        choices=(
            'ahash', 'phash', 'dhash', 'whash', 'ahash_cv', 'blockhash',
            'mhhash', 'phash_cv', 'radialhash', 'pdqhash',
            'crop_resistant_hash', 'bhash', 'colorhash', 'colorhash_cv'
        ),
        help="Hash method"
    )
    parser.add_argument(
        "--filter", nargs='+',
        help="List of preprocessing filters. Can be any combination of none,sq,res,res512,res256,clahe,threshold,laplacian,sobel,sobel_x,filter2D,sketch,pencil,canny,segments,fast,good,corner,orb,sift joined with '-'"
    )

    args = parser.parse_args()

    print_header()

    if args.file:
        compare_file(args.file, args.similar_files, args.folder, args.hash, args.filters)
    else:
        compare_files(args.similar_files, args.folder, args.hash, args.filters)


if __name__ == "__main__":
    main()
