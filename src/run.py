import sys
from PySide6.QtCore import QCoreApplication, QLibraryInfo, QLocale, QSettings, QTranslator
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QDialog
from FindDialog import FindDialog
from Tools import TemporaryDir


class Model():
    fields = [] 


def main():
    app = QApplication(sys.argv)

    QCoreApplication.setOrganizationName('Janis')
    QCoreApplication.setApplicationName('SimilarImageFinder')

    TemporaryDir.init('SimilarImageFinder')

#    locale = QLocale()

#    translator = QTranslator(app)
#    if translator.load(locale, 'lang', '_', ':/i18n'):
#        app.installTranslator(translator)

#    path = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
#    translator = QTranslator(app)
#    if translator.load(locale, 'qtbase', '_', path):
#        app.installTranslator(translator)

    model = Model()

    dlg = FindDialog(model)
    dlg.exec()

    # Clear temporary files
    TemporaryDir.remove()


if __name__ == "__main__":
#    import resources
    main()
