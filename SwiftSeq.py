#!/usr/bin/env python3

import argparse
import os

import parsl
from parsl import *

workers = ThreadPoolExecutor(max_workers=8)
dfk = DataFlowKernel(workers)

import bioapps as bio


if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="task_executor.log", help="Logfile path. Defaults to ./task_executor.log")
   parser.add_argument("-c", "--conffile", default="test.conf", help="Config file path. Defaults to ./test.conf")
   parser.add_argument("-j", "--jobid", type=str, action='append')
   parser.add_argument("-i", "--workload_id", default=None)
   args   = parser.parse_args()

   print(dir(bio))
