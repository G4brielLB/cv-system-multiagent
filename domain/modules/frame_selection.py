import numpy as np
import time

class FrameSelection:

    '''
    Perform the frame selection task
    - suitable_window: the window of seconds that should be considered suitable
    - snooze_duration: the duration of the sleep in seconds
    '''
    def __init__(self, suitable_window: float, snooze_duration: float):
        self.suitable_window = suitable_window
        self.snooze_duration = snooze_duration

    def evaluate(self, elapsed_time: float):
        suite = False

        if elapsed_time <= self.suitable_window:
            suite = True
        
        time.sleep(self.snooze_duration)
        return suite