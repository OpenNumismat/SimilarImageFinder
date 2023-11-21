import io
import os
from PIL import Image
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from FindDialog import FindDialog, ComparisonResult, TableWidget
from Tools import Gui


class Model():
    fields = []
    settings = {'image_height': 1.5}

    def __init__(self):
        self.folder = None

    def setFolder(self, folder):
        self.folder = folder

    def getPhotoCount(self):
        count = 0
        for _ in self.scan():
            count += 1

        return count

    def scan(self):
        if self.folder:
            formats = ["*.jpg", "*.jpeg", "*.bmp", "*.png", "*.tif", "*.tiff", "*.gif"]
            supported_formats = QImageReader.supportedImageFormats()
            if b'webp' in supported_formats:
                formats.append("*.webp")
            if b'jp2' in supported_formats:
                formats.append("*.jp2")

            dir_ = QDir(self.folder)
            for fileName in dir_.entryList(formats, QDir.AllEntries | QDir.NoDotAndDotDot, QDir.Name):
                yield fileName, dir_.filePath(fileName)


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

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.folderEdit)
        hLayout.addWidget(folderButton)

        self.layout().insertLayout(0, hLayout)

    def folderButtonClicked(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Source folder"), self.folderEdit.text())
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

    def start(self):
        self.saveSettings()

        folder = self.folderEdit.text()
        self.model.setFolder(folder)

        img = self.targetImgLabel.data()
        if isinstance(img, QImage):
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            img.save(buffer, 'png')
            target_data = buffer.data()
        else:
            target_data = img

        method = self.methodSelector.currentData()

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

        for fileName, filePath in self.model.scan():
            progressDlg.step()
            if progressDlg.wasCanceled():
                break

            pil_img = Image.open(filePath)
            hash_ = self._imageHash(pil_img, method)
            record_distance = target_hash - hash_

            comparison_results.append(ComparisonResult(
                0,
                fileName,
                filePath,
                record_distance
            ))

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
        max_distance = max_val * (100 - similarity) / 100

        for comp_res in comparison_results:
            if comp_res.distance > max_distance:
                break

            item = QTableWidgetItem()
            item.setData(Qt.UserRole, comp_res)
            self.table.addItem(item)

        self.table.update()

    def _getImageData(self, photo_id):
        with open(photo_id, "rb") as file:
            data = file.read()

        return data
