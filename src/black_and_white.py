from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile as JPEG
from PIL import ImageEnhance
from PIL import ImageFilter 

def img_to_greyscale(img : Image.Image) -> Image.Image:
    """ 
        converts an image to greyscale using ITU-R 601-2 luma transformo
        args: img -> np array or PIL image object (of any filetype)
        returns a PIL image object in greyscale
    """
    #never can be too safe
    if not isinstance(img, Image.Image):
        raise TypeError("img parameter did not recieve PIL image")

    return img.convert("L")


def crop_img(img : Image.Image, corners: tuple[int, int, int, int]) -> Image.Image:
    """
        crops an image based on 4 provided corners & restores original
        args:
            -img: PIL image object
            -(left, upper, right, lower)
                -the two corners of the rectangle to crop to
                -using PIL image coordinate system ((0, 0) at top left)
        returns: a new image object of the cropped image region
    """

    #just in case
    if not isinstance(img, Image.Image):
        raise TypeError("img parameter did not recieve PIL image")


    # check for any negative values
    if any(val < 0 for val in corners):
        raise Exception("at least one of the coordinates provided is below 0")

    # check that x coords provided dont go out of range, and y coords dont too
    x_range = img.size[0]
    y_range = img.size[1]

    if (corners[0] > x_range or corners[2] > x_range):
        raise Exception("Coordinate values go out of bounds")
    if (corners[1] > y_range or corners[3] > y_range):
        raise Exception("Coordinate values go our of bounds")

    # checking that cooordinates are provided in the correct order is done by PIL

    return img.crop(corners)

def change_saturation(img : Image.Image, saturation_level : float) -> Image.Image:
    """
    
    control saturation level of image by some multiplier saturation_level
    multiplier 0 makes image greyscale
    args: PIL image object, saturation_level mutliplier
    returns a PIL image object with the modified image

    """
    #safety first
    if not isinstance(img, Image.Image):
        raise TypeError("img parameter did not recieve PIL image")

    enhancer_obj = ImageEnhance.Color(img)
    img = enhancer_obj.enhance(saturation_level)
    return img

def edge_enhance(img : Image.Image) -> Image.Image:
    """
        makes edges in image more pronounced
        args: PIL image 
        returns a PIL image
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img parameter did not recieve PIL image")

    edge_detected = img.filter(ImageFilter.EDGE_ENHANCE)

    return edge_detected

def edges_in_image_filter(img : Image.Image) -> Image.Image:
    """
        edge detection
        args: PIL image 
        returns a PIL image of the edges found
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img parameter did not recieve PIL image")

    edge_detected = img.filter(ImageFilter.FIND_EDGES)

    return edge_detected
