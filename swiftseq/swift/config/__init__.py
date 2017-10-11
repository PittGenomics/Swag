import os
from collections import defaultdict

from swiftseq.core import SwiftSeqApps, SwiftSeqStrings
from swiftseq.swift.config.generate import SwiftConfigProp, SwiftConfigBlock


def create_swift_config(**kwargs):
    """
    Creates a Swift configuration file for this SwiftSeq run.

    kwargs used: wrapper_dir, tmp_dir, disable_lazy_errors, retries,
                 and everything used by get_execution_block()

    :param kwargs: dict Various Swift configuration parameters needed to create the config
    :return: str The path to the Swift config file
    """
    # configHandle
    with open(SwiftSeqStrings.swift_conf_filename) as swift_conf:
        apps_by_site = partition_apps_by_site(SwiftSeqApps.all())
        sites = apps_by_site.keys()

        swift_conf.write('sites: [{}]\n\n'.format(', '.join(sites)))

        for site_i, site in enumerate(sites):
            host_number = str(site_i)

            site_block = SwiftConfigBlock(
                'site.{site}'.format(site=site),
                SwiftConfigProp('staging', 'direct', override='{key}: {val}'),
                SwiftConfigProp('workDirectory', kwargs.get('tmp_dir')),
                SwiftConfigProp('maxParallelTasks', 1001),
                SwiftConfigProp('initialParallelTasks', 999),

                get_execution_block(host_number, site, **kwargs),
                *get_app_blocks(apps_by_site, kwargs.get('wrapper_dir'), kwargs.get('tmp_dir'))
            )

            swift_conf.write(str(site_block) + '\n')

        root_conf_props = [
            SwiftConfigProp('lazyErrors', str(not kwargs.get('disable_lazy_errors')).lower(),
                            override=SwiftConfigProp.NO_QUOTE),
            SwiftConfigProp('executionRetries', int(kwargs.get('retries'))),
            SwiftConfigProp('keepSiteDir', 'true', override=SwiftConfigProp.NO_QUOTE),
            SwiftConfigProp('logProvenance', 'false', override=SwiftConfigProp.NO_QUOTE),
            SwiftConfigProp('statusMode', 'provider'),
            SwiftConfigProp('providerStagingPinSwiftFiles', 'false', override=SwiftConfigProp.NO_QUOTE),
            SwiftConfigProp('alwaysTransferWrapperLog', 'false', override=SwiftConfigProp.NO_QUOTE),
            SwiftConfigProp('maxForeachThreads', 300),
            SwiftConfigProp('TCPPortRange', '50000,51000')
        ]

        swift_conf.write('\n'.join(map(str, root_conf_props)) + '\n')

    return SwiftSeqStrings.swift_conf_filename


def get_app_blocks(apps, wrapper_dir, tmp_dir):
    """
    Formats app blocks for all apps in a given site.

    :param apps: dict Configuration for all apps is a given site, by app name
    :param wrapper_dir: str Directory where all app wrapper scripts reside
    :param tmp_dir: str Temporary directory for this SwiftSeq run
    :return: list<SwiftConfigBlock> A config block for each app in this given site
    """
    app_wrapper_path = os.path.join(wrapper_dir, '{app_name}.sh')
    return [
        SwiftConfigBlock(
            'app.{app_name}'.format(app_name=app_name),
            SwiftConfigProp('executable', app_wrapper_path.format(app_name=app_name)),
            SwiftConfigProp('maxWallTime', app_config['walltime']),
            SwiftConfigProp('env.TMPDIR', tmp_dir, override='{key}="{val}"')
        )
        for app_name, app_config in apps.items()
    ]


def get_execution_block(host_number, site, **kwargs):
    """
    Formats the execution block for a given site.

    kwargs used: job_manager, and everything used by get_options_block()

    :param host_number: int Host number
    :param site: str Name of the site this execution block belongs to
    :param kwargs: dict Various Swift configuration parameters needed to create the config
    :return: SwiftConfigBlock The execution config block for this given site
    """
    return SwiftConfigBlock(
        'execution',
        SwiftConfigProp('type', 'coaster'),
        SwiftConfigProp('URL', 'localhost:{}'.format(host_number)),
        SwiftConfigProp('jobManager', kwargs.get('job_manager', 'pbs')),
        get_options_block(site, **kwargs)
    )


def get_options_block(site, **kwargs):
    """
    Formats the options block that goes in the execution block for a given site.

    kwargs used: tasks_per_node, queue, num_nodes, job_time, work_dir, project_id, job_options

    :param site: str Name of the site this options block belongs to
    :param kwargs: dict Various Swift configuration parameters needed to create the config
    :return: SwiftConfigBlock The options block for this given site
    """
    if site == 'one':
        tasks_per_node = 1
    elif site == 'RAM':
        tasks_per_node = int(round(kwargs.get('tasks_per_node') / 2.0))
    else:
        tasks_per_node = int(kwargs.get('tasks_per_node'))

    return SwiftConfigBlock(
        'options',
        *([
            # Core options
            SwiftConfigProp('nodeGranularity', 1),
            SwiftConfigProp('jobQueue', kwargs.get('queue')),
            SwiftConfigProp('maxNodesPerJob', 1),
            SwiftConfigProp('maxJobs', kwargs.get('queue')),
            SwiftConfigProp('highOverallocation', 100),
            SwiftConfigProp('maxJobTime', str(kwargs.get('job_time'))),
            SwiftConfigProp('lowOverallocation', 100),
            SwiftConfigProp('tasksPerNode', tasks_per_node),
            SwiftConfigProp('workerLoggingLevel', 'DEBUG'),
            SwiftConfigProp('workerLoggingDirectory', os.path.join(kwargs.get('work_dir'), 'workerLogging'))
        ] + [
            # If a project ID exists, return a property, else nothing
            SwiftConfigProp('jobProject', kwargs.get('project_id'))
        ] if kwargs.get('project_id') is not None else [] + [
            # The jobOptions block
            SwiftConfigBlock(
                'jobOptions',
                *[
                    SwiftConfigProp(key.strip(), value.strip(), override=SwiftConfigProp.NO_QUOTE)
                    for option in kwargs.get('job_options').split(';')
                    for key, value in option.strip().split(':')
                ]
            )
        ])
    )


def partition_apps_by_site(apps):
    """
    Partitions a dictionary of SwiftSeq supported apps by their pools as given in
    swiftseq.core.SwiftSeqApps

    :param apps: dict Dictionary of apps as given in swiftseq.core.SwiftSeqApps
    :return: dict Supported apps arranged by pool name
    """
    apps_by_site = defaultdict(dict)
    for app_name in apps:
        pool = apps[app_name].get('pool', SwiftSeqStrings.app_pool_default)
        apps_by_site[pool][app_name] = apps[app_name]
    return apps_by_site
