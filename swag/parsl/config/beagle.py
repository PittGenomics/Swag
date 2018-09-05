from libsubmit.providers import TorqueProvider

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor

config = Config(
    executors=[
        IPyParallelExecutor(
            label='beagle',
            provider=TorqueProvider(
                queue='batch',
                nodes_per_block=1,
                tasks_per_node=1,
                init_blocks=1,
                max_blocks=1,
                overrides='cd /lustre/beagle2/woodard/swag_demo/run; source activate swag'
            ),
        )
    ],
)
