import numpy as np
import time

class FrameSelection:

    '''
    ?????
    - n: the amount of imager per animal
    - rateio: percent of images that should be considered suitable
    '''
    def __init__(self, imgs_per_animal: int, ratio: float, duration: float):
        self.duration = duration

        median = int(imgs_per_animal / 2)
        qtt = imgs_per_animal * ratio
        qtt_median = int(qtt / 2)

        self.interval = range(median - qtt_median, median + qtt_median + 1)
        self.n = 0
        self.animal_code = None


    def evaluate(self, animal_code: str):
        time.sleep(self.duration)

        if self.animal_code != animal_code:
            self.animal_code = animal_code
            self.n = 0
        
        self.n += 1
        return self.n in self.interval