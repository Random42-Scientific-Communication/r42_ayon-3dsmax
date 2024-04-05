import os
import platform
import subprocess
from string import Formatter

import ayon_api

from ayon_core.pipeline import (
    Anatomy,
    LauncherAction,
)
from ayon_core.pipeline.template_data import get_template_data


class OpenTaskPath(LauncherAction):
    name = "open_task_path"
    label = "Explore here"
    icon = "folder-open"
    order = 500

    def is_compatible(self, session):
        """Return whether the action is compatible with the session"""
        return bool(session.get("AYON_FOLDER_PATH")) and bool(session.get("AYON_TASK_NAME"))

    def process(self, session, **kwargs):
        from qtpy import QtCore, QtWidgets

        project_name = session["AYON_PROJECT_NAME"]
        folder_path = session["AYON_FOLDER_PATH"]
        task_name = session.get("AYON_TASK_NAME", None)

        path = self._get_workdir(project_name, folder_path, task_name)
        if not path:
            return

        app = QtWidgets.QApplication.instance()
        ctrl_pressed = QtCore.Qt.ControlModifier & app.keyboardModifiers()
        if ctrl_pressed:
            # Copy path to clipboard
            self.copy_path_to_clipboard(path)
        else:
            self.open_in_explorer(path)

    def _find_first_filled_path(self, path):
        if not path:
            return ""

        fields = set()
        for item in Formatter().parse(path):
            _, field_name, format_spec, conversion = item
            if not field_name:
                continue
            conversion = "!{}".format(conversion) if conversion else ""
            format_spec = ":{}".format(format_spec) if format_spec else ""
            orig_key = "{{{}{}{}}}".format(
                field_name, conversion, format_spec)
            fields.add(orig_key)

        for field in fields:
            path = path.split(field, 1)[0]
        return path

    def _get_workdir(self, project_name, folder_path, task_name):
        project_entity = ayon_api.get_project(project_name)
        folder_entity = ayon_api.get_folder_by_path(project_name, folder_path)
        task_entity = ayon_api.get_task_by_name(
            project_name, folder_entity["id"], task_name
        )

        data = get_template_data(project_entity, folder_entity, task_entity)

        anatomy = Anatomy(project_name)
        workdir = anatomy.templates_obj["work"]["folder"].format(data)

        # Remove any potential un-formatted parts of the path
        valid_workdir = self._find_first_filled_path(workdir)

        # Path is not filled at all
        if not valid_workdir:
            raise AssertionError("Failed to calculate workdir.")

        # Normalize
        valid_workdir = os.path.normpath(valid_workdir)
        if os.path.exists(valid_workdir):
            return valid_workdir

        data.pop("task", None)
        workdir = anatomy.templates_obj["work"]["folder"].format(data)
        valid_workdir = self._find_first_filled_path(workdir)
        if valid_workdir:
            # Normalize
            valid_workdir = os.path.normpath(valid_workdir)
            if os.path.exists(valid_workdir):
                return valid_workdir
        raise AssertionError("Folder does not exist yet.")

    @staticmethod
    def open_in_explorer(path):
        platform_name = platform.system().lower()
        if platform_name == "windows":
            args = ["start", path]
        elif platform_name == "darwin":
            args = ["open", "-na", path]
        elif platform_name == "linux":
            args = ["xdg-open", path]
        else:
            raise RuntimeError(f"Unknown platform {platform.system()}")
        # Make sure path is converted correctly for 'os.system'
        os.system(subprocess.list2cmdline(args))

    @staticmethod
    def copy_path_to_clipboard(path):
        from qtpy import QtWidgets

        path = path.replace("\\", "/")
        print(f"Copied to clipboard: {path}")
        app = QtWidgets.QApplication.instance()
        assert app, "Must have running QApplication instance"

        # Set to Clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(os.path.normpath(path))
