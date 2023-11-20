import os
import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from FindDialog import FindDialog


class Model():
    fields = []

    def __init__(self):
        self.folder = None

    def setFolder(self, folder):
        self.folder = folder

    def getPhotoCount(self):
        count = 0
        if self.folder:
            for path in os.scandir(self.folder):
                if path.is_file():
                    count += 1

        return 0


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
