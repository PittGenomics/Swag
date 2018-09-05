from parsl.app.app import bash_app
from swag.core import SwagStrings

@bash_app
def BwaMem(work_dir, in_bam, RG_name, id, dir, outputs=[], stdout=None, stderr=None):
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'BwaMem.sh')

    return executable + ' {1} {outputs[0]} {2} {outputs[1]} {3} {4}'


@bash_app
def RgMergeSort(work_dir, id, dir, inputs=[], outputs=[], stdout=None, stderr=None):
    """
    inputs: RGalnBams
    outputs: [alnSampleContigBamFile, alnSampleBamLog, alnSampleContigBams....]
    """
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'RgMergeSort.sh')
    in_bams = ' '.join([str(i) for i in inputs])

    return executable + ' {outputs[0]} {outputs[1]} {1} {2} ' + in_bams

@bash_app
def PicardMarkDuplicates(work_dir, in_bam, id, dir, outputs=[], stdout=None, stderr=None):
    """
    outputs = [file logFile, file outBam, file outBamMetrics]
    """
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'PicardMarkDuplicates.sh')

    return executable + ' {1} {outputs[1]} {outputs[0]} {outputs[2]} {2} {3}'

@bash_app
def IndexBam(work_dir, in_bam, outputs=[], stdout=None, stderr=None):
    """
    outputs = [file logFile, file outIndex]
    """
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'IndexBam.sh')

    return executable + ' {1} {outputs[1]} {outputs[0]}'

@bash_app
def ContigMergeSort(work_dir, id, dir, inputs=[], outputs=[], stdout=None, stderr=None):
    """
    outputs = [file logFile, file outBam, file outBamBai]
    """

    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'ContigMergeSort.sh')

    bams = ' '.join(inputs)
    return executable + ' {outputs[1]} {outputs[0]} {1} {2} ' + bams

