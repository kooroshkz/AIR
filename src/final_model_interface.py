from cv2.dnn import Model
import numpy as np
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)

from src.global_model_state import GlobalModelState
from src.workflows import Pipeline

from cellposeUI.__main__ import main

class ModelInterface(QWidget):
    """
    Widget for launching & interacting with the cellpose UI, which is used to finetune the final model for the pipeline
    """

    preprocessing_pipeline: Pipeline | None = None
    # true if a pipeline is attached to the current cellpose UI process
    pipeline_attached = False

    def __init__(self, viewer, filter_widget):
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget
        self.launch_btn = QPushButton("prepare model")  # the final stage

        self.setup_ui()

        # the QMainWindow object representing the Cellpose UI
        # this object has not yet been initialized
        self.main_window, self.cellpose_logger = main(self)
        self.is_rendered = False

    def setup_ui(self):
        """Configure the widget's user interface."""

        self.launch_btn.setStyleSheet(
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
        self.launch_btn.clicked.connect(self._launch_cellpose_ui)

        layout = QHBoxLayout()
        layout.addWidget(self.launch_btn)

        self.setLayout(layout)

    def _launch_cellpose_ui(self) -> None:
        # get the pipeline which final model will be attached to (if a pipeline
        # is selected)
        ModelInterface.preprocessing_pipeline = self.filter_widget.workflow.get_pipelines()

        # 3 options, user just closed it, user picked to launch with no
        # pipeline, or user selected pipeline
        if ModelInterface.preprocessing_pipeline is None:
            return
        elif ModelInterface.preprocessing_pipeline.name == "":
            self.filter_widget.add_to_chat(
                f"[Info] launching cellpose with no pipeline attached")
            ModelInterface.pipeline_attached = False
            ModelInterface.preprocessing_pipeline = None
        else:
            self.filter_widget.add_to_chat(
                f"[Info] launching cellpose with pipeline {
                    ModelInterface.preprocessing_pipeline}")
            ModelInterface.pipeline_attached = True
            ModelInterface.preprocessing_pipeline.final_stage = GlobalModelState()

        # launches cellpose with the currently selected napari layer
        try:
            self.main_window.__init__(None, self.cellpose_logger)
            self.is_rendered = True
        #when cellpose launches with no image as it does in this case it raises a NameError
        except NameError as ne:
            pass 
        except Exception as e:
            self.filter_widget.chat_widget.add_to_chat(
                "[Error] Could not launch cellpose UI")
            self.filter_widget.chat_widget.add_to_chat(f"[Error] {e}")

def set_MIPipeline_attr(name : str, val : any):
    try:
        from src.final_model_interface import ModelInterface
        if ModelInterface.preprocessing_pipeline is not None:
                ModelInterface.preprocessing_pipeline.final_stage.set_attr(name, val)
        return None
    except Exception as e:
        print(f"[Error] {e}")
