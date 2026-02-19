import os, keras, time, json
import numpy as np

from datetime import datetime

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
    def __init__(self, pid: str,
        herd_size: int, imgs_per_animal: int, arrival_time: int, fselection_time: float, fselection_ratio:int):
        
        self.pid = pid
        self.metrics = {
            'pid':pid,
            'load_model_start':datetime.now().isoformat(),
        }

        self.imgs_per_animal = imgs_per_animal
        self.herd_size = herd_size
        self.arrival_time = arrival_time
        
        self.model = keras.models.load_model(f'infra/models/model_run7_epoch180.keras')
        self.metrics['load_model_final'] = datetime.now().isoformat()         

        self.frame_selection = FrameSelection(
            imgs_per_animal=imgs_per_animal, 
            ratio=fselection_ratio, 
            duration=fselection_time
        )
        
        self.image_capture = ImageCapture()
        self.data_enhance = DataEnhance()
        self.predict_weight = PredictWeight(model=self.model)

    def run(self):
        self.metrics['animals'] = {}
        
        for animal in range(1, self.herd_size + 1):
            print(f'animal: {animal}')

            self.metrics['animals'][animal] = {
                'first_image_capture_time':datetime.now().isoformat(),
                'imgs':{}
            }

            weights = []
            for i in range(1, self.imgs_per_animal):
                print(f'image: {i}')

                img = self.image_capture.get_frame()
                
                if (i == self.imgs_per_animal - 1):
                    self.metrics['animals'][animal]['last_image_capture_time'] = datetime.now().isoformat()
                
                img = self.data_enhance.run(img)
                
                suitable = self.frame_selection.evaluate(animal_code=animal)
                if suitable:
                    inference_metrics = {
                        'weight_prediction_start':datetime.now().isoformat()
                    }
                    
                    weight = self.predict_weight.predict(imgs=[img])
                    weights.append(weight)

                    inference_metrics['weight_prediction_final'] = datetime.now().isoformat()
                    self.metrics['animals'][animal]['imgs'][i] = inference_metrics
            
            print(weights)

            predicted_weight = np.mean(weights)
            self.metrics['animals'][animal]['weight_prediction_final'] = datetime.now().isoformat()
            print(predicted_weight)

            # wait for the next animal
            time.sleep(self.arrival_time)

        with open(f"infra/reports/{self.pid}/metrics.json", "w") as json_file:
            json.dump(self.metrics, json_file, indent=4)

class BatchStreamStrategy:

    '''
    Docstring for BatchStreamStrategy
    '''
    def __init__(self, herd_size: int, imgs_per_animal: int, interval: int, selecion_time: int, selection_ratio:int):
        pass
