import pynvml

pynvml.nvmlInit()
gpu_count = pynvml.nvmlDeviceGetCount()
print('Quantidade de GPUs:', gpu_count)

for i in range(gpu_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    name = pynvml.nvmlDeviceGetName(handle)
    # Compatível com bytes e str
    if isinstance(name, bytes):
        name = name.decode('utf-8')
    print(f'GPU {i}: {name}')
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f'  Memória total: {mem_info.total / (1024**3):.2f} GB')
    print(f'  Memória livre: {mem_info.free / (1024**3):.2f} GB')
    print(f'  Memória usada: {mem_info.used / (1024**3):.2f} GB')

pynvml.nvmlShutdown() 