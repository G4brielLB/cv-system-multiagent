import tensorflow as tf
import numpy as np

class Replicate1DtoNDimChannel:

    def __init__(self, dim: int):
        self.dim = dim

    def transform(self, data: np.array):
        img_rows, img_cols = data.shape
        g = np.zeros((img_rows, img_cols, self.dim))

        for i in range(0, data.shape[0]):
          for j in range(0, data.shape[1]):
            g[i,j] = [data[i,j]] * self.dim           

        return g
        
class NoiseRemovalSetMaxValue:

    def __init__(self, max_value: int):
        self.max_value = max_value

    def transform(self, data: np.array):
        g = np.copy(data)

        for i in range(0, data.shape[0]):
          for j in range(0, data.shape[1]):
            pos = (i,j)
            if data[pos] >= self.max_value:
                g[pos] = self.max_value

        return g

class AdjustScaleWithFixedMaxValue:

    def __init__(self, max_value: int):
        self.max_value = max_value

    def transform(self, data: np.array):
        data = data.astype('float32')
        data /= self.max_value
        
        return data

class ResizeImageWithPadding:

    def __init__(self, shape: tuple):
        self.shape = shape

    def transform(self, data: np.array):    
        img = tf.image.convert_image_dtype(data, tf.float32)
    
        # Redimensiona mantendo proporção (lado menor ajustado)
        resized_img = tf.image.resize_with_pad(img, self.shape[0], self.shape[1])
        
        return resized_img