from swag.core.config import SwagConfig
from parsl.configs.local_threads import config as parsl_config

config = SwagConfig(
    data='data',
    workflow='workflow.json',
    ref_config='references.config',
    exe_config='executables.config',
    parsl_config=parsl_config
)
