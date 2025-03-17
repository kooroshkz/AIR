"""
Copyright © 2023 Howard Hughes Medical Institute, Authored by Carsen Stringer and Marius Pachitariu.
"""

from .gui import gui3d, gui
GUI_ENABLED = True


# settings re-grouped a bit
def main(attached_model_interface):
    main_window, logger = gui.run(attached_model_interface)
    return main_window, logger
