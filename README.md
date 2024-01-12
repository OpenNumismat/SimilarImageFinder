[![GitHub release](https://img.shields.io/github/release/opennumismat/SimilarImageFinder.svg)](https://github.com/opennumismat/SimilarImageFinder/releases/)
[![GitHub release (latest by date)](https://img.shields.io/github/downloads/opennumismat/SimilarImageFinder/latest/total.svg)](https://hanadigital.github.io/grev/?user=OpenNumismat&repo=SimilarImageFinder)
[![GitHub all releases](https://img.shields.io/github/downloads/opennumismat/SimilarImageFinder/total.svg)](https://hanadigital.github.io/grev/?user=OpenNumismat&repo=SimilarImageFinder)
[![GitHub license](https://img.shields.io/github/license/opennumismat/SimilarImageFinder.svg)](https://github.com/opennumismat/SimilarImageFinder/blob/master/LICENSE)
[![Latest build](https://github.com/OpenNumismat/SimilarImageFinder/actions/workflows/snapshot.yml/badge.svg)](https://github.com/OpenNumismat/SimilarImageFinder/releases/tag/latest)

# SimilarImageFinder

This application is designed to test algorithms for finding similar images using perceptual hashes.
The following hash types are currently supported:
* Average hashing
* Perceptual hashing
* Difference hashing
* Wavelet hashing
* HSV color hashing
* Crop-resistant hashing
* Marr-Hildreth hashing
* Radial variance hashing
* Block mean hashing
* Color moment hashing
* PDQ hashing

For hash calcualtion uses labraries [ImageHash](https://github.com/JohannesBuchner/imagehash), [OpenCV](https://github.com/opencv/opencv-python), [pdqhash](https://github.com/faustomorales/pdqhash-python) and [blockhash](https://github.com/commonsmachinery/blockhash-python).

SimilarImageFinder is a part of [OpenNumismat](http://opennumismat.github.io/) project, so it aims to finding coins images.

![Screenshot](https://opennumismat.github.io/images/imageFinder.png)

#### Download
[Latest version for Windows 10 and later](https://github.com/OpenNumismat/SimilarImageFinder/releases/latest)

#### Usage
    python3 src/cli.py [-h] [--file FILE] --similar_files SIMILAR_FILES [SIMILAR_FILES ...] --folder FOLDER
                       --hash
                       {ahash,phash,dhash,whash,ahash_cv,blockhash,mhhash,phash_cv,radialhash,pdqhash,crop_resistant_hash,bhash,colorhash,colorhash_cv}
                       [{ahash,phash,dhash,whash,ahash_cv,blockhash,mhhash,phash_cv,radialhash,pdqhash,crop_resistant_hash,bhash,colorhash,colorhash_cv} ...]
                       [--filter FILTER [FILTER ...]]

    options:
      -h, --help        show this help message and exit
      --file FILE       File for search
      --similar_files SIMILAR_FILES [SIMILAR_FILES ...]
                        Group of similar image files in FOLDER
      --folder FOLDER   Folder for scan similarity images
      --hash {ahash,phash,dhash,whash,ahash_cv,blockhash,mhhash,phash_cv,radialhash,pdqhash,crop_resistant_hash,bhash,colorhash,colorhash_cv} [{ahash,phash,dhash,whash,ahash_cv,blockhash,mhhash,phash_cv,radialhash,pdqhash,crop_resistant_hash,bhash,colorhash,colorhash_cv} ...]
                        Hash method
      --filter FILTER [FILTER ...]
                        List of preprocessing filters. Can be any combination of none,sq,sq512,sq256,clahe,threshold,laplacian,sobel,sobel_x,filter2D,sketch,pencil,canny,segments,fast,good,corner,orb,sift joined with '-'

    Usage examples:
      cli.py --similar_files "01.jpg" "02.jpg" --folder C:/SimilarImageFinder/ --hash phash --preprocess corner sq-sketch
      cli.py --similar_files "01.jpg" "02.jpg" --file C:/similar_image.jpg --folder C:/SimilarImageFinder/ --hash phash pdqhash

#### For run from source code
    pip3 install -r requirements.txt
    python3 src/run.py
