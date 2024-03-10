# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 15:29:00 2024

@author: NGPF
"""

import sys
import numpy as np
import copy
from PIL import Image, ImageQt
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QWidget, QFileDialog, QLabel, QGroupBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.orig_image = None
        self.orig_image_dir = None
        self.new_image = None
        self.new_image_dir = None

        self.setWindowTitle("IG POST RESIZER")
        self.setFixedSize(QSize(1200, 600))

        base_widget = QWidget(self)
        self.setCentralWidget(base_widget)

        main_h_layout = QHBoxLayout()
        function_v_widget = QWidget()
        function_v_widget.setFixedWidth(150)
        function_v_layout = QVBoxLayout()

        resize_group = QGroupBox("Resize")
        resize_v_layout = QVBoxLayout()
        self.quick_resize_option = QComboBox()
        self.quick_resize_option.addItems(["", "Square (1:1)", "Landscape (1.91:1)", "Portrait (4:5)"])
        self.quick_resize_option.setCurrentText("")
        convert_button = QPushButton("Convert")
        convert_button.clicked.connect(self.convert_to_new)
        resize_v_layout.addWidget(self.quick_resize_option)
        resize_v_layout.addWidget(convert_button)
        resize_group.setLayout(resize_v_layout)

        io_group = QGroupBox("File")
        io_v_layout = QVBoxLayout()
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.browse_image)
        #export_option = QComboBox()
        #export_option.addItems(["PNG", "JPG"])
        #export_option.setCurrentText("PNG")
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.save_image)
        io_v_layout.addWidget(import_button)
        #io_v_layout.addWidget(export_option)
        io_v_layout.addWidget(export_button)
        io_group.setLayout(io_v_layout)

        function_v_layout.addWidget(io_group)
        function_v_layout.addWidget(resize_group)
        function_v_widget.setLayout(function_v_layout)

        old_image_group = QGroupBox("Original")
        old_image_v_layout = QVBoxLayout()
        self.old_image_pixmap = QLabel()
        self.old_image_size_label = QLabel()
        self.old_image_dir_label = QLabel()
        old_image_v_layout.addWidget(self.old_image_dir_label)
        old_image_v_layout.addWidget(self.old_image_pixmap)
        old_image_v_layout.addWidget(self.old_image_size_label)
        old_image_group.setLayout(old_image_v_layout)

        new_image_group = QGroupBox("Resized")
        new_image_v_layout = QVBoxLayout()
        self.new_image_pixmap = QLabel()
        self.new_image_size_label = QLabel()
        self.new_image_dir_label = QLabel()
        new_image_v_layout.addWidget(self.new_image_dir_label)
        new_image_v_layout.addWidget(self.new_image_pixmap)
        new_image_v_layout.addWidget(self.new_image_size_label)
        new_image_group.setLayout(new_image_v_layout)

        main_h_layout.addWidget(function_v_widget)
        main_h_layout.addWidget(old_image_group)
        main_h_layout.addWidget(new_image_group)
        base_widget.setLayout(main_h_layout)

    def set_pixmap_from_array(self, obj, image_arr):
        qimage = QImage(image_arr, image_arr.shape[1], image_arr.shape[0], QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(qimage)
        qpixmap = qpixmap.scaled(450, 600, Qt.KeepAspectRatio)
        obj.setPixmap(qpixmap)

    def browse_image(self):
        support_file_format = ["png", "PNG", "jpg", "JPG"]
        open_file = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;PNG (*.png;*.PNG);;JPEG (*.jpg;*.JPG)")[0]
        if open_file[-3:] in support_file_format:
            self.orig_image_dir = open_file
            self.orig_image = self.image_loader(self.orig_image_dir)
            self.set_pixmap_from_array(self.old_image_pixmap, self.orig_image)
            self.old_image_size_label.setText(f"Size: {self.orig_image.shape[1]} x {self.orig_image.shape[0]}")
            self.old_image_dir_label.setText(f"{self.orig_image_dir}")
        elif open_file == "":
            pass
        else:
            return

    def save_image(self):
        save_file = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;PNG (*.png;*.PNG);;JPEG (*.jpg;*.JPG)")[0]
        self.new_image_dir = save_file
        image_to_save = copy.deepcopy(self.new_image)
        image_to_save = image_to_save.astype(np.uint8)
        image_to_save_pil = Image.fromarray(image_to_save)
        image_to_save_pil.save(self.new_image_dir)

    def image_loader(self, image_dir):
        return np.array(Image.open(image_dir))

    def convert_to_new(self):
        if self.orig_image is not None:
            self.new_image = self.image_quick_resize(self.orig_image, str(self.quick_resize_option.currentText()))
            self.set_pixmap_from_array(self.new_image_pixmap, self.new_image)
            self.new_image_size_label.setText(f"Size: {self.new_image.shape[1]} x {self.new_image.shape[0]}")
            #self.new_image_dir_label.setText(f"{self.new_image_dir}")

    def get_image_aspect_ratio(self, image_arr):
        image_ratio_orig_height = image_arr.shape[0]
        image_ratio_orig_horizontal = image_arr.shape[1]
        if image_ratio_orig_height == image_ratio_orig_horizontal:
            return (1.0, 1.0)
        elif image_ratio_orig_height > image_ratio_orig_horizontal:
            return (1, image_ratio_orig_height / image_ratio_orig_horizontal)
        elif image_ratio_orig_horizontal > image_ratio_orig_height:
            return (image_ratio_orig_horizontal / image_ratio_orig_height, 1)
        else:
            return

    def image_quick_resize(self, image_arr, resize_option):
        orig_image_ratio = self.get_image_aspect_ratio(image_arr)
        orig_image_shape = image_arr.shape
        new_image_ratio = None
        if resize_option == "Square (1:1)":
            new_image_ratio = (1.0, 1.0)
        elif resize_option == "Landscape (1.91:1)":
            new_image_ratio = (1.91, 1.0)
        elif resize_option == "Portrait (4:5)":
            new_image_ratio = (4.0, 5.0)
        else:
            new_image_ratio = orig_image_ratio

        # Horizontal-vertical ratio
        new_h_v_ratio = new_image_ratio[0] / new_image_ratio[1]
        original_h_v_ratio = orig_image_ratio[0] / orig_image_ratio[1]
        modify_ratio = round(new_h_v_ratio / original_h_v_ratio, 5)

        # if the original ratio is already as expected, return the original image
        if new_h_v_ratio == original_h_v_ratio:
            return image_arr
        # The new ratio should be wider than original --> Add padding horizontally
        elif new_h_v_ratio > original_h_v_ratio:
            new_width_half = round((round(orig_image_shape[1] * modify_ratio) - orig_image_shape[1]) / 2)
            npad = ((0, 0), (new_width_half, new_width_half), (0, 0))
            new_image_arr = np.pad(image_arr, npad, mode='constant', constant_values=0)
            return new_image_arr
        # The new image should be taller than original --> Add padding vertically
        elif original_h_v_ratio > new_h_v_ratio:
            new_height_half = round((round(orig_image_shape[0] / modify_ratio) - orig_image_shape[0]) / 2)
            npad = ((new_height_half, new_height_half), (0, 0), (0, 0))
            new_image_arr = np.pad(image_arr, npad, mode='constant', constant_values=0)
            return new_image_arr
        else:
            return


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()