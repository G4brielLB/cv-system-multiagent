import numpy as np

from domain.helpers import transformations

class DataEnhance:

    def __init__(self):
        self.transfs = [
            transformations.NoiseRemovalSetMaxValue(max_value=1950),
            transformations.AdjustScaleWithFixedMaxValue(max_value=1950),
            transformations.Replicate1DtoNDimChannel(dim=3),
            transformations.ResizeImageWithPadding(shape=(300,300))
        ]

    def run(self, img: np.array):
        for trf in self.transfs:
            img = trf.transform(img)
        return img