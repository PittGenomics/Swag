from importlib.util import spec_from_file_location, module_from_spec
import logging
from multiprocessing import cpu_count
import os
from tempfile import gettempdir

from parsl.utils import RepresentationMixin
from parsl.configs.local_threads import config

from swag.util.path import is_valid_dir, is_valid_file, is_valid_tmp_dir

logger = logging.getLogger(__name__)

class SwagConfig(RepresentationMixin):
    """
    Specification of Swag configuration options.

    Parameters
    ----------
    data : str
        The data directory containing sequencing data to be run.
    workflow : str
        Path to the Swag workflow (in .json format) that will be run over input data.
    ref_config : str
        Path to the configuration file that contains paths to the references files.
    exe_config : str
        Path to file that contains paths to algorithm executables.
    geno_segment_size : int, optional
        Size of the segment used by any variant calling process (default = 10000000).
    cores_per_node : int, optional
        Number of processing cores available per worker node (default = <num cores on head node>).
    tasks_per_node : int, optional
        Number of tasks to pack (run simultaneously) on each worker node (default = 8).
    ram_per_node : int, optional
        Amount of RAM in megabytes available on each worker node (default = 29000).
    tmp : str, optional
        Temporary directory for this run (by default on will be created).
    worker_use_tmp : bool, optional
        Have wrappers use /tmp on the working as temp space. Should assist in reducing
        overall IO burden (default = True).
    parsl_config : parsl.config.Config, optional
        The Parsl configuration to use. Default is parsl.config.Config(ThreadPoolExecutor()).
    """
    def __init__(self,
                 data,
                 workflow,
                 ref_config,
                 exe_config,
                 geno_segment_size=10000000,
                 cores_per_node=cpu_count(),
                 tasks_per_node=8,
                 ram_per_node=29000,
                 tmp=os.path.join(gettempdir(), os.environ['USER']),
                 worker_use_tmp=True,
                 parsl_config=config):
        self.data = data
        self.workflow = workflow
        self.ref_config = ref_config
        self.exe_config = exe_config
        self.geno_segment_size = geno_segment_size
        self.cores_per_node = cores_per_node  # TODO read from parsl config?
        self.tasks_per_node = tasks_per_node
        self.ram_per_node = ram_per_node
        self.tmp = tmp
        self.worker_use_tmp = worker_use_tmp
        self.parsl_config = parsl_config

        is_valid_dir(data)
        is_valid_tmp_dir(tmp)
        is_valid_file(workflow)
        is_valid_file(ref_config)
        is_valid_file(exe_config)


def load_config(filepath):
    """Load a SwagConfig configuration.

    This only works in Python 3.5+
    Adapted from https://github.com/djf604/operon/blob/master/operon/_util/home.py#L81

    Parameters
    ----------
    filepath : str
        Filepath to file containing a SwagConfig object.
    """
    spec = spec_from_file_location('config', filepath)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)

    for v in mod.__dict__.values():
        if isinstance(v, SwagConfig):
            return v

