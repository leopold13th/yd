#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import pprint
import logging
import queue
import re
import subprocess
import sys
import threading

from PyQt5.QtCore import QCoreApplication, QBasicTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QSplitter, QComboBox, QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QTableView, QTableWidget, QTableWidgetItem, QAbstractItemView, QTabWidget
from PyQt5.QtWidgets import QVBoxLayout

import AddDlg
import DlListWidget
import tmodel

# from PyQt5.QtWidgets import QMessageBox

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.q = queue.Queue()
        self.initUI()
        self.initDlMgr()

    def initUI(self):
        self.curUrl = ''

        self.setMenu()

        # List of downloads
        self.table = QTableView(self)
        self.model = tmodel.Model(self.table)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.resizeColumnsToContents()
        # selectionModel = self.table.selectionModel()
        self.table.selectionModel().currentChanged.connect(self.currentChangedTable)

        # List of formats
        self.cbVideo = QComboBox()
        self.cbAudio = QComboBox()
        self.cbOther = QComboBox()
        self.cbVideo.activated.connect(self.videoChange)
        self.cbAudio.activated.connect(self.audioChange)
        self.cbOther.activated.connect(self.otherChange)

        self.tblFormats = QTableWidget() #(self)
        self.tblFormats.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblFormats.setColumnCount(2)
        self.tblFormats.setRowCount(2)
        self.tblFormats.setHorizontalHeaderLabels(["id", "Format"])

        layout1 = QVBoxLayout()
        layout1.addWidget(QLabel("Video:"))
        layout1.addWidget(self.cbVideo)
        layout1.addWidget(QLabel("Audio:"))
        layout1.addWidget(self.cbAudio)
        layout1.addWidget(QLabel("Video+Audio:"))
        layout1.addWidget(self.cbOther)
        # layout1.addWidget(self.tblFormats)

        # Tabs
        self._tabs = QTabWidget()
        self.tab1 = QWidget()   
        # self.tab2 = QWidget()
        self.tab1.setLayout(layout1)
        self._tabs.addTab(self.tab1, "Formats")
        # self._tabs.addTab(self.tab2, "Settings")

        # Splitter
        vsplitter = QSplitter(Qt.Vertical)
        vsplitter.addWidget(self.table)
        vsplitter.addWidget(self._tabs)

        vbox = QVBoxLayout()
        vbox.addWidget(vsplitter)

        mainWidget = QWidget(self)
        mainWidget.setLayout(vbox)

        self.setCentralWidget(mainWidget)
        self.setGeometry(20, 100, 1000, 600)
        self.setWindowTitle('Youtube-dl')
        self.setWindowIcon(QIcon('icons/gamma.png'))
        self.show()

        # timer
        self.timer = QBasicTimer()
        self.timer.start(300, self)

    def setMenu(self):
        menubar = self.menuBar()

        addAction = QAction(QIcon('icons/add.png'), '&Add', self)
        addAction.setShortcut('Ctrl+A')
        addAction.setStatusTip('Add link to movie')
        addAction.triggered.connect(self.addLink)

        delAction = QAction(QIcon('icons/delete.png'), '&Delete', self)
        delAction.setShortcut('Alt+D')
        delAction.setStatusTip('Delete link')
        delAction.triggered.connect(self.delLink)

        exitAction = QAction(QIcon('icons/exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QCoreApplication.instance().quit)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(addAction)
        fileMenu.addAction(delAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        startAction = QAction(QIcon('icons/player_play.png'), '&Start', self)
        startAction.setShortcut('Ctrl+S')
        startAction.setStatusTip('Start download')
        startAction.triggered.connect(self.startItem)

        stopAction = QAction(QIcon('icons/player_stop.png'), '&Stop', self)
        stopAction.setShortcut('Ctrl+P')
        stopAction.setStatusTip('Stop download')
        stopAction.triggered.connect(self.stopItem)

        aMenu = menubar.addMenu('&Actions')
        aMenu.addAction(startAction)
        aMenu.addAction(stopAction)

    def initDlMgr(self):
        logging.debug("Starting Download Manager...")
        # self.testvar = "25"
        t = threading.Thread(name='DlMgr', target=self.dlMgr, args=("j932jdjokmjoas0f2",))
        t.start()

    def dlMgr(self, x):
        logging.debug("Download Manager started. TestArgument: " + x)

    def addLink(self):
        adddlg = AddDlg.AddDlg(self.model, "", self)
        adddlg.exec_()
        # self.table.model().layoutChanged.emit()

    def delLink(self):
        pass

    def startItem(self):
        threading.Thread(target=self.startItemInThread, args=(self.q,)).start()

    def startItemInThread(self, q):
        videoUrl = self.model.getUrlByIdx(self.selectedIdx)
        formats = self.model.getFormatsByIdx(self.selectedIdx)

        logging.debug("Starting Downloading " + videoUrl + "     formats: " + formats)

        cmd = ["youtube-dl",
               "--no-color",
               "--no-playlist",
               "--newline",
               "-f", formats,
               videoUrl]
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        isVideo = 0
        isAudio = 0
        videoProgress = 0
        audioProgress = 0
        while(p.poll() is None):
            line = p.stdout.readline().rstrip().decode("utf-8")
            logging.debug(line)
            sp = line.split()
            if len(sp) > 0 and sp[0].strip() == '[download]':
                if sp[1] == 'Destination:':
                    if isVideo == 0 and isAudio == 0:
                        isVideo = 1
                        isAudio = 0
                    elif isVideo == 1 and isAudio == 0:
                        isVideo = 0
                        isAudio = 1
                else:
                    if isVideo == 1 and isAudio == 0:
                        videoProgress = sp[1]
                    if isVideo == 0 and isAudio == 1:
                        audioProgress = sp[1]
                    # print(isVideo, "v<<->>a", isAudio, ";", videoProgress, "->>>", audioProgress)

                    # self.model.updateProgress(self.selectedIdx, videoProgress)
                    q.put((self.selectedIdx, videoProgress, audioProgress))
        logging.debug("Done")

    def stopItem(self):
        pass

    def currentChangedTable(self, current, previous):
        # print("--->>> itemChanged ", current.row(), " % ", current.data())
        self.selectedIdx = current.row()
        self.tblFormats.setRowCount(10)

        formats = self.model.getListOfFormatsByIdx(self.selectedIdx)
        for i, f in enumerate(formats["video"]):
    	    format = formats["video"][i]
    	    self.tblFormats.setItem(i,0, QTableWidgetItem("video"))
    	    self.tblFormats.setItem(i,1, QTableWidgetItem(format))

        self.tblFormats.resizeColumnsToContents()

        self.cbVideo.clear()
        for i, f in enumerate(formats["video"]):
            format = formats["video"][i]
            self.cbVideo.addItem(format)

        self.cbAudio.clear()
        for i, f in enumerate(formats["audio"]):
            format = formats["audio"][i]
            self.cbAudio.addItem(format)

        self.cbOther.clear()
        for i, f in enumerate(formats["other"]):
            format = formats["other"][i]
            self.cbOther.addItem(format)

    def videoChange(self,i):
        print("Items in the list are : videoChange")

    def audioChange(self,i):
        print("Items in the list are : audioChange")

    def otherChange(self,i):
        print("Items in the list are : otherChange")

    def timerEvent(self, e):
        while not self.q.empty():
            progress = self.q.get()
            self.q.task_done()
            print(progress)
            self.model.updateProgress(progress[0], progress[1], progress[2])
        
        cb_text = cb.text().strip()
        if self.curUrl == cb_text:
            return
        else:
            self.curUrl = cb_text
        # print(cb_text)
        if cb_text[0:7] == "http://" or cb_text[0:8] == "https://":
            matchUrl = re.match(r'http.?://.*\.youtube\.com/watch(.*)', cb_text, re.M | re.I)
            if matchUrl:
                # print ("matchUrl.group() : ", matchUrl.group())
                # print ("matchUrl.group(1) : ", matchUrl.group(1))
                # print ("matchUrl.group(2) : ", matchUrl.group(2))
                self.activateWindow()
                adddlg = AddDlg.AddDlg(self.model, cb_text, self)
                adddlg.exec_()

    # def closeEvent(self, event):
    #     reply = QMessageBox.question(self, 'Quit?', "Are you sure to quit?",
    #                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()


# class clipboardListener(QObject):
#     @pyqtSlot()
#     def changedSlot(self):
#         if(QApplication.clipboard().mimeData().hasText()):
#             QMessageBox.information(None, "ClipBoard Text Copy Detected!", "You Copied:" + QApplication.clipboard().text());


if __name__ == '__main__':
    # listener = clipboardListener()
    # QObject.connect(QApplication.clipboard(), SIGNAL("dataChanged()"),
    #       listener, SLOT("changedSlot()"))
    app = QApplication(sys.argv)
    cb = app.clipboard()
    ex = MainWindow()
    sys.exit(app.exec_())
