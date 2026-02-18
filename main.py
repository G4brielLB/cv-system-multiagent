from domain.pipelines import SingleStreamStrategy

def main():
    pipeline = SingleStreamStrategy(
        herd_size=5, 
        imgs_per_animal=5, 
        arrival_time=3, 
        selecion_time=0.1, 
        selection_ratio=0.1
    )
    
    pipeline.run()

if __name__ == "__main__":
    main()