import threading, time, psutil

class CPUMonitor(threading.Thread):
    def __init__(self, pid: str):
        super().__init__()
        self.running = True
        self.data = []
        self.daemon = True # Allows the main program to exit even if thread is running

    def run(self):
        # The first call returns 0.0, so we ignore it
        psutil.cpu_percent(percpu=True)
        while self.running:
            # Call with an interval, which blocks the thread for that duration 
            # and updates the measurement internally
            cpu_percent = psutil.cpu_percent(percpu=True, interval=1)
            self.data.append(cpu_percent)
            print(f'CPU: {cpu_percent}')

    def stop(self):
        self.running = False
        # TODO: save data

class RAMMonitor(threading.Thread):
    def __init__(self, pid: str):
        super().__init__()
        self.running = True
        self.data = []
        self.daemon = True # Allows the main program to exit even if thread is running

    def run(self):
        while self.running:
            # Call with an interval, which blocks the thread for that duration 
            # and updates the measurement internally
            virtual_memory = psutil.virtual_memory()
            self.data.append(virtual_memory)
            print(f'RAM: {virtual_memory}')
            
            time.sleep(1)

    def stop(self):
        self.running = False