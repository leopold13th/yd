import logging
import json

from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant

class Model(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.gui = parent
        self.colLabels = ['Title', 'Video', 'Audio', 'Progress', 'URL']

        self._data = []
        # self._data = [
        #                ['Кухня 87', '140', '137', '0%', 'https://www.youtube.com/watch?v=G6bSu02Fmxo', [],],
        #                ['Кухня 92', '140', '137', '0%', 'https://www.youtube.com/watch?v=thazG-S8J-Q', [],],
        #                ['100 Years of Flight Attendant Uniforms', '160', '249', '0%', 'https://www.youtube.com/watch?v=1IEfCoGnTow', [],],
        #              ]
        with open('yd.json', encoding='utf-8') as f:
            data = json.load(f)
            # print(json.dumps(data, indent=2))
            # print(data["items"][0])
            for el in data["items"]:
                print(el["formats"])
                print("\n\n")
                self._data.append([el["title"], el["video"], el["audio"], '0%', el["url"], el["formats"],])

    
    def save(self):
        state = { 'items': self._data }
        with open('yd-new.json', mode='w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self.colLabels)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        value = ''
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self._data[row][col]
        return QVariant(value)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.colLabels[section])
        return QVariant()

    def addrow(self, row):
        self._data.append(row)

    def getRowByIdx(self, idx):
        return self._data[idx]

    def getFormatsByIdx(self, idx):
        return self._data[idx][1] + "+" + self._data[idx][2]

    def getListOfFormatsByIdx(self, idx):
        return self._data[idx][5]

    def getUrlByIdx(self, idx):
        return self._data[idx][4]

    def updateProgress(self, idx, value1, value2):
        self._data[idx][3] = str(value1) + "+" + str(value2)
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        # logging.debug(self._data[idx])
