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
        herd_size: int, arrival_time: int, passage_time: int, fselection_time: float, fselection_window:float):
        
        self.pid = pid
        self.metrics = {
            'pid':pid,
            'load_model_start':datetime.now().isoformat(),
        }

        self.herd_size = herd_size
        self.arrival_time = arrival_time
        self.passage_time = passage_time
        
        self.model = keras.models.load_model(f'infra/models/model_run1_epoch029.keras')
        self.metrics['load_model_final'] = datetime.now().isoformat()

        self.frame_selection = FrameSelection(
            suitable_window=fselection_window, 
            model=self.model
        )
        
        self.image_capture = ImageCapture()
        self.data_enhance = DataEnhance()
        self.predict_weight = PredictWeight(model=self.model)

    def run(self):
        self.metrics['animals'] = {}
        
        for animal in range(1, self.herd_size + 1):
            print(f'animal: {animal}')
            start_at = datetime.now()

            self.metrics['animals'][animal] = {
                'first_image_capture_time':datetime.now().isoformat(),
                'imgs':{}
            }

            weights = []
            i = 0
            
            elapsed_time = (datetime.now() - start_at).total_seconds()
            last_image_capture = None
            while elapsed_time < self.passage_time:
                i += 1
                print(f'image: {i}')

                img = self.image_capture.get_frame()             
                last_image_capture = datetime.now().isoformat()
                
                img = self.data_enhance.run(img)
                
                suitable = self.frame_selection.evaluate(
                    elapsed_time=elapsed_time,
                    img=img
                )
                if suitable:
                    inference_metrics = {
                        'weight_prediction_start':datetime.now().isoformat()
                    }
                    
                    weight = self.predict_weight.predict(imgs=[img])[0][0]
                    weights.append(weight)

                    inference_metrics['weight_prediction_final'] = datetime.now().isoformat()
                    self.metrics['animals'][animal]['imgs'][i] = inference_metrics

                elapsed_time = (datetime.now() - start_at).total_seconds()
            
            self.metrics['animals'][animal]['last_image_capture_time'] = last_image_capture
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
    def __init__(self, pid: str,
        herd_size: int, arrival_time: int, passage_time: int, fselection_time: float, fselection_window:float):
        
        self.pid = pid
        self.metrics = {
            'pid':pid,
            'load_model_start':datetime.now().isoformat(),
        }

        self.herd_size = herd_size
        self.arrival_time = arrival_time
        self.passage_time = passage_time

        self.model = keras.models.load_model(f'infra/models/model_run1_epoch029.keras')
        self.metrics['load_model_final'] = datetime.now().isoformat()         

        self.frame_selection = FrameSelection(
            suitable_window=fselection_window, 
            model=self.model
        )
        
        self.image_capture = ImageCapture()
        self.data_enhance = DataEnhance()
        self.predict_weight = PredictWeight(model=self.model)

    def run(self):
        self.metrics['animals'] = {}
        
        for animal in range(1, self.herd_size + 1):
            print(f'animal: {animal}')
            start_at = datetime.now()

            self.metrics['animals'][animal] = {
                'first_image_capture_time':datetime.now().isoformat(),
                'imgs':{}
            }

            imgs = []
            i = 0
            
            elapsed_time = (datetime.now() - start_at).total_seconds()
            last_image_capture = None

            while elapsed_time < self.passage_time:
                i += 1
                print(f'image: {i}')

                img = self.image_capture.get_frame()
                last_image_capture = datetime.now().isoformat()
                
                img = self.data_enhance.run(img)

                suitable = self.frame_selection.evaluate(
                    elapsed_time=elapsed_time,
                    img=img
                )
                if suitable:
                    imgs.append(img)

                elapsed_time = (datetime.now() - start_at).total_seconds()
                
            self.metrics['animals'][animal]['last_image_capture_time'] = last_image_capture
            inference_metrics = {
                'weight_prediction_start':datetime.now().isoformat()
            }
            
            weights = self.predict_weight.predict(imgs=imgs)
            print(weights)

            inference_metrics['weight_prediction_final'] = datetime.now().isoformat()
            self.metrics['animals'][animal]['imgs'][i] = inference_metrics

            predicted_weight = np.mean(weights)
            self.metrics['animals'][animal]['weight_prediction_final'] = datetime.now().isoformat()
            print(predicted_weight)

            # wait for the next animal
            time.sleep(self.arrival_time)

        with open(f"infra/reports/{self.pid}/metrics.json", "w") as json_file:
            json.dump(self.metrics, json_file, indent=4)    
