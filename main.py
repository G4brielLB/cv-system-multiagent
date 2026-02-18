import sys
from domain.pipelines import SingleStreamStrategy

def main(
        strategy: str, herd_size: int, imgs_per_animal: int, arrival_time: int, fselection_time: float, fselection_ratio:int):
    
    pipeline = SingleStreamStrategy(
        herd_size=herd_size, 
        imgs_per_animal=imgs_per_animal, 
        arrival_time=arrival_time, 
        fselection_ratio=fselection_ratio, 
        fselection_time=fselection_time,
    ) if strategy == 'single' else None
    
    pipeline.run()

if __name__ == "__main__":    
    main(
        strategy = sys.argv[1], herd_size = int(sys.argv[2]), imgs_per_animal = int(sys.argv[3]), 
        arrival_time = int(sys.argv[4]), fselection_time = float(sys.argv[5]), fselection_ratio=float(sys.argv[6]),
    )