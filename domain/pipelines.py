import os, keras, time
import numpy as np

os.environ["TF_ENABLE_ONEDNN_OPTS"] = '0'
os.environ["KERAS_BACKEND"] = "tensorflow"

def dummy_npwarn_decorator_factory():
  def npwarn_decorator(x):
    return x
  return npwarn_decorator
np._no_nep50_warning = getattr(np, '_no_nep50_warning', dummy_npwarn_decorator_factory)

from domain.modules.frame_selection import FrameSelection
from domain.modules.image_capture   import ImageCapture
from domain.modules.predict_weight  import PredictWeight
from domain.modules.data_enhance    import DataEnhance

class SingleStreamStrategy:

    '''
    Docstring for SingleStreamStrategy
    '''
    def __init__(self, 
        herd_size: int, imgs_per_animal: int, arrival_time: int, fselection_time: float, fselection_ratio:int):
        
        self.imgs_per_animal = imgs_per_animal
        self.herd_size = herd_size
        self.arrival_time = arrival_time
        self.model = keras.models.load_model(f'infra/models/model_run7_epoch180.keras')

        self.frame_selection = FrameSelection(
            imgs_per_animal=imgs_per_animal, 
            ratio=fselection_ratio, 
            duration=fselection_time
        )
        
        self.image_capture = ImageCapture()
        self.data_enhance = DataEnhance()
        self.predict_weight = PredictWeight(model=self.model)

    def run(self):
        
        for animal in range(self.herd_size):
            print(f'animal: {animal}')
            weights = []

            for i in range(self.imgs_per_animal):
                print(f'image: {i}')

                img = self.image_capture.get_frame()
                img = self.data_enhance.run(img)
                suitable = self.frame_selection.evaluate(animal_code=animal)
                if suitable:
                    weights.append(
                        self.predict_weight.predict(imgs=[img])
                    )

            print(weights)
            predicted_weight = np.mean(weights)
            print(predicted_weight)

            # wait for the next animal
            time.sleep(self.arrival_time)
 
class BatchStremStrategy:

    '''
    Docstring for BatchStreamStrategy
    '''
    def __init__(self, herd_size: int, imgs_per_animal: int, interval: int, selecion_time: int, selection_ratio:int):
        pass
