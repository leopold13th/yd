import pprint
import re
import subprocess

from PyQt5.QtCore import Qt  # , QAbstractTableModel, QVariant
# from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout  # QGridLayout
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QPushButton, QLineEdit  # QLabel, QMessageBox

import listofformatswidget


class AddDlg(QDialog):
    """AddDlg."""
    def __init__(self, model, url, parent=None):
        super(AddDlg, self).__init__(parent)
        self.parent = parent
        self.model = model
        self.formats = []

        self.urlEdit = QLineEdit()
        self.btnGetInfo = QPushButton("&Info")
        self.btnGetInfo.clicked.connect(self.btnGetInfoClick)

        urlBox = QHBoxLayout()
        urlBox.addWidget(self.urlEdit)
        urlBox.addWidget(self.btnGetInfo)

        self.listOfFormatsWidget = listofformatswidget.ListOfFormatsWidget()
        self.listOfFormatsWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listOfFormatsWidget.itemClicked.connect(self.listOfFormatsWidget.clicked)
        self.listOfFormatsWidget.currentItemChanged.connect(self.listOfFormatsWidget.itemChanged)

        addButton = QPushButton("&Add")
        addButton.setDefault(True)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttonBox.addButton(addButton, QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.addButtonClick)
        buttonBox.rejected.connect(self.reject)

        grid = QVBoxLayout()
        grid.addLayout(urlBox)
        grid.addWidget(self.listOfFormatsWidget)
        grid.addWidget(buttonBox)

        self.setLayout(grid)
        self.setWindowTitle("Add movie")
        self.setWindowModality(Qt.ApplicationModal)
        self.urlEdit.setText(url)
        self.resize(600, 400)
        # self.exec_()

    def addButtonClick(self):
        # TODO(me): add getting of real props instead of 'Кухня 88'
        audio = ''
        video = ''
        print(self.urlEdit.text())
        rows = self.listOfFormatsWidget.selectionModel().selectedRows()
        for row in rows:
            # print(row.data(), "\n")
            matchLine = re.match(r'^(\d+)\s', row.data(), re.M | re.I)
            if matchLine:
                # print("  @@@>>> ", matchLine.group(1))
                matchVideo = re.match(r'^(\d+)\s.*DASH video', row.data(), re.M | re.I)
                if matchVideo:
                    print("  @@@ Video >>> ", matchVideo.group(1))
                    video = matchLine.group(1)
                matchAudio = re.match(r'^(\d+)\s.*DASH audio', row.data(), re.M | re.I)
                if matchAudio:
                    print("  @@@ Audio >>> ", matchAudio.group(1))
                    audio = matchLine.group(1)

        pp = pprint.PrettyPrinter(indent=4, width=1024)
        # pp.pprint(self.formats)
        
        for f in self.formats:
            print(f)

        self.model.addrow(['Кухня 88', video, audio, '0%', self.urlEdit.text(), self.formats, ])
        self.model.layoutChanged.emit()

        self.accept()

    def btnGetInfoClick(self):
        # Load movie's info
        # https://www.youtube.com/watch?v=G6bSu02Fmxo  - Кухня
        # https://www.youtube.com/watch?v=1IEfCoGnTow  - 100 Years of Flight Attendant Uniforms
        # default format: -o '%(title)s-%(id)s.%(ext)s'
        # youtube-dl -j --flat-playlist

        videoUrl = self.urlEdit.text()
        process_output = subprocess.check_output(["youtube-dl", "-F", videoUrl], universal_newlines=True)
        # print(process_output + "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        lines = process_output.split("\n")
        for line in lines:
            matchLine = re.match(r'^(\d+)\s', line, re.M | re.I)
            if matchLine:
                # print (matchLine.group(1), "  -> ", line)
                self.listOfFormatsWidget.addItem(matchLine.group(1) + "  -> " + line)
                self.formats.append(line)

        fw = 2 * self.listOfFormatsWidget.frameWidth()
        self.listOfFormatsWidget.setFixedSize(self.listOfFormatsWidget.sizeHintForColumn(0) + fw,
                                              self.listOfFormatsWidget.sizeHintForRow(0) * self.listOfFormatsWidget.count() + fw)
        # QMessageBox.information(self, "btnGetInfoClick", "You clicked: ")
