import threading, time, psutil, csv, GPUtil
from datetime import datetime

class CPUMonitor(threading.Thread):
    def __init__(self, pid: str):
        super().__init__()
        self.pid = pid
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
            self.data.append([datetime.now().isoformat()] + cpu_percent)
            print(f'CPU: {cpu_percent}')

    def stop(self):
        self.running = False

        # Criar cabeçalho do CSV
        num_cores = len(self.data[0]) - 1
        cabecalho = ["timestamp"] + [f"cpu_core_{i}" for i in range(num_cores)]

        # Salvar CSV
        with open(f"infra/reports/{self.pid}/cpu.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(cabecalho)
            writer.writerows(self.data)

class RAMMonitor(threading.Thread):
    def __init__(self, pid: str):
        super().__init__()
        self.pid = pid
        self.running = True
        self.data = []
        self.daemon = True # Allows the main program to exit even if thread is running

    def run(self):
        while self.running:
            # Call with an interval, which blocks the thread for that duration 
            # and updates the measurement internally
            mem = psutil.virtual_memory()
            
            line = [
                datetime.now().isoformat(),
                mem.total,
                mem.available,
                mem.used,
                mem.percent,
                mem.free,
                mem.active,
                mem.inactive,
                mem.buffers,
                mem.cached
            ]
            
            self.data.append(line)
            print(f'RAM: {mem}')
            
            # wait 1 sec
            time.sleep(1)

    def stop(self):
        self.running = False

        # Cabeçalho CSV
        header = [
            "timestamp",
            "total",
            "available",
            "used",
            "percent",
            "free",
            "active",
            "inactive",
            "buffers",
            "cached"
        ]

        # Salvar arquivo
        with open(f"infra/reports/{self.pid}/mem.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(self.data)


class GPUMonitor(threading.Thread):
    def __init__(self, pid: str):
        super().__init__()
        self.pid = pid
        self.running = True
        self.data = []
        self.daemon = True # Allows the main program to exit even if thread is running

    def run(self):
        while self.running:
            gpus = GPUtil.getGPUs()

            for gpu in gpus:
                linha = [
                    datetime.now().isoformat(),
                    gpu.id,
                    gpu.name,
                    gpu.load * 100,
                    gpu.memoryUsed,
                    gpu.memoryTotal,
                    gpu.memoryUtil * 100,
                    gpu.temperature
                ]
                self.data.append(linha)    
            
            print(f'GPU: {gpus}')            
            # wait 1 sec
            time.sleep(1)

    def stop(self):
        self.running = False

        # Cabeçalho CSV
        header = [
            "timestamp",
            "gpu_id",
            "nome",
            "uso_gpu_percent",
            "memoria_usada_MB",
            "memoria_total_MB",
            "uso_memoria_percent",
            "temperatura_C"
        ]

        # Salvar CSV
        with open(f"infra/reports/{self.pid}/gpu.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(self.data)
