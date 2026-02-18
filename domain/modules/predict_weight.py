import numpy as np

class PredictWeight:

    def __init__(self, model: object):
        self.model = model

    def predict(self, imgs: list):
        return self.model(np.array(imgs), training=False).numpy()[0][0]