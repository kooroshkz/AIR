from functools import partial
import pickle
from importlib.metadata import files
from typing import Callable, Dict, List
from napari._qt.widgets.qt_progress_bar import QtLabeledProgressBar
from napari._qt.widgets.qt_viewer_dock_widget import QtCustomTitleBar
from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QTextEdit
)
import json

#pipeline class so that the name can stay coupled to the original pipeline system without needing a rewrite
class Pipeline():
    def __init__(self) -> None:
        self.workflow : Dict[int, Callable] = {}
        self.name : str = ""
    def __len__(self):
        return len(self.workflow)
    def __getitem__(self, key):
        return self.workflow[key]
    def __setitem__(self, key, value):
        self.workflow[key] = value
    def __delitem__(self, key):
        del self.workflow[key]
    def __contains__(self, key):
        return key in self.workflow
    def __iter__(self):
        return iter(self.workflow)

class WorkflowWidget(QWidget):
    """
    Widget for interacting with different workflows
    A workflow is just a recorded sequence of events, which biologists can use to build pipelines
    """

    def __init__(self, viewer, filter_widget):
        """
        Initialize the chat widget, available commands, and UI.
        """
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget

        self.main_wf_layout = QVBoxLayout()  # the main top level widget for workflows
        self.buttons = QHBoxLayout()  # buttons for interacting with workflows
        self.recording_wf_layout = QVBoxLayout()  # ongoing recordings of workflows
        self.saved_wf_layout = QVBoxLayout()  # already saved workflows
        self.wf_name_menu = QHBoxLayout()  # menu for choosing the wf name

        self.setup_ui()
        self.recording = False

        # the recorded workflow, all actions get recorded here
        # stored as dict for automatic index management when removing or adding
        # items to the workflow
        self.wf_idx = 0
        self.current_workflow : Pipeline = Pipeline()
        self.workflows: Dict[int, Pipeline] = {}

    def setup_ui(self):
        """Configure the widget's user interface."""

        record_workflow_btn = QPushButton("record")
        record_workflow_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0255b3;
            }
            """
        )
        record_workflow_btn.clicked.connect(self.start_workflow)

        # stop recording the workflow
        stop_workflow_btn = QPushButton("stop")
        stop_workflow_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0255b3;
            }
            """
        )
        stop_workflow_btn.clicked.connect(self.stop_recording_wf)

        save_workflow_btn = QPushButton("save")
        save_workflow_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0255b3;
            }
            """
        )
        save_workflow_btn.clicked.connect(self.save_workflow)

        wf_name_btn = QPushButton("set name")
        wf_name_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0255b3;
            }
            """
        )
        wf_name_btn.clicked.connect(self.set_wf_name)

        self.buttons.addWidget(record_workflow_btn)
        self.buttons.addWidget(stop_workflow_btn)
        self.buttons.addWidget(wf_name_btn)
        self.buttons.addWidget(save_workflow_btn)

        import_wf_btn = QPushButton("Import workflow")
        import_wf_btn.clicked.connect(self.import_wf)

        self.main_wf_layout.addWidget(import_wf_btn)
        self.main_wf_layout.addLayout(self.buttons)
        self.main_wf_layout.addLayout(self.recording_wf_layout)
        self.main_wf_layout.addLayout(self.saved_wf_layout)

        self.setLayout(self.main_wf_layout)

    def start_workflow(self):
        if not self.recording:
            self.reset()
            self.recording = True
            self.recording_wf_layout.addWidget(
                QLabel("Recording new workflow"))
            self.recording_wf_layout.addWidget(
                QLabel("press on event to delete"))

    def stop_recording_wf(self):
        self.recording = False

    def save_workflow(self):
        # save the current pipeline state
        if not self._check_wf_exists("Cannot save empty workflow"):
            return

        if self.current_workflow.name == "":
            self.current_workflow.name = f"workflow {len(self.workflows)}"

        self.workflows[len(self.workflows)] = self.current_workflow
        wf_index = len(self.workflows) - 1

        wf_area = QHBoxLayout()
        wf_button = QPushButton(self.current_workflow.name)
        wf_delete_button = QPushButton("delete")
        wf_export_button = QPushButton("export to file")

        wf_button.clicked.connect(partial(self.apply_wf, wf_index))
        wf_delete_button.clicked.connect(partial(self.remove_wf, wf_area))
        wf_export_button.clicked.connect(partial(self.export_wf, wf_index))

        wf_area.addWidget(wf_button)
        wf_area.addWidget(wf_delete_button)
        wf_area.addWidget(wf_export_button)
        self.saved_wf_layout.addLayout(wf_area)

        self.recording = False
        self.reset()

    def export_wf(self, wf_index):
        assert wf_index in self.workflows
        file_path, _ = QFileDialog.getSaveFileName(self, "save to file", ".")
        if not file_path:
            return

        wf = self.workflows[wf_index]

        with open(file_path, 'wb') as fp:
            pickle.dump(wf, fp)
        self.filter_widget.chat_widget.add_to_chat(f"[Update] saved workflow {wf.name} to file: {file_path}")

    def import_wf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "open exported pipeline", ".")
        if file_path:
            try:
                with open(file_path, 'rb') as fp:
                    new_pipeline = pickle.load(fp)
                    if not isinstance(new_pipeline, Pipeline):
                        self.filter_widget.chat_widget.add_to_chat(f"[Error] did not recognize {file_path} as a valid pipeline")
                    self.current_workflow = new_pipeline
                    self.save_workflow()
            except Exception as e:
                    self.filter_widget.chat_widget.add_to_chat(f"[Error] {e}")

    def remove_wf(self, wf_area):
        while wf_area.count():
            item = wf_area.takeAt(0)
            if item is not None:
                widget = item.widget()
            else:
                continue

            # Ensure the widget is removed and detached
            if widget is not None:
                wf_area.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

        wf_area.parentWidget().adjustSize()
        wf_area.setParent(None)
        wf_area.deleteLater()
        self.repaint()  # Ensure the UI redraws fully

    def add_event_to_workflow(self, event: Callable):
        if self.recording:
            self.current_workflow[len(self.current_workflow)] = event
            lb = QPushButton(f"event {len(self)}: {event.__name__}")
            lb.setStyleSheet(
                """
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #FF0000;
            }
            """
            )
            lb.clicked.connect(
                partial(
                    self.remove_event_wf, len(
                        self.current_workflow) - 1, lb))
            self.recording_wf_layout.addWidget(lb)

    def remove_event_wf(self, pos: int, widget: QPushButton):
        assert len(self.current_workflow) != 0
        del self.current_workflow[pos]
        self.recording_wf_layout.removeWidget(widget)
        widget.setParent(None)
        widget.deleteLater()

    def set_wf_name(self):
        prompt = QInputDialog()
        text, ok = prompt.getText(None, "Set pipeline name", "new name")
        if ok:
            self.current_workflow.name = text

    def _check_wf_exists(self, message : str):
        """Returns true if there are any actions in the current pipeline"""
        if len(self.current_workflow) == 0:
            self.filter_widget.chat_widget.add_to_chat(
                f"[Error] {message}")
            return False
        return True

    def apply_wf(self, wf_index: int):
        wf = self.workflows[wf_index]
        for filter_event in wf:
            self.filter_widget._apply_filter(wf[filter_event])

    def reset(self):
        """resets the current workflow pipeline"""
        self.current_workflow = Pipeline()
        self.reset_workflow_ui()

    def reset_workflow_ui(self):
        # Remove widgets from the layout immediately
        while self.recording_wf_layout.count():
            item = self.recording_wf_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
            else:
                continue

            # Ensure the widget is removed and detached
            if widget is not None:
                self.recording_wf_layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

        # Force the layout and UI to update
        self.recording_wf_layout.update()
        self.recording_wf_layout.parentWidget().adjustSize()
        self.repaint()  # Ensure the UI redraws fully

    def __len__(self):
        return len(self.current_workflow)
