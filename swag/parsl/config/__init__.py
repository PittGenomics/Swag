import os
from collections import defaultdict

import six

from swag.core import SwagApps, SwagStrings
from swag.parsl.config.generate import ParslConfigProp, ParslConfigBlock


def create_parsl_config(**kwargs):
    """
    Creates a Parsl configuration file for this Swag run.

    kwargs used: wrapper_dir, tmp_dir, disable_lazy_errors, retries,
                 and everything used by get_execution_block()

    :param kwargs: dict Various Parsl configuration parameters needed to create the config
    :return: str The path to the Parsl config file
    """
    executor = kwargs.get('executor', 'scheduler')
    print('Creating parsl config')
    print(kwargs)
    # configHandle
    with open(SwagStrings.parsl_conf_filename, 'w') as parsl_conf:
        if executor == 'local':
            apps_by_site = partition_apps_by_site(SwagApps.all(), common_pool_name='local')

            parsl_conf.write('sites: [local]\n\n')

            site_block = ParslConfigBlock(
                'site.local',
                ParslConfigProp('staging', 'direct', override='{key}: {val}'),
                ParslConfigProp('workDirectory', kwargs.get('tmp_dir')),
                ParslConfigProp('maxParallelTasks', 1),
                ParslConfigProp('initialParallelTasks', 1),

                ParslConfigBlock(
                    'execution',
                    ParslConfigProp('type', 'local'),
                    ParslConfigProp('URL', 'localhost')
                ),

                *get_app_blocks(
                    apps=apps_by_site['local'],
                    wrapper_dir=kwargs.get('wrapper_dir'),
                    tmp_dir=kwargs.get('tmp_dir'),
                    apps_workflow=kwargs.get('workflow')
                )
            )

            parsl_conf.write(str(site_block) + '\n')

            root_conf_props = [
                ParslConfigProp('lazyErrors', 'false',
                                override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('executionRetries', 0),
                ParslConfigProp('keepSiteDir', 'true', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('logProvenance', 'false', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('statusMode', 'provider'),
                ParslConfigProp('providerStagingPinParslFiles', 'false', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('alwaysTransferWrapperLog', 'true', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('TCPPortRange', '50000,51000')
            ]

            parsl_conf.write('\n'.join(map(str, root_conf_props)) + '\n')

        elif executor == 'scheduler':
            apps_by_site = partition_apps_by_site(SwagApps.all())
            sites = apps_by_site.keys()

            parsl_conf.write('sites: [{}]\n\n'.format(', '.join(sites)))

            for site_i, site in enumerate(sites):
                host_number = str(site_i)

                site_block = ParslConfigBlock(
                    'site.{site}'.format(site=site),
                    ParslConfigProp('staging', 'direct', override='{key}: {val}'),
                    ParslConfigProp('workDirectory', kwargs.get('tmp_dir')),
                    ParslConfigProp('maxParallelTasks', 1001),
                    ParslConfigProp('initialParallelTasks', 999),

                    get_execution_block(host_number, site, **kwargs),
                    *get_app_blocks(
                        apps=apps_by_site[site],
                        wrapper_dir=kwargs.get('wrapper_dir'),
                        tmp_dir=kwargs.get('tmp_dir'),
                        apps_workflow=kwargs.get('workflow')
                    )
                )

                parsl_conf.write(str(site_block) + '\n')

            root_conf_props = [
                ParslConfigProp('lazyErrors', str(not kwargs.get('disable_lazy_errors')).lower(),
                                override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('executionRetries', int(kwargs.get('retries'))),
                ParslConfigProp('keepSiteDir', 'true', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('logProvenance', 'false', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('statusMode', 'provider'),
                ParslConfigProp('providerStagingPinParslFiles', 'false', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('alwaysTransferWrapperLog', 'false', override=ParslConfigProp.NO_QUOTE),
                ParslConfigProp('maxForeachThreads', 300),
                ParslConfigProp('TCPPortRange', '50000,51000')
            ]

            parsl_conf.write('\n'.join(map(str, root_conf_props)) + '\n')
        else:
            raise ValueError('executor keyword argument must be either \'local\' or \'pbs\'')

    return SwagStrings.parsl_conf_filename


def get_app_blocks(apps, wrapper_dir, tmp_dir, apps_workflow):
    """
    Formats app blocks for all apps in a given site.

    :param apps: dict Configuration for all apps is a given site, by app name
    :param wrapper_dir: str Directory where all app wrapper scripts reside
    :param tmp_dir: str Temporary directory for this Swag run
    :return: list<ParslConfigBlock> A config block for each app in this given site
    """
    app_wrapper_path = os.path.join(wrapper_dir, '{app_name}.sh')

    # If workflow config isn't available default to an empty dict which will always defer
    # to global app config walltime
    try:
        app_workflow_configs = apps_workflow.programs_in_workflow
    except AttributeError:
        app_workflow_configs = dict()

    # Iterate though apps to form app blocks
    app_blocks = list()
    for app_name, app_config in six.iteritems(apps):
        walltime = (app_workflow_configs.get(app_name, dict()).get('walltime') or
                    app_config.get('walltime', SwagStrings.app_walltime_default))
        app_blocks.append(
            ParslConfigBlock(
                'app.{app_name}'.format(app_name=app_name),
                ParslConfigProp('executable', app_wrapper_path.format(app_name=app_name)),
                ParslConfigProp('maxWallTime', walltime),
                ParslConfigProp('env.TMPDIR', tmp_dir, override='{key}="{val}"')
            )
        )
    return app_blocks


def get_execution_block(host_number, site, **kwargs):
    """
    Formats the execution block for a given site.

    kwargs used: job_manager, and everything used by get_options_block()

    :param host_number: int Host number
    :param site: str Name of the site this execution block belongs to
    :param kwargs: dict Various Parsl configuration parameters needed to create the config
    :return: ParslConfigBlock The execution config block for this given site
    """
    return ParslConfigBlock(
        'execution',
        ParslConfigProp('type', 'coaster'),
        ParslConfigProp('URL', 'localhost:{}'.format(host_number)),
        ParslConfigProp('jobManager', kwargs.get('job_manager', 'pbs')),
        get_options_block(site, **kwargs)
    )


def get_options_block(site, **kwargs):
    """
    Formats the options block that goes in the execution block for a given site.

    kwargs used: tasks_per_node, queue, num_nodes, job_time, work_dir, project_id, job_options

    :param site: str Name of the site this options block belongs to
    :param kwargs: dict Various Parsl configuration parameters needed to create the config
    :return: ParslConfigBlock The options block for this given site
    """
    if site == 'one':
        tasks_per_node = 1
    elif site == 'RAM':
        tasks_per_node = int(round(kwargs.get('tasks_per_node') / 2.0))
    else:
        tasks_per_node = int(kwargs.get('tasks_per_node'))

    return ParslConfigBlock(
        'options',
        *([
            # Core options
            ParslConfigProp('nodeGranularity', 1),
            ParslConfigProp('jobQueue', kwargs.get('queue')),
            ParslConfigProp('maxNodesPerJob', 1),
            ParslConfigProp('maxJobs', kwargs.get('num_nodes')),
            ParslConfigProp('highOverallocation', 100),
            ParslConfigProp('maxJobTime', str(kwargs.get('job_time'))),
            ParslConfigProp('lowOverallocation', 100),
            ParslConfigProp('tasksPerNode', tasks_per_node),
            ParslConfigProp('workerLoggingLevel', 'DEBUG'),
            ParslConfigProp('workerLoggingDirectory',
                            os.path.join(kwargs.get('work_dir'), SwagStrings.worker_logging_dir))
        ] + ([
            # If a project ID exists, return a property, else nothing
            ParslConfigProp('jobProject', kwargs.get('project_id'))
        ] if kwargs.get('project_id') is not None else []) + ([
            # The jobOptions block
            ParslConfigBlock(
                'jobOptions',
                *parse_job_options(kwargs.get('job_options'))
            )
        ] if kwargs.get('job_options') else []))
    )

def parse_job_options(job_options):
    options = list()
    for job_options in job_options.strip().split(';'):
        key, value = job_options.strip().split(':')
        options.append(ParslConfigProp(key.strip(), value.strip(), override=ParslConfigProp.NO_QUOTE))
    return options


def partition_apps_by_site(apps, common_pool_name=None):
    """
    Partitions a dictionary of Swag supported apps by their pools as given in
    swag.core.SwagApps

    :param apps: dict Dictionary of apps as given in swag.core.SwagApps
    :return: dict Supported apps arranged by pool name
    """
    apps_by_site = defaultdict(dict)
    for app_name in apps:
        pool = common_pool_name or apps[app_name].get('pool', SwagStrings.app_pool_default)
        apps_by_site[pool][app_name] = apps[app_name]
    return apps_by_site
