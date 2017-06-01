from parsl import *

workers = ThreadPoolExecutor(max_workers=8)
dfk = DataFlowKernel(workers)
