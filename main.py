import sys
import time
from dataclasses import dataclass
from typing import List
from ast import literal_eval as make_tuple
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QMainWindow, QListWidgetItem, QDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QObject
from PyQt5.QtGui import QPixmap, QColor, QImage
import cv2
import numpy as np
import psycopg2
from layout import Ui_MainWindow
from dialog_station_add import Ui_Dialog as StationAddDialogUI
from dialog_station_edit import Ui_Dialog as StationEditDialogUI

# Todo: frame {(c_id, s_id): FrameBox} => {c_id : (s_id): FrameBox}
# Todo: do not iterate over frame boxes! Mapping Frame ID to FrameBoxes
# Todo: Größe auf 720p anpassen

def make_items_from_dict(labels, index = 0):
    """Qt item list with key as item data

    Args:
    labels (dict[int, list]): All dict entries are converted to items. The key are added as data
    index (int): The index to the item label in the entry

    Returns:
    list[items]: A converted list of qt items
    """
    item_list = []
    for key, value in labels.items():
        item = QListWidgetItem()
        item.setText(value[index])
        item.setData(Qt.UserRole, int(key))
        item_list.append(item)
    return item_list

def insert_items_into_widget(qt_widget, item_list):
    for i in item_list:
        qt_widget.addItem(i)

def insert_dict_into_widget(qt_widget, label_dict, index = 0):
    item_list = make_items_from_dict(label_dict, index)
    insert_items_into_widget(qt_widget, item_list)

# @dataclass
# class FrameBox:
#     point1 = (int(0), int(0))
#     point2 = (int(0), int(0))

@dataclass(init=True)
class FrameBox:
    start : List[int]
    length : List[int]
    frame_id : int = int(-1)
    is_modified = False
    is_new = False

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

class DataManager(QObject):
    cameras_modified = pyqtSignal()
    stations_modified = pyqtSignal()
    stations_cameras_modified = pyqtSignal()
    stations_exercises_modified = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self._cameras = {0: ["cam1"], 10: ["cam2"], 11: ["cam3"], 12: ["cam4"]}
        self._exercises = ["Bizeps-Curls", "Flys", "Unterarm-Curls", "Cable Crossover", "Rumpf-Twist",
            "Seitheben", "Schulterdrücken", "Kurzhanteln-Rudern"]
        self._stations = None
        self._cameras = None
        self._station_cameras = None
        self._frame_boxes = None
        #self._stations = {0: ['Hantelbank'], 10: ['Cable Tower'], 11: ['station_2']}
        #self._station_cameras = {0: [0, 10], 10: [0, 11]}
        #self._station_cameras_ids = {0: [0, 10], 10: [0, 11]}
        #self._frame_boxes = {(0,0): FrameBox}
        self._station_exercises = {}

        try:
            self.connection = psycopg2.connect(user="ted",
                                    password="esel1212",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="trainerai_db")
            self.cursor = self.connection.cursor()
        except psycopg2.Error as error:
            raise RuntimeError('Failed to open database') from error

        self.update_cameras()
        self.update_stations()
        self.update_station_cameras()
        self.update_frame_boxes()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def update_cameras(self):
        select_query = "select * from camera_list"
        try:
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchall()
            camera_list = {}
            for row in mobile_records:
                camera_list[row[0]] = [row[1]]
            self._cameras = camera_list
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def update_stations(self):
        try:
            select_query = "select * from station_list"
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchall()
            station_list = {}
            for row in mobile_records:
                station_list[row[0]] = [row[1]]
            self._stations = station_list
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def update_station_cameras(self):
        try:
            select_query = "select * from camera_station_join"
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchall()

            station_cameras = {}
            for row in mobile_records:
                if row[2] not in station_cameras:
                    station_cameras[row[2]] = []
                station_cameras[row[2]].append(row[1])
            self._station_cameras = station_cameras
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def update_frame_boxes(self):
        select_query = "SELECT frame_list.id, camera_station_join.camera_id, camera_station_join.station_id, frame_list.frame_box " + \
        "FROM camera_station_join " + \
        "INNER JOIN frame_list ON camera_station_join.id=frame_list.cs_id;"
        #self._frame_boxes = {(0,0): FrameBox}
        try:
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchall()
            frame_boxes = {}
            for row in mobile_records:
                box_size = make_tuple("(" + row[3] + ")")
                box_start = box_size[1]
                box_len = (box_size[0][0] - box_size[1][0], box_size[0][1] - box_size[1][1])
                box = FrameBox(start=list(box_start), length=list(box_len), frame_id=row[0])
                frame_boxes[(row[1], row[2])] = box
                #print(make_tuple("(" + row[3] + ")")[0])
            self._frame_boxes = frame_boxes
            print(self._frame_boxes)
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def add_camera(self, camera_string : str):
        try:
            select_query = f"INSERT INTO camera_list(name) VALUES('{camera_string}') RETURNING id;"
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchone()
            result_id = mobile_records[0]
            self._cameras[result_id] = [camera_string]
            self.cameras_modified.emit()
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def remove_camera(self, camera_id : int):
        try:
            select_query = f"DELETE FROM camera_list WHERE id={camera_id};"
            self.cursor.execute(select_query)
            self._cameras.pop(camera_id, None)
            self.cameras_modified.emit()

        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)


    def add_station(self, station_string : str):
        try:
            select_query = f"INSERT INTO station_list(name) VALUES('{station_string}') RETURNING id;"
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchone()
            result_id = mobile_records[0]
            self._stations[result_id] = [station_string]
            self.stations_modified.emit()
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def remove_station(self, station_id : int):
        try:
            select_query = f"DELETE FROM camera_station_join WHERE station_id={station_id};"
            self.cursor.execute(select_query)
            select_query = f"DELETE FROM station_list WHERE id={station_id};"
            self.cursor.execute(select_query)
            self._stations.pop(station_id, None)
            self._station_cameras.pop(station_id, None)
            self._station_exercises.pop(station_id, None)
            self.stations_modified.emit()
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)


    def edit_station(self, station_string, new_name):
        if station_string not in self._stations:
            return
        index = self._stations.index(station_string)
        self._stations.remove(station_string)
        self._stations.insert(index, new_name)
        self._station_cameras[new_name] = self._station_cameras.pop(station_string)
        self._station_exercises[new_name] = self._station_exercises.pop(station_string)
        self.stations_modified.emit()

    def add_camera_to_station(self, station_id : int, camera_id : int):
        try:
            select_query = "INSERT INTO camera_station_join(camera_id, station_id) " + \
                            f"VALUES('{camera_id}', '{station_id}');"
            self.cursor.execute(select_query)
            if station_id not in self._station_cameras:
                self._station_cameras[station_id] = []
            self._station_cameras[station_id].append(camera_id) #self._cameras[exercise_id])
            self.stations_cameras_modified.emit()
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def remove_camera_from_station(self, station_id : int, camera_id : int):
        try:
            select_query = f"DELETE FROM camera_station_join WHERE station_id={station_id} and camera_id={camera_id};"
            self.cursor.execute(select_query)
            self._station_cameras[station_id].remove(camera_id) #self._cameras[exercise_id])
            self.stations_cameras_modified.emit()
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def add_exercise_to_station(self, station_string, exercise_string):
        if station_string not in self._station_exercises:
            self._station_exercises[station_string] = []
        self._station_exercises[station_string].append(exercise_string) #self._exercises[exercise_id])
        self.stations_exercises_modified.emit()

    def remove_exercise_from_station(self, station_string, exercise_string):
        self._station_exercises[station_string].remove(exercise_string) #self._exercises[exercise_id])
        self.stations_exercises_modified.emit()

    def store_frames_to_database(self):
        try:
            for box in self._frame_boxes.values():
                if not box.is_modified:
                    return
                frame_id = box.frame_id
                end_point = (box.start[0] + box.length[0], box.start[1] + box.length[1])
                frame_box_str = f"\'({box.start[0]},{box.start[1]})({end_point[0]},{end_point[1]})\'"
                print(frame_box_str)
                sql_query = \
                "UPDATE frame_list " + \
                f"SET frame_box = {frame_box_str} " + \
                f"WHERE id = {frame_id};"
                self.cursor.execute(sql_query)
                box.is_modified = False
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def add_new_frame(self, camera_id : int, station_id : int):
        try:
            select_query = f"SELECT id FROM camera_station_join WHERE camera_id = {camera_id} and station_id = {station_id}"
            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchone()
            cs_id = mobile_records[0]

            select_query = \
            "INSERT INTO frame_list(cs_id, frame_box) " + \
            f"VALUES('{cs_id}', '((100, 100),(400,400))') " + \
            "RETURNING id;"

            self.cursor.execute(select_query)
            mobile_records = self.cursor.fetchone()
            result_id = mobile_records[0]

            self._frame_boxes[(camera_id, station_id)] = FrameBox(start=[100, 100], length=[300,300], frame_id=result_id)
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)

    def get_cameras(self):
        return self._cameras

    def get_stations(self):
        return self._stations

    def get_exercises(self):
        return self._exercises

    def get_station_cameras(self):
        return self._station_cameras

    def get_station_exercises(self):
        return self._station_exercises

    def get_camera_string(self, index : int) -> str:
        return self._cameras[index][0]

    def get_station_string(self, index : int) -> str:
        return self._stations[index][0]

    def get_frame_boxes(self):
        return self._frame_boxes

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self, data = None):
        super().__init__()
        self.data = data
        self.video_id = 0
        self.start_point = [[230, 5], [280, 25], [280, 25]]
        self.length = [[230, 470], [200, 415], [200, 415]]
        self.box_is_active = False
        self.color1 = (0, 255, 0)
        self.color2 = (255, 0, 0)
        self.countdown = 0
        self.cam_is_busy = False
        self.screen_mode = False
        self.selected_frame = None

        self.cap1 = cv2.VideoCapture("./out1.avi")
        self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.cap2 = cv2.VideoCapture("./out2.avi")
        self.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.cap3 = cv2.VideoCapture("./out3.avi")
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

            #if self.video_id == 0:
            cap = self.cap1

            stations = self.data.get_station_cameras().keys()
            frames = self.data.get_frame_boxes()

            s_points = []
            e_points = []
            selection_index = -1
            for station in stations:
                if (self.video_id, station) in frames:
                    frame_box = frames[(self.video_id, station)]
                    start = frame_box.start
                    end = (start[0] + frame_box.length[0], start[1] + frame_box.length[1])
                    s_points.append(tuple(frame_box.start))
                    e_points.append(end)
                    if self.selected_frame is not None:
                        #print(self.selected_frame)
                        if(frame_box.frame_id == self.selected_frame.frame_id):
                            selection_index = len(s_points) - 1

            #s_points = tuple(self.start_point[0])
            #e_points = (self.start_point[0][0] + self.length[0][0], self.start_point[0][1] + self.length[0][1])
            screen = self.screen1
            # elif self.video_id == 1:
            #     cap = self.cap2
            #     s_point = tuple(self.start_point[1])
            #     e_point = (self.start_point[1][0] + self.length[1][0], self.start_point[1][1] + self.length[1][1])
            #     screen = self.screen2
            # else:
            #     cap = self.cap3
            #     s_point = tuple(self.start_point[2])
            #     e_point = (self.start_point[2][0] + self.length[2][0], self.start_point[2][1] + self.length[2][1])
            #     screen = self.screen3
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
                    for i, s_point in enumerate(s_points):
                        e_point = e_points[i]
                        if i == selection_index:
                            cv_img = cv2.rectangle(cv_img, s_point, e_point, self.color2, 3)
                        else:
                            cv_img = cv2.rectangle(cv_img, s_point, e_point, self.color1, 3)
                if self.countdown > 0:
                    cv2.putText(cv_img,f"{self.countdown}", (320,240), cv2.FONT_HERSHEY_SIMPLEX, 5, 255, thickness=10)
                self.change_pixmap_signal.emit(cv_img)
                time.sleep(0.016)

    def take_screens(self):
        _, self.screen1 = self.cap1.read()
        _, self.screen2 = self.cap2.read()
        _, self.screen3 = self.cap3.read()


class App(Ui_MainWindow, QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.main_window = QMainWindow()
        self.gui = Ui_MainWindow()
        self.gui.setupUi(self.main_window)
        self.setupUi(self.main_window)
        self.disply_width = 640
        self.display_height = 480
        self.image_label.setScaledContents(True)
        self.data = DataManager()

        #Dialogs
        self.station_add_dialog = QDialog()
        self.station_add_ui = StationAddDialogUI()
        self.station_add_ui.setupUi(self.station_add_dialog)
        self.station_edit_dialog = QDialog()
        self.station_edit_ui = StationEditDialogUI()
        self.station_edit_ui.setupUi(self.station_edit_dialog)

        #Fill Data into Gui
        self.overview_mode = 0
        self.configure = ["Camera", "Exercise"]
        self.configure_list.addItems(self.configure)

        self.update_station_list_co()
        self.update_station_list_so()

        # Init Signal/Slots
        self.station_add_dialog.finished.connect(self.station_add_dialog_finished)
        self.station_edit_dialog.finished.connect(self.station_edit_dialog_finished)

        self.station_list_co.itemClicked.connect(self.station_list_co_clicked)
        self.station_list_so.itemClicked.connect(self.station_list_so_clicked)
        self.frame_list.itemClicked.connect(self.frame_list_clicked)
        self.configure_list.itemClicked.connect(self.configure_list_clicked)
        self.camera_list.itemClicked.connect(self.camera_list_clicked)
        self.compute_box_button.clicked.connect(self.compute_box_clicked)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.width_slider.sliderMoved.connect(self.width_slider_moved)
        self.height_slider.sliderMoved.connect(self.height_slider_moved)
        self.width_box.valueChanged.connect(self.width_box_changed)
        self.height_box.valueChanged.connect(self.height_box_changed)
        self.countdown_box.valueChanged.connect(self.countdown_box_changed)
        self.countdown_box.valueChanged.connect(self.countdown_box_changed)
        self.add_suggestion_button.clicked.connect(self.add_suggestion_clicked)
        self.remove_suggestion_button.clicked.connect(self.remove_suggestion_clicked)
        self.add_station_button.clicked.connect(self.add_station)
        self.add_frame_button.clicked.connect(self.add_frame_clicked)
        self.edit_station_button.clicked.connect(self.edit_station)
        self.station_edit_ui.remove_button.clicked.connect(self.remove_station_clicked)

        #Init Signal/Slots data
        self.data.cameras_modified.connect(self.cameras_modified)
        self.data.stations_modified.connect(self.stations_modified)
        self.data.stations_cameras_modified.connect(self.stations_cameras_modified)
        self.data.stations_exercises_modified.connect(self.stations_exercises_modified)

        # Init Threads
        self.thread = VideoThread(self.data)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        self.countdown_thread = QThread()
        self.worker = CountdownThread(5)
        self.worker.moveToThread(self.countdown_thread)
        self.countdown_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.countdown_thread.quit)
        self.worker.finished.connect(self.countdown_finished)
        self.worker.countdown.connect(self.report_countdown)

        self.log_info("Info")
        self.log_warning("Warning")
        self.log_error("Error")

    @pyqtSlot(int)
    def station_add_dialog_finished(self, result):
        if result != 1:
            return
        text = self.station_add_ui.sation_name_edit.text()
        if not text:
            self.log_error("Empty Strings are not allowed")
            return
        self.data.add_station(text)
        self.log_info(f"Added new Station: {text}")

    @pyqtSlot(int)
    def station_edit_dialog_finished(self, result):
        if result != 1:
            return
        text = self.station_edit_ui.sation_name_edit.text()
        if not text:
            self.log_error("Empty Strings are not allowed")
            return
        selected_station = self.station_list_so.selectedItems()[0]
        #print(selected_station.text())
        self.log_info(f"Changed station \"{selected_station.text()}\" to \"{text}\"")
        self.data.edit_station(selected_station.text(), text)

    @pyqtSlot()
    def add_station(self):
        self.station_add_dialog.show()

    @pyqtSlot()
    def edit_station(self):
        selected_station = self.station_list_so.selectedItems()
        if not selected_station:
            self.log_warning("Select a Station first")
            return
        selected_station = selected_station[0]
        self.station_edit_ui.sation_name_edit.setText(selected_station.text())
        self.station_edit_dialog.show()

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

    @pyqtSlot()
    def set_slider_values(self):
        if not self.thread.box_is_active:
            return

        frame = self.thread.selected_frame
        if frame is None:
            return

        bbox = frame.start + frame.length #self.thread.start_point[index] + self.thread.length[index]
        width_center = bbox[0] + (bbox[2] / 2)
        height_center = bbox[1] + (bbox[3] / 2)
        slider1_value = int((width_center * 100) / self.disply_width)
        slider2_value = int((height_center * 100) / self.display_height)
        self.width_slider.setValue(slider1_value)
        self.height_slider.setValue(slider2_value)
        self.width_box.setValue(frame.length[0])
        self.height_box.setValue(frame.length[1])

    @pyqtSlot()
    def width_slider_moved(self):
        if not self.thread.box_is_active:
            return

        frame = self.thread.selected_frame
        if frame is None:
            return
        print(frame)
        bbox = frame.start + frame.length #self.thread.start_point[index] + self.thread.length[index]
        half_width = bbox[2] / 2
        start = (self.width_slider.value() * (self.disply_width / 100)) - half_width
        frame.start[0] = int(start)
        frame.is_modified = True

    @pyqtSlot()
    def height_slider_moved(self):
        if not self.thread.box_is_active:
            return

        frame = self.thread.selected_frame
        if frame is None:
            return

        bbox = frame.start + frame.length #self.thread.start_point[index] + self.thread.length[index]
        half_height = bbox[3] / 2
        start = (self.height_slider.value() * (self.display_height / 100)) - half_height
        frame.start[1] = int(start)
        frame.is_modified = True

    @pyqtSlot(int)
    def width_box_changed(self, value):
        if not self.thread.box_is_active:
            return

        frame = self.thread.selected_frame
        if frame is None:
            return

        frame.length[0] = value
        frame.is_modified = True
        self.set_slider_values()

    @pyqtSlot(int)
    def height_box_changed(self, value):
        if not self.thread.box_is_active:
            return

        frame = self.thread.selected_frame
        if frame is None:
            return

        frame.length[1] = value
        frame.is_modified = True
        self.set_slider_values()

    @pyqtSlot(int)
    def countdown_box_changed(self, value):
        self.worker.countdown_value = value

    @pyqtSlot(QListWidgetItem)
    def station_list_co_clicked(self, item):
        self.update_camera_list(item)
        self.update_frame_list()

    @pyqtSlot(QListWidgetItem)
    def station_list_so_clicked(self, item):
        self.update_setting_and_suggestion_list(item)

    @pyqtSlot(QListWidgetItem)
    def configure_list_clicked(self, item):
        self.setting_label.setText(item.text() + "s")
        self.overview_mode = self.configure.index(item.text())
        self.update_setting_and_suggestion_list()

    @pyqtSlot(QListWidgetItem)
    def camera_list_clicked(self, item):
        camera_index = int(item.data(Qt.UserRole))
        self.thread.video_id = camera_index
        self.update_frame_list()

    @pyqtSlot(QListWidgetItem)
    def frame_list_clicked(self, item):
        frame_index = int(item.data(Qt.UserRole))
        boxes = self.data.get_frame_boxes()
        for box in boxes.values():
            if box.frame_id == frame_index:
                self.thread.selected_frame = box
                break
        self.set_slider_values()

    @pyqtSlot()
    def add_suggestion_clicked(self):
        selected_station = self.station_list_so.selectedItems()
        if not selected_station:
            self.log_warning("Select a Station first")
            return
        selected_station = selected_station[0]
        items = self.suggestion_list.selectedItems()

        if items:
            item = items[0]
            if self.overview_mode == 0:
                camera_index = int(item.data(Qt.UserRole))
                station_index = int(selected_station.data(Qt.UserRole))
                self.data.add_camera_to_station(station_index, camera_index)
            else:
                self.data.add_exercise_to_station(selected_station.text(), item.text())

    @pyqtSlot()
    def remove_suggestion_clicked(self):
        selected_station = self.station_list_so.selectedItems()
        if not selected_station:
            self.log_warning("Select a Station first")
            return
        selected_station = selected_station[0]
        items = self.setting_list.selectedItems()

        if items:
            item = items[0]
            if self.overview_mode == 0:
                camera_index = int(item.data(Qt.UserRole))
                station_index = int(selected_station.data(Qt.UserRole))
                self.data.remove_camera_from_station(station_index, camera_index)
            else:
                self.data.remove_exercise_from_station(selected_station.text(), item.text())


    @pyqtSlot()
    def compute_box_clicked(self):
        self.countdown_thread.start()

    @pyqtSlot()
    def save_button_clicked(self):
        self.data.store_frames_to_database()
        self.data.connection.commit()
        self.log_info("Data stored to database")

    @pyqtSlot()
    def remove_station_clicked(self):
        selected_station = self.station_list_so.selectedItems()
        if not selected_station:
            self.log_warning("Select a Station first")
            return
        selected_station = selected_station[0]
        station_index = int(selected_station.data(Qt.UserRole))
        self.data.remove_station(station_index)
        self.station_edit_dialog.close()

    @pyqtSlot()
    def add_frame_clicked(self):
        selected_items = self.station_list_co.selectedItems()
        if not selected_items:
            return
        selected_station = selected_items[0]
        station_index = int(selected_station.data(Qt.UserRole))


        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            return
        selected_camera = selected_items[0]
        camera_index = int(selected_camera.data(Qt.UserRole))

        self.data.add_new_frame(camera_index, station_index)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        convert_to_qt_format = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = convert_to_qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(pixmap)

    def show(self):
        self.main_window.show()
        sys.exit(self.app.exec_())

    def log_info(self, msg):
        self.log_textbox.setTextColor(QColor(0,0,0))
        self.log_textbox.append(f"[Info] {msg}")

    def log_error(self, msg):
        self.log_textbox.setTextColor(QColor(235, 64, 52))
        self.log_textbox.append(f"[ERROR] {msg}")

    def log_warning(self, msg):
        self.log_textbox.setTextColor(QColor(214, 147, 39))
        self.log_textbox.append(f"[WARNING] {msg}")

    ### Gui Update Functions ###
    ### Update Functions are not allowed to modify the data manager (update loop) ###
    ### Only Update Gui elements
    @pyqtSlot()
    def cameras_modified(self):
        self.update_setting_and_suggestion_list()
        self.update_camera_list()

    @pyqtSlot()
    def stations_modified(self):
        self.update_setting_and_suggestion_list()
        self.update_station_list_so()
        self.update_station_list_co()

    @pyqtSlot()
    def stations_cameras_modified(self):
        self.update_setting_and_suggestion_list()
        self.update_station_list_co()

    @pyqtSlot()
    def stations_exercises_modified(self):
        self.update_setting_and_suggestion_list()

    def update_setting_and_suggestion_list(self, selected_station = None):
        if selected_station is None:
            selected_station = self.station_list_so.selectedItems()
            if not selected_station:
                #self.log_warning("Select a Station first")
                return
            selected_station = selected_station[0]

        index = self.overview_mode
        self.setting_list.clear()
        self.suggestion_list.clear()

        if index == 0:
            station_cameras = self.data.get_station_cameras()
            cameras = self.data.get_cameras().keys()
            camera_ids = []
            station_index = int(selected_station.data(Qt.UserRole))
            print(station_index)
            if station_index in station_cameras:
                camera_ids = station_cameras[station_index]
                items = {i : [self.data.get_camera_string(i)] for i in camera_ids}
                insert_dict_into_widget(self.setting_list, items)
                #self.setting_list.addItems(items)
            suggestion = {i : [self.data.get_camera_string(i)] for i in cameras if i not in camera_ids}
            insert_dict_into_widget(self.suggestion_list, suggestion)
            #self.suggestion_list.addItems(suggestion)
        else:
            station_exercises = self.data.get_station_exercises()
            exercises = self.data.get_exercises()
            items = []
            if selected_station.text() in station_exercises:
                items = station_exercises[selected_station.text()]
            suggestion = [i for i in exercises if i not in items]
            self.setting_list.addItems(items)
            self.suggestion_list.addItems(suggestion)

    def update_camera_list(self, selected_station = None):
        self.camera_list.clear()
        if selected_station is None:
            selected_items = self.station_list_co.selectedItems()
            if not selected_items:
                return
            selected_station = selected_items[0]

        station_cameras = self.data.get_station_cameras()
        station = int(selected_station.data(Qt.UserRole))

        if station in station_cameras:
            cameras = {i : [self.data.get_camera_string(i)] for i in station_cameras[station]}
            insert_dict_into_widget(self.camera_list, cameras)
            #self.camera_list.addItems(cameras)

    def update_station_list_co(self):
        self.station_list_co.clear()
        station_cameras = self.data.get_station_cameras()
        stations_with_cam = {i : [self.data.get_station_string(i)] for i in station_cameras}
        insert_dict_into_widget(self.station_list_co, stations_with_cam)
        #self.station_list_co.addItems(stations_with_cam)

    def update_station_list_so(self):
        self.station_list_so.clear()
        stations = self.data.get_stations()
        insert_dict_into_widget(self.station_list_so, stations)

    def update_frame_list(self, selected_camera = None):
        self.frame_list.clear()
        self.thread.selected_frame = None
        # selected_items = self.station_list_co.selectedItems()
        # if not selected_items:
        #     return
        # selected_station = selected_items[0]
        if selected_camera is None:
            selected_items = self.camera_list.selectedItems()
            if not selected_items:
                return
            selected_camera = selected_items[0]

        stations = self.data.get_station_cameras().keys()
        frames = self.data.get_frame_boxes()
        camera_index = int(selected_camera.data(Qt.UserRole))

        frame_dict = {}
        for station in stations:
            if (camera_index, station) in frames:
                frame_string = f"Frame Station {station}"
                frame_id = frames[(camera_index, station)].frame_id
                frame_dict[frame_id] = [frame_string]

        insert_dict_into_widget(self.frame_list, frame_dict)

if __name__=="__main__":
    a = App()
    a.show()
