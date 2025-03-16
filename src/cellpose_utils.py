from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np

def masks_to_segmentation(image: np.ndarray):
    # converts segmented image into a transparent layer where each cell segmentation is given a new color
    # returns the new layer, and the number of segmented regions

    cmap = plt.get_cmap('viridis')
    img = cmap(image)
    img[image == 0] = np.array([0, 0, 0, 0])
    return img
