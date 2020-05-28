import os
import sys

from Qt import QtWidgets, QtCore

from .pipeline import (
    publish,
    launch_workfiles_app,
    reload_pipeline
    )

from avalon.tools import (
    creator,
    loader,
    sceneinventory,
    libraryloader
)

def load_stylesheet():
    path = os.path.join(os.path.dirname(__file__), "menu_style.qss")
    if not os.path.exists(path):
        print("Unable to load stylesheet, file not found in resources")
        return ""

    with open(path, "r") as file_stream:
        stylesheet = file_stream.read()
    return stylesheet


class Spacer(QtWidgets.QWidget):
    def __init__(self, height, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setFixedHeight(height)

        real_spacer = QtWidgets.QWidget(self)
        real_spacer.setObjectName("Spacer")
        real_spacer.setFixedHeight(height)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 11, 0, 0)
        layout.addWidget(real_spacer)

        self.setLayout(layout)


class PypeMenu(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setObjectName("PypeMenu")

        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowStaysOnTopHint
        )

        self.setWindowTitle("Pype")
        workfiles_btn = QtWidgets.QPushButton("Workfiles", self)
        create_btn = QtWidgets.QPushButton("Create", self)
        publish_btn = QtWidgets.QPushButton("Publish", self)
        load_btn = QtWidgets.QPushButton("Load", self)
        inventory_btn = QtWidgets.QPushButton("Inventory", self)
        rename_btn = QtWidgets.QPushButton("Rename", self)
        set_colorspace_btn = QtWidgets.QPushButton(
            "Set colorspace from presets", self
        )
        reset_resolution_btn = QtWidgets.QPushButton(
            "Reset Resolution from peresets", self
        )
        reload_pipeline_btn = QtWidgets.QPushButton("Reload pipeline", self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)

        layout.addWidget(workfiles_btn)
        layout.addWidget(create_btn)
        layout.addWidget(publish_btn)
        layout.addWidget(load_btn)
        layout.addWidget(inventory_btn)

        layout.addWidget(Spacer(11, self))

        layout.addWidget(rename_btn)
        layout.addWidget(set_colorspace_btn)
        layout.addWidget(reset_resolution_btn)

        layout.addWidget(Spacer(11, self))

        layout.addWidget(reload_pipeline_btn)

        self.setLayout(layout)

        workfiles_btn.clicked.connect(self.on_workfile_clicked)
        create_btn.clicked.connect(self.on_create_clicked)
        publish_btn.clicked.connect(self.on_publish_clicked)
        load_btn.clicked.connect(self.on_load_clicked)
        inventory_btn.clicked.connect(self.on_inventory_clicked)
        rename_btn.clicked.connect(self.on_rename_clicked)
        set_colorspace_btn.clicked.connect(self.on_set_colorspace_clicked)
        reset_resolution_btn.clicked.connect(self.on_reset_resolution_clicked)
        reload_pipeline_btn.clicked.connect(self.on_reload_pipeline_clicked)

    def on_workfile_clicked(self):
        print("Clicked Workfile")
        launch_workfiles_app()

    def on_create_clicked(self):
        print("Clicked Create")
        creator.show()

    def on_publish_clicked(self):
        print("Clicked Publish")
        publish(None)

    def on_load_clicked(self):
        print("Clicked Load")
        loader.show(use_context=True)

    def on_inventory_clicked(self):
        print("Clicked Inventory")
        sceneinventory.show()

    def on_rename_clicked(self):
        print("Clicked Rename")

    def on_set_colorspace_clicked(self):
        print("Clicked Set Colorspace")

    def on_reset_resolution_clicked(self):
        print("Clicked Reset Resolution")

    def on_reload_pipeline_clicked(self):
        print("Clicked Reload Pipeline")
        reload_pipeline()


def launch_pype_menu():
    app = QtWidgets.QApplication(sys.argv)

    pype_menu = PypeMenu()

    stylesheet = load_stylesheet()
    pype_menu.setStyleSheet(stylesheet)

    pype_menu.show()

    sys.exit(app.exec_())
