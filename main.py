import sys
import time
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QMainWindow, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QObject
from PyQt5.QtGui import QPixmap, QColor
import cv2
import numpy as np
from layout import Ui_MainWindow

class CountdownThread(QObject):
    finished = pyqtSignal()
    countdown = pyqtSignal(int)

    def __init__(self, counter):
        super().__init__()
        self.countdown_value = counter

    def run(self):
        for i in range(self.countdown_value, 0, -1):
            self.countdown.emit(i)
            #print(i)
            time.sleep(1)
        self.countdown.emit(0)
        self.finished.emit()
        #self.count_class.thread.countdown = 0
        #self.count_class.thread.box_is_active = True
        #self.count_class.set_slider_values()

    @pyqtSlot(int)
    def countdown_box_changed(self, value):
        print(value)
        self.countdown_value = value


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self.video_id = 0
        self.start_point = [[230, 5], [280, 25], [280, 25]]
        self.length = [[230, 470], [200, 415], [200, 415]]
        self.box_is_active = False
        self.color1 = (0, 255, 0)
        self.countdown = 0
        self.cam_is_busy = False
        self.screen_mode = False

        self.cap1 = cv2.VideoCapture(0)
        self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.cap2 = cv2.VideoCapture(2)
        self.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.cap3 = cv2.VideoCapture(4)
        self.cap3.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.screen1 = None
        self.screen2 = None
        self.screen3 = None
        #img_draw = cv2.rectangle(img_draw, start_point, end_point, color1, thickness)

    def run(self):
        # capture from web cam
        #cap1 = cv2.VideoCapture("./out1.avi")
        #cap2 = cv2.VideoCapture("./out2.avi")
        #cap3 = cv2.VideoCapture("./out3.avi")
        #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            if self.screen_mode: 
                self.take_screens()
                self.screen_mode = False
                continue

            if self.video_id == 0:
                cap = self.cap1
                s_point = tuple(self.start_point[0])
                e_point = (self.start_point[0][0] + self.length[0][0], self.start_point[0][1] + self.length[0][1])
                screen = self.screen1
            elif self.video_id == 1:
                cap = self.cap2
                s_point = tuple(self.start_point[1])
                e_point = (self.start_point[1][0] + self.length[1][0], self.start_point[1][1] + self.length[1][1])
                screen = self.screen2
            else:
                cap = self.cap3
                s_point = tuple(self.start_point[2])
                e_point = (self.start_point[2][0] + self.length[2][0], self.start_point[2][1] + self.length[2][1])
                screen = self.screen3
            if screen is not None: 
                cv_img = screen
                ret = True
            else:
                if not self.cam_is_busy:
                    ret, cv_img = cap.read()
                else:
                    continue
                if ret is not True:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, cv_img = cap.read()
            if ret:
                cv_img = cv2.resize(cv_img, (640, 480))
                if self.box_is_active:
                    cv_img = cv2.rectangle(cv_img, s_point, e_point, self.color1, 3)
                if self.countdown > 0:
                    cv2.putText(cv_img,f"{self.countdown}", (320,240), cv2.FONT_HERSHEY_SIMPLEX, 5, 255, thickness=10)
                self.change_pixmap_signal.emit(cv_img)
                time.sleep(0.016)

    def take_screens(self):
        ret, self.screen1 = self.cap1.read()
        ret, self.screen2 = self.cap2.read()
        ret, self.screen3 = self.cap3.read()


class App(Ui_MainWindow, QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.mainWindow = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.mainWindow)
        self.setupUi(self.mainWindow)
        self.disply_width = 640
        self.display_height = 480
        self.image_label.setScaledContents(True)

        self.station_cameras = {"1" : ["1", "2"], "2" : ["1", "3"]}
        self.station_list.addItems(list(self.station_cameras.keys()))

        # Init Signal/Slots
        self.station_list.itemClicked.connect(self.station_list_clicked)
        self.camera_list.itemClicked.connect(self.camera_list_clicked)
        self.compute_box_button.clicked.connect(self.compute_box_clicked)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.width_slider.sliderMoved.connect(self.width_slider_moved)
        self.height_slider.sliderMoved.connect(self.height_slider_moved)
        self.width_box.valueChanged.connect(self.width_box_changed)
        self.height_box.valueChanged.connect(self.height_box_changed)
        self.countdown_box.valueChanged.connect(self.countdown_box_changed)
        self.countdown_box.valueChanged.connect(self.countdown_box_changed)

        # Init Threads
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        self.countdown_thread = QThread()
        self.worker = CountdownThread(5)    
        self.worker.moveToThread(self.countdown_thread)
        self.countdown_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.countdown_thread.quit)
        self.worker.finished.connect(self.countdown_finished)
        self.worker.countdown.connect(self.report_countdown)      


    @pyqtSlot(int)
    def report_countdown(self, i):
        self.thread.countdown = i
        self.log_info(f"Countdown: {i}")

    @pyqtSlot()
    def countdown_finished(self):
        self.thread.box_is_active = True
        self.set_slider_values()
        self.thread.screen_mode=True
        #self.thread.cam_is_busy = True
        #self.thread.take_screens()
        #self.thread.cam_is_busy = False
        #

    @pyqtSlot()
    def set_slider_values(self):
        if not self.thread.box_is_active:
            return
        index = self.thread.video_id

        bbox = self.thread.start_point[index] + self.thread.length[index] 
        width_center = bbox[0] + (bbox[2] / 2)
        height_center = bbox[1] + (bbox[3] / 2)
        slider1_value = int((width_center * 100) / self.disply_width)
        slider2_value = int((height_center * 100) / self.display_height)
        self.width_slider.setValue(slider1_value)
        self.height_slider.setValue(slider2_value)
        self.width_box.setValue(self.thread.length[index][0])
        self.height_box.setValue(self.thread.length[index][1])

    @pyqtSlot()
    def width_slider_moved(self):
        if not self.thread.box_is_active:
            return
        index = self.thread.video_id

        bbox = self.thread.start_point[index] + self.thread.length[index]
        half_width = bbox[2] / 2
        start = (self.width_slider.value() * (self.disply_width / 100)) - half_width
        self.thread.start_point[index][0] = int(start)

    @pyqtSlot()
    def height_slider_moved(self):
        if not self.thread.box_is_active:
            return
        index = self.thread.video_id

        bbox = self.thread.start_point[index] + self.thread.length[index]
        half_height = bbox[3] / 2
        start = (self.height_slider.value() * (self.display_height / 100)) - half_height
        self.thread.start_point[index][1] = int(start)

    @pyqtSlot(int)
    def width_box_changed(self, value):
        print(value)
        if not self.thread.box_is_active:
            return
        index = self.thread.video_id

        self.thread.length[index][0] = value
        self.set_slider_values()

    @pyqtSlot(int)
    def height_box_changed(self, value):
        if not self.thread.box_is_active:
            return
        index = self.thread.video_id

        self.thread.length[index][1] = value
        self.set_slider_values()
        print(self.height_box.value())

    @pyqtSlot(int)
    def countdown_box_changed(self, value):
        self.worker.countdown_value = value

    @pyqtSlot(QListWidgetItem)
    def station_list_clicked(self, item):
        self.camera_list.clear()
        self.camera_list.addItems(self.station_cameras[item.text()])

    @pyqtSlot(QListWidgetItem)
    def camera_list_clicked(self, item):
        self.thread.video_id = int(item.text()) - 1

    @pyqtSlot()
    def compute_box_clicked(self):
        self.countdown_thread.start()

    @pyqtSlot()
    def save_button_clicked(self):
        self.log_info("Data stored into yaml files")

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def show(self):
        self.mainWindow.show()
        sys.exit(self.app.exec_())

    def log_info(self, msg):
        self.log_textbox.setTextColor(QColor(0,0,0))
        self.log_textbox.append(f"[Info] {msg}")

    def log_error(self, msg):
        self.log_textbox.setTextColor(QColor(255,0,0))
        self.log_textbox.append(f"[ERROR] {msg}")

if __name__=="__main__":
    a = App()
    a.show()
