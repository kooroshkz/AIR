import matplotlib.pyplot as plt
import numpy as np

def apply_colormap(value, max_value):
    if value == 0: #cmaps dont return 0,0,0,0 from 0
        return np.array([0.0, 0.0, 0.0, 0.0])

    normalized_value = (value / max_value) * 255
    normalized_value = np.clip(normalized_value, 0, 255) #safety

    colormap = plt.get_cmap('viridis')

    rgba = np.array(colormap(normalized_value / 255.0))  # Normalize to 0-1 for colormap
    return rgba

def masks_to_segmentation(image : np.ndarray) -> np.ndarray:

    assert len(image.shape) == 2

    max = np.max(image)
    rgba_img = np.zeros((*image.shape, 4))
    for row in range(len(image)):
        for col in range(len(image[row])):
            cell_class = apply_colormap(image[row, col], max)
            print(f'on row {row} col {col} value {image[row, col]} cmask {cell_class}')
            rbga = cell_class
            rgba_img[row, col] = rbga
    return rgba_img
