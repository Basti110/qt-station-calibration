# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(853, 797)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.layoutWidget = QtWidgets.QWidget(self.splitter_2)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.layoutWidget)
        self.splitter.setFrameShape(QtWidgets.QFrame.Box)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setObjectName("splitter")
        self.frame_2 = QtWidgets.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.image_label = QtWidgets.QLabel(self.frame_2)
        self.image_label.setObjectName("image_label")
        self.gridLayout_3.addWidget(self.image_label, 0, 0, 1, 1)
        self.height_slider = QtWidgets.QSlider(self.frame_2)
        self.height_slider.setProperty("value", 50)
        self.height_slider.setTracking(True)
        self.height_slider.setOrientation(QtCore.Qt.Vertical)
        self.height_slider.setInvertedAppearance(True)
        self.height_slider.setObjectName("height_slider")
        self.gridLayout_3.addWidget(self.height_slider, 0, 1, 1, 1)
        self.width_slider = QtWidgets.QSlider(self.frame_2)
        self.width_slider.setProperty("value", 50)
        self.width_slider.setTracking(True)
        self.width_slider.setOrientation(QtCore.Qt.Horizontal)
        self.width_slider.setInvertedAppearance(False)
        self.width_slider.setInvertedControls(False)
        self.width_slider.setObjectName("width_slider")
        self.gridLayout_3.addWidget(self.width_slider, 1, 0, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.splitter)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.splitter_3 = QtWidgets.QSplitter(self.frame_3)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter_3)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.station_list = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.station_list.setObjectName("station_list")
        self.verticalLayout.addWidget(self.station_list)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.splitter_3)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.camera_list = QtWidgets.QListWidget(self.verticalLayoutWidget_2)
        self.camera_list.setObjectName("camera_list")
        self.verticalLayout_2.addWidget(self.camera_list)
        self.gridLayout_5.addWidget(self.splitter_3, 0, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.splitter)
        self.frame_6 = QtWidgets.QFrame(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame_6)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.compute_box_button = QtWidgets.QPushButton(self.frame_6)
        self.compute_box_button.setObjectName("compute_box_button")
        self.horizontalLayout_3.addWidget(self.compute_box_button)
        self.label_3 = QtWidgets.QLabel(self.frame_6)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.width_box = QtWidgets.QSpinBox(self.frame_6)
        self.width_box.setMaximum(1920)
        self.width_box.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.width_box.setObjectName("width_box")
        self.horizontalLayout_3.addWidget(self.width_box)
        self.label_4 = QtWidgets.QLabel(self.frame_6)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.height_box = QtWidgets.QSpinBox(self.frame_6)
        self.height_box.setMaximum(1080)
        self.height_box.setObjectName("height_box")
        self.horizontalLayout_3.addWidget(self.height_box)
        self.label_6 = QtWidgets.QLabel(self.frame_6)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        self.countdown_box = QtWidgets.QSpinBox(self.frame_6)
        self.countdown_box.setProperty("value", 5)
        self.countdown_box.setObjectName("countdown_box")
        self.horizontalLayout_3.addWidget(self.countdown_box)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.save_button = QtWidgets.QPushButton(self.frame_6)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout_3.addWidget(self.save_button)
        self.gridLayout_4.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.frame_6)
        self.frame = QtWidgets.QFrame(self.splitter_2)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)
        self.log_textbox = QtWidgets.QTextEdit(self.frame)
        self.log_textbox.setReadOnly(True)
        self.log_textbox.setObjectName("log_textbox")
        self.gridLayout_2.addWidget(self.log_textbox, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 853, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DigiGym Calibration"))
        self.image_label.setText(_translate("MainWindow", "Image"))
        self.label.setText(_translate("MainWindow", "Station List"))
        self.label_2.setText(_translate("MainWindow", "Camera List"))
        self.compute_box_button.setText(_translate("MainWindow", "Compute Box"))
        self.label_3.setText(_translate("MainWindow", "Box width (px)"))
        self.label_4.setText(_translate("MainWindow", "Box height (px)"))
        self.label_6.setText(_translate("MainWindow", "Countdown"))
        self.save_button.setText(_translate("MainWindow", "Save"))
        self.label_5.setText(_translate("MainWindow", "Log Box:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
