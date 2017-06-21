from parsl import *

workers = ThreadPoolExecutor(max_workers=1024)
dfk = DataFlowKernel(workers)
