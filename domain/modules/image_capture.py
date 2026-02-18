import skimage.io as ski

class ImageCapture:

    def __init__(self):
        pass

    def get_frame(self):
        return ski.imread(f'infra/images/sample.png')