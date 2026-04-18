import numpy as np
import time

class FrameSelection:

    '''
    Perform the frame selection task
    - suitable_window: the window of seconds that should be considered suitable
    - snooze_duration: the duration of the sleep in seconds
    '''
    def __init__(self, suitable_window: float,  model: object):
        self.suitable_window = suitable_window
        self.model = model

    def evaluate(self, elapsed_time: float, img):
        suite = False

        if elapsed_time <= self.suitable_window:
            suite = True
        
        self.model(np.array([img]), training=False)
        return suite