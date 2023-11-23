import blockhash.core
import cv2
import imagehash
import io
from dataclasses import dataclass
from PIL import Image

from PySide6.QtCore import Qt, QBuffer, QMargins, QRect, QRectF, QSettings
from PySide6.QtGui import QImage, QPixmap, QIcon, QTextOption, QPalette
from PySide6.QtSql import QSqlQuery
from PySide6.QtWidgets import *

try:
    from OpenNumismat.EditCoinDialog.ImageLabel import ImageEdit, ImageLabel
    from OpenNumismat.Tools.DialogDecorators import storeDlgSizeDecorator
    from OpenNumismat.Tools import Gui
    from OpenNumismat.Collection.CollectionFields import FieldTypes as Type
except ModuleNotFoundError:
    from ImageLabel import ImageEdit, ImageLabel
    from Tools.DialogDecorators import storeDlgSizeDecorator
    from Tools import Gui


@dataclass(slots=True, frozen=True)
class ComparisonResult:
    coin_id: int
    coin_title: str
    photo_id: int
    distance: float


@storeDlgSizeDecorator
class FindDialog(QDialog):

    def __init__(self, model, parent=None):
        super().__init__(parent,
                         Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)

        settings = QSettings()

        self.model = model

        self.setWindowIcon(QIcon(':/binoculars.png'))
        self.setWindowTitle(self.tr("Find"))

        self.targetImgLabel = ImageEdit()
        self.targetImgLabel.imageChanged.connect(self.imageChanged)

        self.imgLabel = ImageLabel()
        self.imgLabel.setFrameStyle(QFrame.Panel | QFrame.Plain)

        form_layout = QFormLayout()

        self.methodSelector = QComboBox()
        self.methodSelector.setSizePolicy(QSizePolicy.Fixed,
                                          QSizePolicy.Fixed)
        self.methodSelector.addItem("Average", 'ahash')
        self.methodSelector.addItem("Perceptual", 'phash')
        self.methodSelector.addItem("Difference", 'dhash')
        self.methodSelector.addItem("Wavelet", 'whash')
        self.methodSelector.addItem("Color", 'colorhash')
        self.methodSelector.addItem("Crop-resistant", 'crop_resistant_hash')
        self.methodSelector.addItem("Average (OpenCV)", 'ahash_cv')
        self.methodSelector.addItem("BlockMean", 'blockhash')
        self.methodSelector.addItem("ColorMoment", 'colorhash_cv')
        self.methodSelector.addItem("Marr-Hildreth", 'mhhash')
        self.methodSelector.addItem("Perceptual (OpenCV)", 'phash_cv')
        self.methodSelector.addItem("Radial Variance", 'radialhash')
        self.methodSelector.addItem("Block", 'bhash')
        method = settings.value('image_find/method', 'phash')
        index = self.methodSelector.findData(method)
        if index:
            self.methodSelector.setCurrentIndex(index)

        form_layout.addRow(self.tr("Hashing method"), self.methodSelector)

        self.similarityLabel = QLabel()
        self.similaritySlider = QSlider(Qt.Horizontal)
        self.similaritySlider.setRange(0, 100)
        self.similaritySlider.setTickInterval(10)
        self.similaritySlider.setTickPosition(QSlider.TicksAbove)
        self.similaritySlider.setSizePolicy(QSizePolicy.Preferred,
                                            QSizePolicy.Fixed)
        self.similaritySlider.valueChanged.connect(self.similarityChanged)
        similarity = settings.value('image_find/similarity', 75, type=int)
        self.similaritySlider.setValue(similarity)

        form_layout.addRow(self.similarityLabel, self.similaritySlider)

        self.fieldsCheckBox = {}
        if self.model.fields:
            field_layout = QGridLayout()
            field_box = QGroupBox(self.tr("Field"))
            field_box.setLayout(field_layout)

            field_pos = 0
            fields_per_row = 2
            for field in self.model.fields:
                if field.type == Type.Image and field.enabled:
                    checkBox = QCheckBox(field.title)
                    checked = settings.value("image_find/%s" % field.name, True, type=bool)
                    checkBox.setChecked(checked)

                    self.fieldsCheckBox[field.name] = checkBox
                    field_layout.addWidget(checkBox, field_pos // fields_per_row,
                                           field_pos % fields_per_row)
                    field_pos += 1

            form_layout.addRow(field_box)

        self.findButton = QPushButton(self.tr("Start"))
        self.findButton.setEnabled(False)
        self.findButton.setSizePolicy(QSizePolicy.Fixed,
                                      QSizePolicy.Fixed)
        self.findButton.clicked.connect(self.start)

        ctrl_layout = QVBoxLayout()
        ctrl_layout.addLayout(form_layout)
        ctrl_layout.addWidget(self.findButton)

        img_layout = QHBoxLayout()
        img_layout.addWidget(self.targetImgLabel)
        img_layout.addWidget(self.imgLabel)
        img_layout.addLayout(ctrl_layout)
        img_layout.setContentsMargins(QMargins())

        buttonBox = QDialogButtonBox(Qt.Horizontal)
        buttonBox.addButton(QDialogButtonBox.Close)
        buttonBox.rejected.connect(self.reject)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        widget = QWidget()
        widget.setLayout(img_layout)
        self.splitter.addWidget(widget)
        self.splitter.addWidget(QWidget())

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def similarityChanged(self, val):
        self.similarityLabel.setText(self.tr("Similarity") + " (%d%%)" % val)

    def imageChanged(self, label):
        self.findButton.setEnabled(bool(label.data()))

    def saveSettings(self):
        settings = QSettings()

        method = self.methodSelector.currentData()
        settings.setValue('image_find/method', method)

        similarity = self.similaritySlider.value()
        settings.setValue('image_find/similarity', similarity)

        for field, check_box in self.fieldsCheckBox.items():
            settings.setValue("image_find/%s" % field, check_box.isChecked())

    def start(self):
        self.saveSettings()

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

        if not fields:
            QMessageBox.warning(self, self.tr("Find"),
                                self.tr("No image fields selected"))
            return

        # Get count of coins with photos
        row_count = 0
        sql = "SELECT COUNT(*) FROM coins"
        for field in fields:
            sql += " LEFT JOIN photos %s ON coins.%s=%s.id" % (field, field, field)
        if self.model.filter():
            sql += " WHERE " + self.model.filter()
        query = QSqlQuery(sql, self.model.database())
        if query.first():
            record = query.record()
            row_count = record.value(0)

        sql_fileds = ""
        for field in fields:
            sql_fileds += ", %s.image AS %s_image, %s.id AS %s_id" % (field, field, field, field)
        sql = "SELECT coins.id, coins.title%s FROM coins" % sql_fileds
        for field in fields:
            sql += " LEFT JOIN photos %s ON coins.%s=%s.id" % (field, field, field)
        if self.model.filter():
            # TODO: Filter by title fail this request
            sql += " WHERE " + self.model.filter()
        query = QSqlQuery(sql, self.model.database())

        progressDlg = Gui.ProgressDialog(
                    self.tr("Processing..."),
                    self.tr("Cancel"), row_count,
                    self)

        comparison_results = []

        while query.next():
            progressDlg.step()
            if progressDlg.wasCanceled():
                break

            record = query.record()
            coin_id = record.value('coins.id')
            coin_title = record.value('coins.title')

            record_distances = {}
            for field in fields:
                img = record.value('%s_image' % field)
                if img:
                    pil_img = Image.open(io.BytesIO(img))
                    hash_ = self._imageHash(pil_img, method)

                    # TODO: Test similarity threshold here
                    record_distances[field] = target_hash - hash_
                    # record_distances[field] = (target_hash - hash_) / len(hash_.hash) ** 2

            if record_distances:
                field = min(record_distances, key=record_distances.get)
                photo_id = record.value('%s_id' % field)
                distance = record_distances[field]

                comparison_results.append(ComparisonResult(
                    coin_id,
                    coin_title,
                    photo_id,
                    distance
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

    def _imageHash(self, image, method):
        if method == 'ahash':
            return imagehash.average_hash(image)
        elif method == 'phash':
            return imagehash.phash(image)
        elif method == 'dhash':
            return imagehash.dhash(image)
        elif method == 'whash':
            return imagehash.whash(image)
        elif method == 'colorhash':
            return imagehash.colorhash(image)
        elif method == 'crop_resistant_hash':
            return imagehash.crop_resistant_hash(image)
        elif method == 'ahash_cv':
            hsh = cv2.img_hash.AverageHash_create()
            return hsh.compute(image)
        elif method == 'blockhash':
            hsh = cv2.img_hash.BlockMeanHash_create()
            return hsh.compute(image)
        elif method == 'colorhash_cv':
            hsh = cv2.img_hash.ColorMomentHash_create()
            return hsh.compute(image)
        elif method == 'mhhash':
            hsh = cv2.img_hash.MarrHildrethHash_create()
            return hsh.compute(image)
        elif method == 'phash_cv':
            hsh = cv2.img_hash.PHash_create()
            return hsh.compute(image)
        elif method == 'radialhash':
            hsh = cv2.img_hash.RadialVarianceHash_create()
            return hsh.compute(image)
        elif method == 'bhash':
            hash_ = blockhash.core.blockhash_even(image)
            return imagehash.hex_to_hash(hash_)

    def _updateTableSizes(self):
        defaultHeight = self.table.verticalHeader().defaultSectionSize()
        height_multiplex = self.model.settings['image_height']
        height = defaultHeight * height_multiplex * 2
        self.table.verticalHeader().setDefaultSectionSize(int(height + 42))
        self.table.horizontalHeader().setDefaultSectionSize(int(height + 10 * height_multiplex))

    def showImage(self, photo_id):
        data = self._getImageData(photo_id)
        self.imgLabel.loadFromData(data)

    def _getImageData(self, photo_id):
        query = QSqlQuery(self.model.database())
        query.prepare("SELECT image FROM photos WHERE id=?")
        query.addBindValue(photo_id)
        query.exec_()
        if query.first():
            record = query.record()
            return record.value(0)

        return None


class TableWidget(QTableWidget):

    def __init__(self, img_widget, parent=None):
        super().__init__(parent)

        self.img_widget = img_widget

        self.setShowGrid(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.doubleClicked.connect(self.itemDClicked)

        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

        self.setItemDelegate(CardDelegate(self))

        self.count = 0
        self.items = []

    def itemDClicked(self, index):
        comp_res = index.data(Qt.UserRole)
        if comp_res:
            currentListView = self.img_widget.parent().viewTab.currentListView()
            currentListView.selectedId = comp_res.coin_id
            currentListView.modelChanged()  # TODO: Doesn't working when CardView is active
            if currentListView.selectedId:
                currentListView.itemDClicked(None)

    def addItem(self, item):
        self.items.append(item)
        self.setItem(0, self.count, item.clone())
        self.count += 1

    def currentChanged(self, current, previous):
        comp_res = current.data(Qt.UserRole)
        if comp_res:
            self.img_widget.showImage(comp_res.photo_id)

        return super().currentChanged(current, previous)

    def resizeEvent(self, event):
        self.update()
        return super().resizeEvent(event)

    def update(self):
        if self.count == 0:
            return

        width = self.width()
        vertical_bar = self.verticalScrollBar()
        if vertical_bar.isVisible():
            width -= vertical_bar.width() + 2
        col_width = self.columnWidth(0)
        columns = width // col_width
        if columns == self.columnCount():
            return

        rows = (self.count + columns - 1) // columns

        selected_pos = -1
        selected_items = self.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            selected_pos = self.columnCount() * selected_item.row() + selected_item.column()

        self.clear()
        self.setColumnCount(columns)
        self.setRowCount(rows)

        for i in range(rows):
            for j in range(columns):
                pos = i * columns + j
                if pos < self.count:
                    item = self.items[i * columns + j].clone()
                    if pos == selected_pos:
                        selected_item = item
                else:
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemIsEnabled)
                self.setItem(i, j, item)

        if selected_pos >= 0:
            self.setCurrentItem(selected_item)


class CardDelegate(QStyledItemDelegate):
    LABEL_HEIGHT = 30 + 4

    def paint(self, painter, option, index):
        comp_res = index.data(Qt.UserRole)
        if comp_res and comp_res.photo_id:
            image_data = self.parent().img_widget._getImageData(comp_res.photo_id)

            palette = QPalette()
            if option.state & QStyle.State_HasFocus or option.state & QStyle.State_Selected:
                color = palette.color(QPalette.HighlightedText)
                back_color = palette.color(QPalette.Highlight)
            else:
                color = palette.color(QPalette.Text)
                back_color = palette.color(QPalette.Midlight)

            painter.setPen(back_color)
            rect = option.rect.marginsRemoved(QMargins(1, 1, 1, 1))
            painter.drawRect(rect)

            text_rect = QRect(rect)
            text_rect.setHeight(self.LABEL_HEIGHT)
            painter.fillRect(text_rect, back_color)

            text_rect = rect.marginsRemoved(QMargins(3, 2, 2, 2))
            text_rect.setHeight(30)

            painter.setPen(color)
            text_option = QTextOption()
            text_option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            painter.drawText(QRectF(text_rect), comp_res.coin_title, text_option)

            rect.setY(rect.y() + self.LABEL_HEIGHT + 1)
            rect.setHeight(rect.height() - 1)
            image_rect = QRect(rect.x(), rect.y(),
                               rect.width(), rect.height())

            maxWidth = image_rect.width() - 4
            maxHeight = image_rect.height() - 4

            image = QImage()
            image.loadFromData(image_data)
            if image.width() > maxWidth or image.height() > maxHeight:
                scaledImage = image.scaled(maxWidth, maxHeight,
                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                scaledImage = image
            pixmap = QPixmap.fromImage(scaledImage)
            # Set rect at center of item
            image_rect.translate((image_rect.width() - pixmap.width()) // 2,
                                 (image_rect.height() - pixmap.height()) // 2)
            image_rect.setSize(pixmap.size())
            painter.drawPixmap(image_rect, pixmap)
