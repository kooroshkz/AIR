from dotenv import load_dotenv
import napari
from src.napari_image_filtering_interface import napari_experimental_provide_dock_widget


def main():
                                """
                                Main entry point to launch Napari
                                """
                                # Initialize .env
                                load_dotenv()
                                # Create a new Napari viewer
                                viewer = napari.Viewer()

                                # Get the dock widget factory
                                dock_widget_factory = napari_experimental_provide_dock_widget()

                                # Add the dock widget to the viewer
                                viewer.window.add_dock_widget(
                                    dock_widget_factory(viewer),
                                    area='right',
                                    name='Image Filters'
                                )

                                # Start the Napari event loop
                                napari.run()


if __name__ == "__main__":
    main()
