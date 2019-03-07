"""
Apps and app wrappers.

The bodge of writing a wrapper for each app in order to assemble filenames is necessary due to
a limitation in Parsl [1]. As soon as that issue is fixed in Parsl, we can replace these function apps
with class apps, and eliminate the wrappers.

[1] https://github.com/Parsl/parsl/issues/483
"""

import os

from parsl.app.app import bash_app
from swag.core import SwagStrings

@bash_app
def BwaMem(work_dir, bam, RG_name, sample_id, sample_dir, outputs=[], stdout=None, stderr=None):
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'BwaMem.sh')

    return executable + ' {1} {outputs[0]} {2} {outputs[1]} {3} {4}'


@bash_app
def RgMergeSort(work_dir, sample_id, sample_dir, inputs=[], outputs=[], stdout=None, stderr=None):
    """
    inputs: RGalnBams
    outputs: [alnSampleContigBamFile, alnSampleBamLog, alnSampleContigBams....]
    """
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'RgMergeSort.sh')
    bams = ' '.join([str(i) for i in inputs])

    return executable + ' {outputs[0]} {outputs[1]} {1} {2} ' + bams

@bash_app
def picard_mark_duplicates_app(executable, bam, sample_id, sample_dir, outputs=[], stdout=None, stderr=None):
    return executable + ' {1} {outputs[1]} {outputs[0]} {outputs[2]} {2} {3}'

def picard_mark_duplicates(work_dir, bam, contig, sample_id, sample_dir):
    sample_dir = os.path.abspath(sample_dir)
    contigID = "{}.{}".format(sample_id, contig)
    contigDupLog = "{0}/{1}.contig.dup.log".format(sample_dir, contigID)
    contigDupBam = "{0}/{1}.contig.dup.bam".format(sample_dir, contigID)
    contigDupMetrics = "{0}/{1}.contig.dup.metrics".format(sample_dir, contigID)

    future = picard_mark_duplicates_app(
        os.path.join(work_dir, SwagStrings.wrapper_dir, 'PicardMarkDuplicates.sh'),
        bam,
        contigID,
        sample_dir,
        outputs=[contigDupLog, contigDupBam, contigDupMetrics],
    )

    return future.outputs[1]

@bash_app
def index_bam_app(executable, bam, outputs=[], stdout=None, stderr=None):
    return executable + ' {1} {outputs[1]} {outputs[0]}'

def index_bam(work_dir, bam):
    contigIndexStr = bam.filepath;
    contigDupBamBai = "{}.bai".format(contigIndexStr)
    contigDupBamBaiLog = "{}.bai.log".format(contigIndexStr)

    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'IndexBam.sh')
    future = index_bam_app(executable, bam, outputs=[contigDupBamBaiLog, contigDupBamBai])

    return future.outputs[1]

@bash_app
def contig_merge_sort_app(executable, sample_id, sample_dir, inputs=[], outputs=[], stdout=None, stderr=None):
    bams = ' '.join(inputs)
    return executable + ' {outputs[1]} {outputs[0]} {1} {2} ' + bams

def contig_merge_sort(work_dir, bams, sample_dir, sample_id):
    genoMergeBamIndex = "{}/{}.geno.merged.bam.bai".format(sample_dir, sample_id)
    genoMergeBam = "{}/{}.geno.merged.bam".format(sample_dir, sample_id)
    genoMergeLog = "{}/{}.geno.merged.log".format(sample_dir, sample_id)

    future = contig_merge_sort_app(
        os.path.join(work_dir, SwagStrings.wrapper_dir, 'ContigMergeSort.sh'),
        sample_id,
        sample_dir,
        inputs=bams,
        outputs=[genoMergeLog, genoMergeBam, genoMergeBamIndex]
    )

    return future.outputs[1], future.outputs[2]

@bash_app
def PlatypusGerm(work_dir, sample_id, sample_dir, bam, bam_index, coords, outputs=[], stdout=None, stderr=None):
    """
    outputs = [file outVcf, file log]
    """
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'PlatypusGerm.sh')

    return executable + ' {3} {4} {outputs[0]} {outputs[1]} {1} {2} {5}'

@bash_app(executors=['threads'])
def concat_vcf_app(executable, sample_id, sample_dir, inputs=[], outputs=[], stdout=None, stderr=None):
    vcfs = ' '.join([i.filepath for i in inputs])

    return executable + ' {outputs[0]} {outputs[1]} {1} {2} ' + vcfs

def concat_vcf(work_dir, sample_id, sample_dir, genotyper, vcfs):
    concatenated_vcf = "{}/{}.merged.{}.vcf".format(sample_dir, sample_id, genotyper)
    log = "{}/{}.merged.{}.log".format(sample_dir, sample_id, genotyper)
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'ConcatVcf.sh')

    concat_vcf_app(executable, sample_id, sample_dir, inputs=vcfs, outputs=[concatenated_vcf, log]).result()


@bash_app
def samtools_flagstat_app(executable, bam, sample_id, sample_dir, outputs=[], stdout=None, stderr=None):
    log, flagstat = outputs
    template = '{executable} {bam} {flagstat} {log} {sample_id} {sample_dir}'
    return template.format(executable=executable, bam=bam, flagstat=flagstat, log=log, sample_id=sample_id, sample_dir=sample_dir)

def samtools_flagstat(work_dir, bam, sample_id, sample_dir):
    log = "{}/{}.bam.flagstat.log".format(sample_dir, sample_id)
    flagstat = "{}/{}.bam.flagstat".format(sample_dir, sample_id)

    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'samtools_flagstat.sh')
    samtools_flagstat_app(executable, bam, sample_id, sample_dir, outputs=[log, flagstat])
