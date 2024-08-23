import os
import sys

from PyQt6 import sip
from PyQt6.QtCore import Qt, QCoreApplication, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QProgressDialog, \
    QMainWindow, QProgressBar, QRadioButton, \
    QLabel, QFrame, QStyle, QSizePolicy, QButtonGroup, QComboBox, QHBoxLayout, QFileDialog, QToolBar

from tonberrymanager import TonberryManager, Shop


class TonberryShop(QWidget):
    NB_COLUMN_ITEM = 4

    def __init__(self, icon_path='Resources'):

        QWidget.__init__(self)
        self.tonberry_manager = TonberryManager()
        self.file_path = ""
        self.current_shop_index = 0
        # Main window
        self.setWindowTitle("TonberryShop")
        self.setWindowIcon(QIcon(os.path.join(icon_path, 'icon.png')))

        self.layout_top = QHBoxLayout()
        self.layout_item = QHBoxLayout()
        self.layout_main = QVBoxLayout()

        self.file_dialog = QFileDialog()
        self.file_dialog_button = QPushButton()
        self.file_dialog_button.setIcon(QIcon(os.path.join(icon_path, 'folder.png')))
        self.file_dialog_button.setFixedSize(30,30)
        self.file_dialog_button.clicked.connect(self.load_file)

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(os.path.join(icon_path, 'save.svg')))
        self.save_button.setFixedSize(30,30)
        self.save_button.clicked.connect(self.save_file)

        self.shop_list = QComboBox()
        self.shop_list.addItems([f"Shop n°{i+1}" for i in range(self.tonberry_manager.NB_SHOP)])
        self.shop_list.activated.connect(self.reload_item)

        self.item_combo = [QComboBox() for i in range(Shop.NB_ITEM_PER_SHOP)]
        self.item_rare = [QCheckBox("Rare") for i in range(Shop.NB_ITEM_PER_SHOP)]
        [rare.setLayoutDirection(Qt.LayoutDirection.RightToLeft) for rare in self.item_rare]
        self.item_label = [QLabel(f"Item n°{i+1}: ") for i in range(Shop.NB_ITEM_PER_SHOP)]
        self.layout_single_item = [QHBoxLayout() for i in range(Shop.NB_ITEM_PER_SHOP)]
        for i in range(Shop.NB_ITEM_PER_SHOP):
            self.item_combo[i].addItems(list(self.tonberry_manager.item_values.values()))
            self.item_combo[i].activated.connect(self.__save_to_shop_info)
            self.item_rare[i].toggled.connect(self.__save_to_shop_info)

            self.layout_single_item[i].addWidget(self.item_label[i])
            self.layout_single_item[i].addWidget(self.item_rare[i])
            self.layout_single_item[i].addWidget(self.item_combo[i])

        self.layout_sub_item =  [QVBoxLayout() for i in range(self.NB_COLUMN_ITEM)]
        self.qframe =  [QFrame() for i in range(self.NB_COLUMN_ITEM-1)]
        for i in range(self.NB_COLUMN_ITEM):
            self.layout_item.addLayout(self.layout_sub_item[i])
            if i < self.NB_COLUMN_ITEM-1:
                self.qframe[i].setFrameStyle(0x05)
                self.qframe[i].setLineWidth(2)
                self.layout_item.addWidget(self.qframe[i])
            for j in range(i*self.NB_COLUMN_ITEM, i*self.NB_COLUMN_ITEM+self.NB_COLUMN_ITEM):
                self.layout_sub_item[i].addLayout(self.layout_single_item[j])

        self.layout_top.addWidget(self.file_dialog_button)
        self.layout_top.addWidget(self.save_button)
        self.layout_top.addWidget(self.shop_list)
        self.layout_top.addStretch(1)

        self.layout_main.addLayout(self.layout_top)
        self.layout_main.addLayout(self.layout_item)

        self.setLayout(self.layout_main)
        self.show()

    def load_file(self):
        file_name = self.file_dialog.getOpenFileName(parent=self, caption="Search shop.bin file", filter="*.bin", directory=os.getcwd())[0]
        if file_name:
            self.file_path = file_name
            self.tonberry_manager.read_shop_file(file_name)
            self.tonberry_manager.analyze_shop_file()
            self.reload_item()

    def save_file(self):
        if self.file_path:
            print("Writting")
            print(self.file_path)
            self.tonberry_manager.write_shop_file(self.file_path)

    def __save_to_shop_info(self):
            for item_index in range(Shop.NB_ITEM_PER_SHOP):
                self.tonberry_manager.shop_info[self.current_shop_index].item[item_index] = self.item_combo[item_index].currentText()
                self.tonberry_manager.shop_info[self.current_shop_index].rare[item_index] = self.item_rare[item_index].isChecked()

    def reload_item(self):
        self.current_shop_index = self.shop_list.currentIndex()
        for i in range(Shop.NB_ITEM_PER_SHOP):
            self.item_combo[i].setCurrentText(self.tonberry_manager.shop_info[self.current_shop_index].item[i])
            self.item_rare[i].setChecked(self.tonberry_manager.shop_info[self.current_shop_index].rare[i])