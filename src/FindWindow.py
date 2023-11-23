import cv2
import io
import time
import numpy as np
from PIL import Image
from datetime import datetime
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from FindDialog import FindDialog, ComparisonResult, TableWidget, CardDelegate
from ImageLabel import ImageEdit
from Tools import Gui

CardDelegate.LABEL_HEIGHT = 18 + 4


class Model():
    fields = []
    settings = {'image_height': 1.5}

    def __init__(self):
        self.folder = None
        self.scan_subfolders = False

    def getPhotoCount(self):
        count = 0
        for _ in self.scan():
            count += 1

        return count

    def scan(self):
        if self.folder:
            filters = ["*.jpg", "*.jpeg", "*.bmp", "*.png", "*.tif", "*.tiff", "*.gif"]
            supported_formats = QImageReader.supportedImageFormats()
            if b'webp' in supported_formats:
                filters.append("*.webp")
            if b'jp2' in supported_formats:
                filters.append("*.jp2")

            if self.scan_subfolders:
                flags = QDirIterator.Subdirectories
            else:
                flags = QDirIterator.NoIteratorFlags
            it = QDirIterator(self.folder, filters, QDir.Files, flags)
            while it.hasNext():
                it.next()
                yield it.fileName(), it.filePath()


class FindWindow(FindDialog):

    def __init__(self, parent=None):
        model = Model()

        super().__init__(model, parent)

        settings = QSettings()

        folder = settings.value('image_find/folder')
        self.folderEdit = QLineEdit(folder, self)
        self.folderEdit.setMinimumWidth(120)
        icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)
        folderButton = QPushButton(icon, '', self)
        folderButton.clicked.connect(self.folderButtonClicked)
        folderLabel = QLabel(self.tr("Find in folder"), self)

        hLayout = QHBoxLayout()
        hLayout.addWidget(folderLabel)
        hLayout.addWidget(self.folderEdit)
        hLayout.addWidget(folderButton)

        self.layout().insertLayout(0, hLayout)

        scan_subfolders = settings.value('image_find/scan_subfolders', False, type=bool)
        self.scanSubfolders = QCheckBox(self.tr("Scan subfolders"), self)
        if scan_subfolders:
            self.scanSubfolders.setCheckState(Qt.Checked)

        self.layout().insertWidget(1, self.scanSubfolders)

        sizes = settings.value('image_find/splitter')
        if sizes:
            for i, size in enumerate(sizes):
                sizes[i] = int(size)

            self.splitter.setSizes(sizes)

        latest_img_folder = settings.value('image_find/src_folder')
        if latest_img_folder:
            ImageEdit.latestDir = latest_img_folder

    def folderButtonClicked(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Find in folder"), self.folderEdit.text())
        if folder:
            self.folderEdit.setText(folder)

        self.updateFindButton()

    def imageChanged(self, _):
        self.updateFindButton()

    def updateFindButton(self):
        is_image_selected = bool(self.targetImgLabel.data())
        is_folder_selected = bool(self.folderEdit.text())
        self.findButton.setEnabled(is_image_selected and is_folder_selected)

    def saveSettings(self):
        super().saveSettings()

        settings = QSettings()

        folder = self.folderEdit.text()
        settings.setValue('image_find/folder', folder)

        scan_subfolders = (self.scanSubfolders.checkState() == Qt.Checked)
        settings.setValue('image_find/scan_subfolders', scan_subfolders)

        settings.setValue('image_find/src_folder', ImageEdit.latestDir)

    def done(self, r):
        super().done(r)

        settings = QSettings()
        settings.setValue('image_find/splitter', self.splitter.sizes())

    def start(self):
        start_processing_time = time.process_time()

        self.saveSettings()

        folder = self.folderEdit.text()
        self.model.folder = folder
        scan_subfolders = (self.scanSubfolders.checkState() == Qt.Checked)
        self.model.scan_subfolders = scan_subfolders

        img = self.targetImgLabel.data()
        if isinstance(img, QImage):
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            img.save(buffer, 'png')
            target_data = buffer.data()
        else:
            target_data = img

        method = self.methodSelector.currentData()
        if method in ('ahash_cv', 'blockhash', 'colorhash_cv',
                      'mhhash', 'phash_cv', 'radialhash'):
            interpolation = cv2.INTER_AREA
            if method == 'ahash_cv':
                size = (8, 8)
            elif method == 'blockhash':
                size = (256, 256)
            elif method == 'phash_cv':
                size = (32, 32)
            else:
                size = None

            image = np.asarray(bytearray(target_data), dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            if size:
                image = cv2.resize(image, size, interpolation=interpolation)
            target_hash = self._imageHash(image, method)
        else:
            pil_target_img = Image.open(io.BytesIO(target_data))
            target_hash = self._imageHash(pil_target_img, method)

        fields = []
        for field, check_box in self.fieldsCheckBox.items():
            if check_box.isChecked():
                fields.append(field)

        # Get count of coins with photos
        row_count = self.model.getPhotoCount()

        progressDlg = Gui.ProgressDialog(
                    self.tr("Processing..."),
                    self.tr("Cancel"), row_count,
                    self)

        comparison_results = []

        start_hashing_time = time.process_time()
        for fileName, filePath in self.model.scan():
            progressDlg.step()
            if progressDlg.wasCanceled():
                break

            if method in ('ahash_cv', 'blockhash', 'colorhash_cv',
                          'mhhash', 'phash_cv', 'radialhash'):

                image = cv2.imdecode(np.fromfile(filePath, dtype=np.uint8), cv2.IMREAD_COLOR)
                if size:
                    image = cv2.resize(image, size, interpolation=interpolation)
                hash_ = self._imageHash(image, method)
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
                record_distance = hsh.compare(target_hash, hash_)
                if method == 'radialhash':
                    record_distance = 1. - record_distance
            else:
                pil_img = Image.open(filePath)
                hash_ = self._imageHash(pil_img, method)
                record_distance = target_hash - hash_

            if method in ('crop_resistant_hash', 'radialhash'):
                record_distance_str = f"{record_distance:.2f}"
            else:
                record_distance_str = f"{int(record_distance)}"
            comparison_results.append(ComparisonResult(
                0,
                f"{fileName} [{record_distance_str}]",
                filePath,
                record_distance
            ))
        done_hashing_time = time.process_time()

        progressDlg.reset()

        comparison_results = sorted(comparison_results, key=lambda x: x.distance)

        self.table = TableWidget(self, self)
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self._updateTableSizes()

        old_widget = self.splitter.replaceWidget(1, self.table)
        old_widget.deleteLater()

        similarity = self.similaritySlider.value()
        max_val = 64
        if method == 'crop_resistant_hash':
            max_val = 5
        elif method == 'blockhash':
            max_val = 256
        elif method == 'colorhash_cv':
            max_val = 256
        elif method == 'bhash':
            max_val = 256
        elif method == 'mhhash':
            max_val = 576
        elif method == 'radialhash':
            max_val = 1
        max_distance = max_val * (100 - similarity) / 100

        for comp_res in comparison_results:
            if comp_res.distance > max_distance:
                break

            item = QTableWidgetItem()
            item.setData(Qt.UserRole, comp_res)
            self.table.addItem(item)

        self.table.update()

        done_processing_time = time.process_time()
        print(f"Hashing time: {done_hashing_time - start_hashing_time:.2f}",
              f"({(done_hashing_time - start_hashing_time)*100/row_count:.2f}ms per 100).",
              f"Total time: {done_processing_time - start_processing_time:.2f}")

    def _getImageData(self, photo_id):
        with open(photo_id, "rb") as file:
            data = file.read()

        return data
