[![GitHub release](https://img.shields.io/github/release/opennumismat/SimilarImageFinder.svg)](https://github.com/opennumismat/SimilarImageFinder/releases/)
[![GitHub release (latest by date)](https://img.shields.io/github/downloads/opennumismat/SimilarImageFinder/latest/total.svg)](https://hanadigital.github.io/grev/?user=OpenNumismat&repo=SimilarImageFinder)
[![GitHub all releases](https://img.shields.io/github/downloads/opennumismat/SimilarImageFinder/total.svg)](https://hanadigital.github.io/grev/?user=OpenNumismat&repo=SimilarImageFinder)
[![GitHub license](https://img.shields.io/github/license/opennumismat/SimilarImageFinder.svg)](https://github.com/opennumismat/SimilarImageFinder/blob/master/LICENSE)

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

For hash calcualtion uses labraries [ImageHash](https://github.com/JohannesBuchner/imagehash), [OpenCV](https://github.com/opencv/opencv-python) and [blockhash-python](https://github.com/commonsmachinery/blockhash-python).

SimilarImageFinder is a part of [OpenNumismat](http://opennumismat.github.io/) project, so it aims to finding coins images.

![Screenshot](https://opennumismat.github.io/images/imageFinder.png)

#### Download
[Latest version for Windows 10 and later](https://github.com/OpenNumismat/SimilarImageFinder/releases/latest)

#### For run from source code
    pip3 install -r requirements.txt
    python3 src/run.py
