"""
Apps and app wrappers.

The bodge of writing a wrapper for each app in order to assemble filenames is necessary due to
a limitation in Parsl [1]. As soon as that issue is fixed in Parsl, we can replace these function apps
with class apps, and eliminate the wrappers.

[1] https://github.com/Parsl/parsl/issues/483
"""

import os

import parsl
from parsl.app.app import bash_app
from swag.core import SwagStrings

@bash_app
def BwaMem(work_dir, bam, RG_name, sample_id, sample_dir, outputs=[], stdout=parsl.AUTO_LOGNAME,
        stderr=parsl.AUTO_LOGNAME):
    import os

    command = '{exe} {bam} {outfile} {RG_name} {logfile} {sample_id} {sample_dir}'.format(
        exe=os.path.join(work_dir, SwagStrings.wrapper_dir, 'BwaMem.sh'),
        bam=bam,
        outfile=str(outputs[0]),
        RG_name=RG_name,
        logfile=str(outputs[1]),
        sample_id=sample_id,
        sample_dir=sample_dir
    )

    return command

@bash_app
def RgMergeSort(work_dir, sample_id, sample_dir, inputs=[], outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):
    """
    inputs: RGalnBams
    outputs: [alnSampleContigBamFile, alnSampleBamLog, alnSampleContigBams....]
    """
    import os

    command = '{exe} {outfile} {logfile} {sample_id} {sample_dir} {bams}'.format(
        exe=os.path.join(work_dir, SwagStrings.wrapper_dir, 'RgMergeSort.sh'),
        outfile=str(outputs[0]),
        logfile=str(outputs[1]),
        sample_id=sample_id,
        sample_dir=sample_dir,
        bams=' '.join([str(i) for i in inputs])
    )

    return command

@bash_app
def picard_mark_duplicates_app(executable, bam, sample_id, sample_dir, outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):

    command = '{exe} {bam} {outfile} {logfile} {metrics} {sample_id} {sample_dir}'.format(
        exe=executable,
        bam=bam,
        outfile=str(outputs[1]),
        logfile=str(outputs[0]),
        metrics=str(outputs[2]),
        sample_id=sample_id,
        sample_dir=sample_dir
    )

    return command

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
def index_bam_app(executable, bam, outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):
    command = '{exe} {bam} {index} {log}'.format(
        exe=executable,
        bam=bam,
        index=outputs[0],
        log=outputs[1]
    )
    return command

def index_bam(work_dir, bam):
    contigIndexStr = bam.filepath;
    contigDupBamBai = "{}.bai".format(contigIndexStr)
    contigDupBamBaiLog = "{}.bai.log".format(contigIndexStr)

    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'IndexBam.sh')
    future = index_bam_app(executable, bam, outputs=[contigDupBamBai, contigDupBamBaiLog])

    return future.outputs[0]

@bash_app
def contig_merge_sort_app(executable, sample_id, sample_dir, inputs=[], outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):
    log, bam, _ = outputs

    command = '{exe} {bam} {log} {sample_id} {sample_dir} {bams}'.format(
        exe=executable,
        bam=bam,
        log=log,
        sample_id=sample_id,
        sample_dir=sample_dir,
        bams=' '.join([str(i) for i in inputs])
    )
    return command

def contig_merge_sort(work_dir, bams, sample_dir, sample_id):
    genoMergeBamIndex = "{}/{}.geno.merged.bam.bai".format(sample_dir, sample_id)
    genoMergeBam = "{}/{}.geno.merged.bam".format(sample_dir, sample_id)
    genoMergeLog = "{}/{}.geno.merged.log".format(sample_dir, sample_id)

    future = contig_merge_sort_app(
        os.path.join(work_dir, SwagStrings.wrapper_dir, 'ContigMergeSort.sh'),
        sample_id,
        sample_dir,
        inputs=bams,
        outputs=[genoMergeLog, genoMergeBam, genoMergeBamIndex],
    )

    return future.outputs[1], future.outputs[2]

@bash_app
def PlatypusGerm(work_dir, sample_id, sample_dir, bam, bam_index, coords, outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):
    """
    outputs = [file outVcf, file log]
    """
    import os
    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'PlatypusGerm.sh')

    return executable + ' {3} {4} {outputs[0]} {outputs[1]} {1} {2} {5}'

@bash_app(executors=['threads'])
def concat_vcf_app(executable, sample_id, sample_dir, inputs=[], outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):
    command = '{exe} {out_vcf} {log} {sample_id} {sample_dir} {in_vcfs}'.format(
        executable=os.path.join(work_dir, SwagStrings.wrapper_dir, 'ConcatVcf.sh'),
        out_vcf="{}/{}.merged.{}.vcf".format(sample_dir, sample_id, genotyper),
        log="{}/{}.merged.{}.log".format(sample_dir, sample_id, genotyper),
        sample_id=sample_id,
        sample_dir=sample_dir,
        in_vcfs=' '.join([i.filepath for i in inputs])
    )

    return command

def concat_vcf(work_dir, sample_id, sample_dir, genotyper, vcfs):
    concat_vcf_app(executable, sample_id, sample_dir, inputs=vcfs, outputs=[concatenated_vcf, log]).result()


@bash_app
def samtools_flagstat_app(executable, bam, sample_id, sample_dir, outputs=[], stdout=parsl.AUTO_LOGNAME, stderr=parsl.AUTO_LOGNAME):
    log, flagstat = outputs
    template = '{executable} {bam} {flagstat} {log} {sample_id} {sample_dir}'
    return template.format(executable=executable, bam=bam, flagstat=flagstat, log=log, sample_id=sample_id, sample_dir=sample_dir)

def samtools_flagstat(work_dir, bam, sample_id, sample_dir):
    log = "{}/{}.bam.flagstat.log".format(sample_dir, sample_id)
    flagstat = "{}/{}.bam.flagstat".format(sample_dir, sample_id)

    executable = os.path.join(work_dir, SwagStrings.wrapper_dir, 'samtools_flagstat.sh')
    samtools_flagstat_app(executable, bam, sample_id, sample_dir, outputs=[log, flagstat])
