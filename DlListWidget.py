from PyQt5.QtWidgets import QListWidget


class DlListWidget(QListWidget):
    def Clicked(self, item):
        # QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())
        pass

    def itemChanged(self, item):
        # QMessageBox.information(self, "ListWidget", "You itemChanged: " + item.text())
        pass

    # def keyPressEvent(self, e):
    #     if e.key() == Qt.Key_Escape:  # переделать на пробел для выделения по нажатию на пробел
    #         self.close()
