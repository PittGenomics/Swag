from parsl import *
#from parsl.configs.local import localThreads as config

config = {
        "sites": [
            {
                "site": "local_threads",
                "auth": {
                    "channel": None
                },
                "execution": {
                    "executor": "threads",
                    "provider": None,
                    "maxThreads": 4,
                }
            }
        ],
    "globals": {
        "lazyErrors": True
    }
}

import glob

config["globals"]["checkpointMode"] = 'task_exit'
f = glob.glob("./runinfo/[0-9]*/checkpoint")
config["globals"]["checkpointFiles"] = f

dfk = DataFlowKernel(config=config)


if __name__ == "__main__":

    print(config)
