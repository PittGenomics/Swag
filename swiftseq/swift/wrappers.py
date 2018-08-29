import os
import six

""" The section contains functions that will print out the various wrappers
needed for SwiftSeq computations. Each will take various params such as
algorith executables, reference files, and parameter strings that are
needed for the underlying algorithms to run """

# TODO - look into adding a random number to the tmp dirs - currentl there
#		is a possibility for conflicts

# Each wrapper has a fixed output name
# Names of the wrappers present in functions below
# Swift function names should be the same minus the ...'.sh'
"""
GatkIndelRealn.sh
GatkBqsrGrp.sh
GatkBqsrPrint.sh
GatkBqsrGrpReduce.sh
BamUtilRgSplit.sh
Flagstat.sh
PicardMarkDuplicates.sh
GetCoverage.sh
Novosort.sh
ConcatVcf.sh
SamtoolsParseContig.sh
DellyCaller.sh
SnpEff.sh
BwaAlnBam2fastq.sh
PlatypusGerm.sh
HaplotypeCaller.sh
"""


EXECUTABLE_BITS = 73  # 0b 001 001 001


def eof_check(check_filename_variable):
    """Will take a file variable name and will
    print bash code that will check the file for a valid EOF marker
    If the EOF marker is present just let the wrapper exit on own.
    Do not force an exit since other checks may occur afer the EOF
    check"""

    return ('# Check to see if the bam file has an EOF marker\n'
            'if [ `echo \\`tail -n 1 $' + check_filename_variable + ' | hexdump -ve \'1/1 "%.2x"\'\\` | '
            'tail -c56` == "f8b08040000000000ff0600424302001b0003000000000000000000" ] ; then\n'
            '\techo "EOF GOOD" >> $logFile 2>&1\n'
            'else\n'
            '\techo "EOF BAD" >> $logFile 2>&1\n'
            '\texit 1\n'
            'fi')


def no_mapped_reads_check(in_file, out_files):
    """File from map-reduce steps may carry no data. This is indicated by
    the string 'no_mapped_reads'. This must be caught within the wrappers
    to know when not to exit the algorithm required by the wrapper and
    subsequently exit gracefully. Given and input and output file variable
    name we create a string of bash code that will check for the 'no_mapped_reads'
    string and will print this to the output file if present (to propagate
    the checking behavior)

    Will take array with multiple output files"""


    return ('# Check for empty files/no data here\n'
            'if [ "$(head -1 $' + in_file + ')" == "no_mapped_reads" ]; then\n'
            '\techo "$' + in_file + ' contains no mapped reads... exiting" >> $logFile 2>&1\n'
            + ''.join(['\techo no_mapped_reads > ${}\n'.format(o) for o in out_files]) +
            '\trm -rf $tmpDir\n'
            '\texit 0\n'
            'else\n'
            '\techo "$' + in_file + ' contains mapped reads... continuing" >> $logFile 2>&1\n'
            'fi')


def get_broken_symlink_check_str(variableName):
    """Will take a file variable name and will print bash code that will
    check if the symlink for that file is broken

    This seems to be helping with files not being staged out properly.
    Likely will not be necessary in bug fixed versions of Swift

    Do not force an exit since other checks may occur afer the symlink
    check"""

    return ('# See if the symlink is orphaned... if so exit 1\n'
            'if [ ! -e $' + variableName + ' ] ; then\n'
            '\techo "$' + variableName + ' symlink good" >> $logFile 2>&1\n'
            'else\n'
            '\techo "$' + variableName + ' symlink broken" >> $logFile 2>&1\n'
            '\texit 1\n'
            'fi\n\n')


def bam_indexing(samtools, variable_name):
    """Will take a file variable name and a samtools path and will print
    bash code that will create a bam index using samtools """

    return ('# Indexing\n'
            + samtools + ' index $' + variable_name + ' >> $logFile 2>&1')


def hostname_info():
    """ Will return a string of bash code that will initialize a log file
    with the hostname where that particular job is being run"""

    return 'echo Running on... $(hostname) &> $logFile'


def gatk_contig_check():
    """ For Gatk contig style wrappers. Will create a bash sctring to
    determine if the contig is 'unmapped' and if so will set the contig
    param accordingly """

    return ('# Check for the unmapped as the contig\n'
            '# If not, write no_mapped_reads to outBam\n'
            'if [ "$contig" == "unmapped" ]; then\n'
            '\tcontigParam=""\n'
            'else\n'
            '\tcontigParam="-L $contig"\n'
            'fi')


def skip_unknown_chr():
    """Necessary for various genotyping steps"""

    return ('if [ "$coords" == "unmapped:no_mapped_reads" ]; then\n'
            '\techo "Input is the unmapped bam... exiting" >> $logFile\n'
            '\techo no_mapped_reads > $outVcf\n'
            '\texit 0\n'
            'else\n'
            '\techo "Input is not the unmapped bam... continuing" >> $logFile 2>&1\n'
            'fi')


# def get_novosort_string(novosort, numThreads, memMegaBytes, tmpDirVar, outBamVar, inBamVar):
#     """ sss"""
#
#     return (novosort + ' --threads ' + numThreads + ' --ram ' + memMegaBytes + 'M --tmpcompression 6 '
#             '--tmpdir $' + tmpDirVar + ' --output $' + outBamVar + ' --index $' + inBamVar + ' >> $logFile 2>&1\n\n')
#
#
# def get_read_group_string(samtools, inBamVar):
#     """Will print the bash command that will extract a given read group string
#     from a
#
#     THIS HAS SOME ALTERATIONS FROM THE ORIGINAL AND SHOULD BE TESTED """
#
#     return ('$(' + samtools + ' view -H $' + inBamVar + ' 2>> $logFile | '
#             'grep "@RG"| sed "s:\\t:\\\\t:g"| sed "s:\\t:\\\\t:g"\n')
#
#
# def paired_wrapper_setup():
#     ''' When production is initiated the debug statements can be removed or
#     there could be a conditional'''
#
#     return ('sourceTumor=$(pwd)/$inTumor\n'
#             'sourceNormal=$(pwd)/$inNormal\n\n'
#
#             '# Debug ##\n'
#             'echo "original tumorIn: $inTumor" >> $logFile 2>&1\n'
#             'echo "origianl normalIn: $inNormal" >> $logFile 2>&1\n'
#             'echo $(pwd) >> $logFile 2>&1\n'
#             '##########\n\n'
#
#             '# Files will be symlinked we can use thier basenames as paths\n'
#             'inTumor=$(basename $inTumor)\n'
#             'inNormal=$(basename $inNormal)\n\n'
#
#             'cd $dir\n\n'
#
#             '# Symlink tumor files since they are not in the dir\n'
#             '# This should make them available in the dir\n'
#             'ln -s $sourceTumor $tumorIn\n'
#             'ln -s $sourceNormal $normalIn\n'
#
#             '# Debug ##\n'
#             'echo "sourceTumor: $sourceTumor" >> $logFile 2>&1\n'
#             'echo "sourceNormal: $sourceNormal" >> $logFile 2>&1\n'
#             'echo "inTumor: $inTumor" >> $logFile 2>&1\n'
#             'echo "inNormal: $inNormal" >> $logFile 2>&1\n'
#             'echo $(ls -lh) >> $logFile 2>&1\n'
#             'echo $(pwd) >> $logFile 2>&1\n'
#             '##########\n\n')


###############################################
# Common sanity checks for multiple wrappers
###############################################

def getEofCheckStr(variableName):
    """Will take a file variable name and will
    print bash code that will check the file for a valid EOF marker
    If the EOF marker is present just let the wrapper exit on own.
    Do not force an exit since other checks may occur afer the EOF
    check"""

    return ('# Check to see if the bam file has an EOF marker\n'
            'if [ `echo \\`tail -n 1 $' + variableName + ' | hexdump -ve \'1/1 "%.2x"\'\\` | '
            'tail -c56` == "f8b08040000000000ff0600424302001b0003000000000000000000" ] ; then\n'
            '\techo "EOF GOOD" >> $logFile 2>&1\n'
            'else\n'
            '\techo "EOF BAD" >> $logFile 2>&1\n'
            '\texit 1\n'
            'fi\n\n')


def getNoMappedReadsStrCheck(inFile, outFiles):
    """File from map-reduce steps may carry no data. This is indicated by
    the string 'no_mapped_reads. This must be caught within the wrappers
    to know when not to exit the algorithm required by the wrapper and
    sebsequently exit gracefully. Given and input and output file variable
    name we create a string of bash code that will check for the 'no_mapped-reads'
    string and will print this to the output file if present (to propogate
    the checking behavior)

    Will take array with multiple output files"""

    noMappedCat = ''
    for outFile in outFiles:
        noMappedCat = noMappedCat + '\techo no_mapped_reads > $' + outFile + '\n'

    return ('# Check for empty files/no data here\n'
            'if [ "$(head -1 $' + inFile + ')" == "no_mapped_reads" ]; then\n'
            '\techo "$' + inFile + ' contains no mapped reads... exiting" >> $logFile 2>&1\n'
            + noMappedCat +
            '\trm -rf $tmpDir\n'
            '\texit 0\n'
            'else\n'
            '\techo "$' + inFile + ' contains mapped reads... continuing" >> $logFile 2>&1\n'
            'fi\n\n')


def getBrokenSymlinkCheckStr(variableName):
    """Will take a file variable name and will print bash code that will
    check if the symlink for that file is broken

    This seems to be helping with files not being staged out properly.
    Likely will not be necessary in bug fixed versions of Swift

    Do not force an exit since other checks may occur afer the symlink
    check"""

    return ('# See if the symlink is orphaned... if so exit 1\n'
            'if [ ! -e $' + variableName + ' ] ; then\n'
            '\techo "$' + variableName + ' symlink good" >> $logFile 2>&1\n'
            'else\n'
            '\techo "$' + variableName + ' symlink broken" >> $logFile 2>&1\n'
            '\texit 1\n'
            'fi\n\n')


def getBamIndexingString(samtools, variableName):
    """Will take a file variable name and a samtools path and will print
    bash code that will create a bam index using samtools """

    return ('# Indexing\n'
            + samtools + ' index $' + variableName + ' >> $logFile 2>&1\n\n')


def getHostnameString():
    """ Will return a string of bash code that will initialize a log file
    with the hostname where that particular job is being run"""

    return 'echo Running on... $(hostname) &> $logFile\n\n'


def getGatkContigCheckString():
    """ For Gatk contig style wrappers. Will create a bash sctring to
    determine if the contig is 'unmapped' and if so will set the contig
    param accordingly """

    return ('# Check for the unmapped as the contig\n'
            '# If not, write no_mapped_reads to outBam\n'
            'if [ "$contig" == "unmapped" ]; then\n'
            '\tcontigParam=""\n'
            'else\n'
            '\tcontigParam="-L $contig"\n'
            'fi\n\n')


def getSkipUnknownChrString():
    """Necessary for various genotyping steps"""

    return ('if [ "$coords" == "unmapped:no_mapped_reads" ]; then\n'
            '\techo "Input is the unmapped bam... exiting" >> $logFile\n'
            '\techo no_mapped_reads > $outVcf\n'
            '\texit 0\n'
            'else\n'
            '\techo "Input is not the unmapped bam... continuing" >> $logFile 2>&1\n'
            'fi\n\n')


def getNovosortString(novosort, numThreads, memMegaBytes, tmpDirVar, outBamVar, inBamVar):
    """ sss"""

    return (novosort + ' --threads ' + numThreads + ' --ram ' + memMegaBytes + 'M --tmpcompression 6 '
            '--tmpdir $' + tmpDirVar + ' --output $' + outBamVar + ' --index $' + inBamVar + ' >> $logFile 2>&1\n\n')


def getReadGroupString(samtools, inBamVar):
    """Will print the bash command that will extract a given read group string
    from a

    THIS HAS SOME ALTERATIONS FROM THE ORIGINAL AND SHOULD BE TESTED """

    return ('$(' + samtools + ' view -H $' + inBamVar + ' 2>> $logFile | '
            'grep "@RG"| sed "s:\\t:\\\\t:g"| sed "s:\\t:\\\\t:g"\n')


def pairedWrapperSetup():
    ''' When production is initiated the debug statements can be removed or
    there could be a conditional'''

    return ('sourceTumor=$(pwd)/$inTumor\n'
            'sourceNormal=$(pwd)/$inNormal\n\n'

            '# Debug ##\n'
            'echo "original tumorIn: $inTumor" >> $logFile 2>&1\n'
            'echo "origianl normalIn: $inNormal" >> $logFile 2>&1\n'
            'echo $(pwd) >> $logFile 2>&1\n'
            '##########\n\n'

            '# Files will be symlinked we can use thier basenames as paths\n'
            'inTumor=$(basename $inTumor)\n'
            'inNormal=$(basename $inNormal)\n\n'

            'cd $dir\n\n'

            '# Symlink tumor files since they are not in the dir\n'
            '# This should make them available in the dir\n'
            'ln -s $sourceTumor $tumorIn\n'
            'ln -s $sourceNormal $normalIn\n'

            '# Debug ##\n'
            'echo "sourceTumor: $sourceTumor" >> $logFile 2>&1\n'
            'echo "sourceNormal: $sourceNormal" >> $logFile 2>&1\n'
            'echo "inTumor: $inTumor" >> $logFile 2>&1\n'
            'echo "inNormal: $inNormal" >> $logFile 2>&1\n'
            'echo $(ls -lh) >> $logFile 2>&1\n'
            'echo $(pwd) >> $logFile 2>&1\n'
            '##########\n\n')


########################################
# Print wrapper functions
########################################
# All print wrapper functions will take 'parameters' even if currently no
# parameters will be passed to that function as an argument
# This will preserve flexibility for potential changes in the future

def compose_GatkIndelRealignment(app_name, **kwargs):
    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'

        'set -e\n\n'
 
        'inBam=$1\n'
        'outBam=$2\n'
        'logFile=$3\n'
        'ID=$4\n'
        'dir=$5\n'
        'contig=$6\n\n'
 
        'tmpDir={tmp_dir}/${{ID}}.${{contig}}/GatkRecal\n'
        'mkdir -p -v $tmpDir\n\n'
        
        'export PATH={env_PATH}\n\n'
        
        '{hostname_info}\n\n'
        '{no_mapped_reads_check}\n\n'
        '{gatk_contig_check}\n\n'
        '{bam_indexing}\n\n'

        '# Identify suspicious intervals\n'
        '{exe_java} -Djava.io.tmpdir=$tmpDir {gc_flag} {java_mem} -jar {exe_gatk} '
        '-I $inBam $contigParam -R {ref_ref} -T RealignerTargetCreator '
        '-known {ref_indels1kg} -known {ref_indelsMills} '  # Originally the first -known here didn't have a trailing space
        '-o $intervals  >> $logFile 2>&1\n\n'
 
        '# Perform local realingment using the intervals identified above\n'
        '{exe_java} -Djava.io.tmpdir=$tmpDir {gc_flag} {java_mem} -jar {exe_gatk} '
        '-I $inBam $contigParam -R {ref_ref} -T IndelRealigner {app_parameters} -known {ref_indels1kg} '
        '-known {ref_indelsMills} '
        '-targetIntervals $intervals -o $outBam >> $logFile 2>&1\n\n'
 
        '# Erase the temporary directory\n'
        'rm -rf $tmpDir\n\n'
        
        '{eof_check}\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            # Recycled bash snippets
            hostname_info=hostname_info(),
            no_mapped_reads_check=no_mapped_reads_check('inBam', ['outBam', 'intervals']),
            gatk_contig_check=gatk_contig_check(),
            bam_indexing=bam_indexing(exe_config['samtools'], 'inBam'),
            eof_check=eof_check('outBam'),

            # Specific programs in the configurations
            exe_java=exe_config['java-jdk'],
            exe_gatk=exe_config['gatk'],
            ref_ref=ref_config['ref'],
            ref_indels1kg=ref_config['indels1kg'],
            ref_indelsMills=ref_config['indelsMills'],

            # Rest of the format args will be in the kwargs
            **kwargs
        ),
        executable=True
    )


def compose_GatkBqsrGrp(app_name, **kwargs):
    """ NEED TO ADD CONTIG TO THE ACTUAL SWIFT CODE

    ^ Meaning it needs to be passed the name of the contig? """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'outGrp=$2\n'
           'logFile=$3\n'
           'ID=$4\n'
           'dir=$5\n\n'

           'tmpDir=$(pwd)/${ID}.${contig}/GatkRecal\n'
           'mkdir -p -v $tmpDir\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outGrp']) + '\n\n'

           + gatk_contig_check() + '\n\n'

           + bam_indexing(exe_config['samtools'], 'inBam') + '\n\n'

           '# Do base quality recalibration to produce grp file\n'
           + exe_config['java-jdk'] + ' -Djava.io.tmpdir=$tmpDir ' + kwargs.get('gc_flag') + ' ' + kwargs.get('java_mem') + ' -jar ' + exe_config[
               'gatk']
           + ' -I $inBam -R ' + ref_config['ref'] + ' -T BaseRecalibrator ' + kwargs.get('app_parameters') +
           ' -knownSites ' + ref_config['dbSnpVcf'] + ' -knownSites ' + ref_config['indelsMills']
           + ' -knownSites ' + ref_config['indels1kg'] + ' -o $outGrp >> $logFile 2>&1\n\n'

          '# Erase the temporary directory\n'
          'rm -rf $tmpDir\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_GatkBqsr(app_name, **kwargs):
    """yep"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'outBam=$2\n'
           'grp=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n\n'

           'tmpDir=$(pwd)/${ID}/GatkBqsrPrint\n'
           'mkdir -p -v $tmpDir\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outBam']) + '\n\n'

           + bam_indexing(exe_config['samtools'], 'inBam') + '\n\n'

           '# Generate recalibrated bam\n'
           + exe_config['java-jdk'] + ' -Djava.io.tmpdir=$tmpDir ' + kwargs.get('gc_flag') + ' ' + kwargs.get('java_mem')
           + ' -jar ' + exe_config['gatk'] +
           ' -I $inBam -R ' + ref_config['ref'] + ' -T PrintReads -BQSR $grp -o $outBam >> \$logFile 2>&1\n\n'

           '# Erase the temporary directory\n'
           'rm -rf $tmpDir\n\n'

           + eof_check('outBam') + '\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_GatkBqsrGrpReduce(app_name, **kwargs):
    """Don't allow this wrapper to be altered by users. Should be an
    under-the-hood process"""

    exe_config = kwargs.get('exe_config')
    grpReduce_filepath = kwargs.get('util_grpReduce').replace('.class', '')
    grpReduce_classpath = os.path.dirname(kwargs.get('util_grpReduce'))

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'outGrp=$1\n'
           'logFile=$2\n'
           'ID=$3\n'
           'dir=$4\n'
           'shift 4\n'
           '# Load grps into this variable\n'
           'inGrp=$*\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           'export CLASSPATH=' + exe_config['gatkQueue'] + ':' + grpReduce_classpath + '\n\n'

             '# Will check if bam had data in it\n'
             '# if it does not the file will not be passed to the reduce grps step\n'
             'inGrps=""\n'
             'for file in $inGrp;do\n'
             '\tif [ "$(head -1 $file)" == "no_mapped_reads" ]; then\n'
             '\t\techo $file: no_mapped_reads >> $logFile 2>&1\n'
             '\telse\n'
             '\t\tinGrps=$inGrps" "$file\n'
             '\tfi\n'
             'done\n\n'
    
             '# reduce grps\n'
           + exe_config['java-jdk'] + ' ' + grpReduce_filepath + ' $outGrp $inGrps >> $logFile 2>&1')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_SamtoolsFlagstat(app_name, **kwargs):
    """ ff"""

    exe_config = kwargs.get('exe_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'outStats=$2\n'
           'logFile=$3\n'
           'ID=$4\n'
           'dir=$5\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           '# get flagstats results\n'
           + exe_config['samtools'] + ' flagstat $inBam 2>> $logFile > $outStats\n\n'

                                   '# Could check for successful completion here')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_IndexBam(app_name, **kwargs):
    """ ff"""
    exe_config = kwargs.get('exe_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'outIndex=$2\n'
           'logFile=$3\n'
           'ID=$4\n'
           'dir=$5\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outIndex']) + '\n\n'

           '# index the bam\n'
           + exe_config['samtools'] + ' index $inBam 2>> $logFile\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_PicardMarkDuplicates(app_name, **kwargs):
    """dd"""

    exe_config = kwargs.get('exe_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'outBam=$2\n'
           'logFile=$3\n'
           'metrics=$4\n'
           'ID=$5\n'
           'dir=$6\n\n'

           'tmpDir=$(pwd)/${ID}/PicardMarkDupl\n'
           'mkdir -p -v $tmpDir\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outBam', 'metrics']) + '\n\n'

           '## Sorting should not be necessary here.. handle in aln wrappers\n\n'

           '## Here need to be sure you are specifying validation stringency in json\n'
           '## Also need to specify what should be done with duplicates\n'
           + exe_config['java-jdk'] + ' ' + kwargs.get('gc_flag') + ' ' + kwargs.get('java_mem') + ' -jar ' + exe_config[
               'picard'] + ' MarkDuplicates INPUT=$inBam '
           'OUTPUT=$outBam METRICS_FILE=$metrics TMP_DIR=$tmpDir ' + kwargs.get('app_parameters') + ' >> $logFile 2>&1\n\n'

          '# Erase the temporary directory\n'
          'rm -rf $tmpDir\n\n'

           + eof_check('outBam') + '\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_BedtoolsGenomeCoverage(app_name, **kwargs):
    """heh heh """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'outCov=$2\n'
           'outDoC=$3\n'
           'logFile=$4\n'
           'prefix=$5\n'
           'dir=$6\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n'
           'export LD_LIBRARY_PATH=' + kwargs.get('env_LD_LIBRARY_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           '# Get coverage via bedtools and grep out genome info\n'
           + exe_config['genomeCoverageBed'] + ' -ibam $inBam  -g ' + ref_config[
               'ref'] + ' | grep genome > $outCov 2>> $logFile\n'

           + exe_config['python'] + ' ' + kwargs.get('util_getDoC') + ' $outCov 2>> $logFile > $outDoC\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_RgMergeSort(app_name, **kwargs):
    """pass in contigs file, parse within wrapper

    No longer checking for EOF marker

    set -e is commented out for now"""

    exe_config = kwargs.get('exe_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        '#set -e\n\n'

        'sampleContigs=$1\n'
        'logFile=$2\n'
        'ID=$3\n'
        'dir=$4\n'
        '# Be sure this shift is properly picking up all bams\n'
        'shift 4\n'
        '# Load all the rest in this variable\n'
        'inBam=$*\n\n'
        
        'export PATH={env_PATH}\n'
        'export LD_LIBRARY_PATH={env_LD_LIBRARY_PATH}\n\n'
        
        '{hostname_info}\n\n'
        
        'tmpDir=$(pwd)\n\n'
        
        '# Will check if bam has data in it'
        '# if it does not the file will be ignored at the sorting step\n'
        'inBams=""\n'
        'counter=0\n'
        'for file in $inBam;do\n'
        '\tif [ "$(head -1 $file)" == "no_mapped_reads" ]; then\n'
        '\t\techo $file: no_mapped_reads >> $logFile 2>&1\n'
        '\telse\n'
        '\t\tcounter=$((counter+1))\n'
        '\t\tinBams=$inBams" "$file\n'
        '\tfi\n'
        'done\n\n'
        
        'absDirName=$(dirname $logFile)\n\n'
        
        '# if a single bam samtools view if multiple sambamba merge\n'
        '# Use Sambamba for merging. Sorting handled at previous steps\n'
        'if [[ $counter -eq 1 ]]; then\n'
        '\t' + exe_config['samtools'] + ' view -b $inBams'
            '| {exe_bamutil} splitChromosome --in -.bam --out ${{absDirName}}/${{ID}}.contig. --noef'
            ' 2>> $logFile\n'
        'else\n'
        '\t{exe_sambamba} merge --nthreads={max_cores} /dev/stdout $inBams 2>> $logFile '
            '| {exe_bamutil} splitChromosome --in -.bam --out ${{absDirName}}/${{ID}}.contig. --noef'
            ' 2>> $logFile\n'
        'fi\n\n'
        
        '# declare array\n'
        'declare -a outBams\n'
        '# Load file into array.\n'
        'let i=0\n'
        'while IFS=$"\n" read -r line_data; do\n'
        '\techo Contig file: ${{line_data}} >> $logFile\n'
        '\toutBams[i]="${{line_data}}"\n'
        '\t((++i))\n'
        'done < $sampleContigs\n\n'

        '# Test if the contig files exist... if not echo no_mapped_reads\n'
        'for outBam in "${{outBams[@]}}";do\n'
        '\tif [[ ! -s $outBam ]]; then\n'
        '\t\techo $outBam: no_mapped_reads >> $logFile 2>&1\n'
        '\t\techo no_mapped_reads > $outBam 2>> $logFile\n'
        '\telse\n'
        '\t\ttrue\n'
        '\tfi\n'
        'done\n\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            exe_sambamba=exe_config['sambamba'],
            # exe_novosort=exe_config['novosort'],
            exe_bamutil=exe_config['bamutil'],
            **kwargs
        ),
        executable=True
    )


# TEMPORARY SOLUTION... WILL MAKE FLEXIBLE TO SAMTOOLS AS WELL
def compose_ContigMergeSort(app_name, **kwargs):
    """This can potentially be used on contigs as well as read groups... check
    when actually using Swift"""

    exe_config = kwargs.get('exe_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        'set -e\n\n'
        
        'outBam=$1\n'
        'logFile=$2\n'
        'ID=$3\n'
        'dir=$4\n'
        '# Be sure this shift is properly picking up all bams\n'
        'shift 4\n'
        '# Load all the rest in this variable\n'
        'inBam=$*\n\n'
        
        'export PATH={env_PATH}\n'
        'export LD_LIBRARY_PATH={env_LD_LIBRARY_PATH}\n\n'
        
        '{hostname_info}\n\n'
        
        # 'tmpDir=$(pwd)/${{ID}}/NovoSortMergeSort\n'
        'tmpDir=$(pwd)/${{ID}}/SambambaMergeSort\n'
        'mkdir -p -v $tmpDir\n\n'
        
        '# Will check if bam has data in it\n'
        # '# if it does not the file will be ignored at the Novosort step\n'
        '# if it does not the file will be ignored at the Sambamba step\n'
        'inBams=""\n'
        'for file in $inBam;do\n'
        '\tif [ "$(head -1 $file)" == "no_mapped_reads" ]; then\n'
        '\t\techo $file: no_mapped_reads >> $logFile 2>&1\n'
        '\telse\n'
        '\t\tinBams=$inBams" "$file\n'
        '\tfi\n'
        'done\n\n'
        
        '# Use Sambamba merge. Contigs should already be sorted\n'
        'echo [$(date)] Sorting and indexing $inBams into $outBam >> $logFile 2>&1\n'
        '{exe_sambamba} merge --nthreads={max_cores} $outBam $inBams 2>> $logFile\n\n'

        + exe_config['samtools'] + ' index $outBam 2>> $logFile\n\n'
        
        '{eof_check}\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            eof_check=eof_check('outBam'),
            # exe_novosort=exe_config['novosort'],
            exe_sambamba=exe_config['sambamba'],
            **kwargs
        ),
        executable=True
    )


def compose_ConcatVcf(app_name, **kwargs):
    """ Uses sortByRef from GATK's Geraldine"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        '#set -e\n\n'

        'outVcf=$1\n'
        'logFile=$2\n'
        'ID=$3\n'
        'dir=$4\n'
        'shift 4\n'
        '# Load all the rest in this variable\n'
        'contigVcfs=$*\n\n'

        'export PATH={env_PATH}\n\n'

        '{hostname_info}\n\n'

        '# Will check if file had data in it\n'
        '# if it does not the file will not be passed to the reduce vcfs step\n'
        'inVcfs=""\n'
        'for file in $contigVcfs;do\n'
        '\tif [ "$(head -1 $file)" == "no_mapped_reads" ]; then\n'
        '\t\techo $file: no_mapped_reads >> $logFile 2>&1\n'
        '\telse\n'
        '\t\tinVcfs=$inVcfs" "I=$file\n'
        '\t\theaderVcf=$file\n'
        '\tfi\n'
        'done\n\n'

        '#Test if at least one vcf contains variants\n'
        'if [ "$inVcfs" == "" ]; then\n'
        '\techo All vcfs contained no_mapped_reads...exiting >> $logFile 2>&1\n'
        '\techo no_mapped_reads > $outVcf\n'
        '\texit 0\n'
        'else\n'
        '\techo At least one bam contains mapped reads...continuing... >> $logFile 2>&1\n'
        'fi\n\n'
        
        '{exe_java} {gc_flag} {java_mem} -jar {jar_picard} SortVcf $inVcfs OUTPUT=$outVcf '
        'SEQUENCE_DICTIONARY={ref_refDict}\n\n'
        
        'echo sorting complete >> $logFile\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            exe_java=exe_config['java-jdk'],
            jar_picard=exe_config['picard'],
            ref_refDict=ref_config['refDict'],
            **kwargs
        ),
        executable=True
    )


def compose_FilterVcf(app_name, **kwargs):
    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        '#set -e\n\n'
        
        'outVcf=$1\n'
        'logFile=$2\n'
        'ID=$3\n'
        'dir=$4\n'
        'inVcf=$5\n\n'
        
        'export PATH={env_PATH}\n\n'

        '{hostname_info}\n\n'
        
        '{exe_bedtools} intersect -a $inVcf -b {ref_bed} -wa > $outVcf 2> $logFile\n\n'
        
        'echo filtering VCF complete >> $logFile\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            exe_bedtools=exe_config['bedtools'],
            ref_bed=ref_config['bed'],
            **kwargs
        ),
        executable=True
    )


def compose_SamtoolsParseContig(app_name, **kwargs):
    """ ttt"""

    exe_config = kwargs.get('exe_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'inBamIndex=$2\n'
           'outBam=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n'
           'contig=$7\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           '# Check for the unmapped as the contig\n'
           'if [ "$contig" == "unmapped" ]; then\n'
           '\tcontigParam="-f 4"\n'
           'else\n'
           '\tcontigParam="$contig"\n'
           'fi\n\n'

           '# Extract each contig\n'
           + exe_config['samtools'] + ' view -b $inBam $contigParam 2>> $logFile > $outBam\n\n'

           + eof_check('outBam') +

           '# Look into the bam via samtools view and determine if the file contains\n'
           '# mapped reads. Could look into making this more efficient\n'
           'dataString=$(' + exe_config['samtools'] + ' view $outBam | head)\n'
           'if [[ $? != 0 ]]; then\n'
           '\techo "Error from samtools view on read check... exiting 1" >> $logFile 2>&1\n'
           '\texit 1\n'
           'elif [[ -n $dataString ]]; then\n'
           '\techo "bam ($outBam) contains mapped reads... exiting 0" >> $logFile 2>&1\n'
           '\texit 0\n'
           'else\n'
           '\techo "No mapped reads found in $outBam" >> $logFile 2>&1\n'
           '\t# Will subsequently check for header below\n'
           'fi\n\n'

           '# Looks to see if the outBam has a header\n'
           'dataString=$(' + exe_config['samtools'] + ' view -H $outBam)\n'
           'if [[ $? != 0 ]]; then\n'
           '\techo "Error from samtools view on read check... exiting 1" >> $logFile 2>&1\n'
           '\texit 1\n'
           'elif [[ -n $dataString ]]; then\n'
           '\techo "bam ($outBam) contains a header but no mapped reads..." >> $logFile 2>&1\n'
           '\techo "$outBam will be populated with no_mapped_reads... exiting 0" >> $logFile 2>&1\n'
           '\techo "no_mapped_reads" > $outBam\n'
           '\texit 0\n'
           'else\n'
           '\t# Likely should not ever get here\n'
           '\techo "No header found in $outBam... exiting 1" >> $logFile 2>&1\n'
           '\texit 1\n'
           'fi\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_DellyGerm(app_name, **kwargs):
    """333"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'inBamIndex=$2\n'
           'outVcf=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n'
           'analysisType=$7\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outVcf']) +

           '# Initialize delly output file... if no struct vars Delly does\n'
           '# not appear to produce a vcf\n'
           'echo no_mapped_reads > $outVcf\n\n'

           '# Call with delly\n'
           + exe_config['delly'] + ' -g ' + ref_config[
               'ref'] + ' -o $outVcf ' + kwargs.get('app_parameters') + ' -t $analysisType $inBam >> $logFile 2>&1\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_SnpEff(app_name, **kwargs):
    """Like with a few other wrappers, need to add a random component to
    the tmp dir generation... otherwise with two callers operating on
    the same chr there may be removal conflicts at this step"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inVcf=$1\n'
           'outVcf=$2\n'
           'logFile=$3\n'
           'ID=$4\n'
           'dir=$5\n\n'

           'tmpDir=$(pwd)/${ID}/snpEff\n'
           'mkdir -p -v $tmpDir\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           '# Check to see if the vcf has data\n'
           '# If not, write no_mapped_reads to outVcf\n'
           + no_mapped_reads_check('inVcf', ['outVcf']) +

           'export data_dir=$' + ref_config['snpEffDataDir'] + '\n\n'

                                                            '# Execute snpEff\n'
           + exe_config['java-jdk'] + ' -Djava.io.tmpdir=$tmpDir ' + kwargs.get('gc_flag') + ' ' + kwargs.get('java_mem') + ' -jar '
           + exe_config['snpEff'] + ' -v ' + ref_config['snpEffBuild'] + ' -c ' + ref_config['snpEffConfig'] +
           ' ' + kwargs.get('app_parameters') + ' $inVcf 2>> $logFile > $outVcf\n\n'

          '# Erase the temporary directory\n'
          'rm -rf \$tmpDir\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_BwaAln(app_name, **kwargs):
    """Note that maxCores on the sampe or samse steps assumes that bwa tpx is
    being used. May need to find a good way of handling this.

    Need to also handle the fact that novosort is not open source... will
    have to replace this with te multi-threaded version of samtools sort

    Need to change this so tpx is not used

    Removed novosort for scalability

    """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        'set -e\n\n'
        
        'inBam=$1\n'
        'outBam=$2\n'
        'readGroupStr=$3\n'
        'logFile=$4\n'
        'ID=$5\n'
        'dir=$6\n\n'
        
        'export PATH={env_PATH}\n\n'
        
        '{hostname_info}\n\n'
        
        '# Expected output here is ${{ID}}_1.fastq and ${{ID}}_2.fastq if PE\n'
        '# If SE the expected output is ${{ID}}.fastq\n'
        '# the # in -o will get replaced by _1 and _2\n'
        '{exe_bam2fastq} --force -o ${{ID}}#.fastq $inBam >> $logFile 2>&1\n\n'
        
        '\treadGroup=$(sed "s: :\\\\t:g" $readGroupStr) # NEEDS TO BE TESTED\n\n'
        
        '### Checks for PE output... will align SE vs PE accordingly\n'
        'alignPrefix=${{ID}}.bwa.tmp\n'
        'if [ $(find . -name *${{ID}}_1.fastq) ]; then\n\n'
        
        '\t# Aln first end\n'
        '{exe_bwa} aln {app_parameters} -t {max_cores} {ref_ref} ${{ID}}_1.fastq > ${{ID}}_1.sai 2>> $logFile\n\n'

        '\t# Aln second end\n'
        '{exe_bwa} aln {app_parameters} -t {max_cores} {ref_ref} ${{ID}}_2.fastq > ${{ID}}_2.sai 2>> $logFile\n\n'
        
        '\t# Coordinate pairs via sampe & insert the proper read group info\n'
        # '\t{exe_bwa} sampe -P -r "$readGroup" {ref_ref} ${{ID}}_1.sai ${{ID}}_2.sai ${{ID}}_1.fastq ${{ID}}_2.fastq '
        #     '2>> $logFile | {exe_samtools} view -b - 2>> $logFile | {exe_novosort} --threads {max_cores_div_4} '
        #     '--ram {max_mem_div_2}M --tmpcompression 6 --tmpdir $tmpDir --output $outBam --index - 2>> $logFile\n\n'
        '\t{exe_bwa} sampe -P -r "$readGroup" {ref_ref} ${{ID}}_1.sai ${{ID}}_2.sai ${{ID}}_1.fastq ${{ID}}_2.fastq '
            '2>> $logFile | {exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        'else\n'
        '\t# Aln\n'
        '\t{exe_bwa} aln {app_parameters} -t {max_cores} {ref_ref} ${{ID}}.fastq > ${{ID}}.sai 2>> $logFile\n\n'
        
        '\t# Inserts the proper read group info & samse step\n'
        # '\t{exe_bwa} samse -r $readGroup {ref_ref} ${{ID}}.sai ${{ID}}.fastq 2>> $logFile | {exe_samtools} view -b - '
        #     '2>> $logFile | {exe_novosort} --threads {max_cores_div_4} --ram {max_mem_div_2}M --tmpcompression 6 '
        #     '--tmpdir $tmpDir --output $outBam --index - 2>> $logFile\n\n'
        '\t{exe_bwa} samse -r $readGroup {ref_ref} ${{ID}}.sai ${{ID}}.fastq 2>> $logFile | {exe_samtools} view -b - '
            '2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} --memory-limit={max_mem_div_2}M '
            '--tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        'fi\n\n'
        
        '{eof_check}\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            eof_check=eof_check('outBam'),
            exe_bam2fastq=exe_config['bam2fastq'],
            exe_bwa=exe_config['bwa'],
            exe_samtools=exe_config['samtools'],
            # exe_novosort=exe_config['novosort'],
            exe_sambamba=exe_config['sambamba'],
            ref_ref=ref_config['ref'],
            max_cores_div_4=int(kwargs.get('max_cores') / 4),
            max_mem_div_2=int(kwargs.get('max_mem') / 2),
            **kwargs
        ),
        executable=True
    )


def compose_PlatypusGerm(app_name, **kwargs):
    """rrr

    LD_LIBRARY_PATH necessary for Beagle
    """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'inBamIndex=$2\n'
           'outVcf=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n'
           'coords=$7\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n'
           'export LD_LIBRARY_PATH=' + kwargs.get('env_LD_LIBRARY_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['python'] + ' ' + exe_config[
               'platypus-variant'] + ' callVariants --nCPU ' + kwargs.get('packing_cores') + ' --output $outVcf '
                                                                          '--refFile ' + ref_config[
               'ref'] + ' --regions $coords ' + kwargs.get('app_parameters') + ' --bamFiles $inBam >> $logFile 2>&1\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_ScalpelGerm(app_name, **kwargs):
    """rrr

    """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'inBamIndex=$2\n'
           'outVcf=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n'
           'coords=$7\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['scalpel'] + ' --single --bam $inBam --bed $coords --numprocs ' + str(
        int(kwargs.get('packing_cores')) * 2) +
           ' --ref ' + ref_config['ref'] + ' ' + kwargs.get('app_parameters') + ' > $outVcf 2>> $logFile\n\n'

           '# Move output to proper location\n'
           'mv ./outdir/variants.*.indel.vcf $outVcf\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_HaplotypeCaller(app_name, **kwargs):
    """eee

    This is one wrapper that needs a random component to the tmp dir.
    Could just have coords be involved

    Parallel garbage collection not used here"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'inBamIndex=$2\n'
           'outVcf=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n'
           'coords=$7\n\n'

           '# Cannot remove tmp dir at end of this script! Other processes\n'
           '# will be using that dir as tmp\n'
           'tmpDir=$(pwd)/${ID}/GatkHaplotypeCaller\n'
           'mkdir -p -v $tmpDir\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inBam', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['java-jdk'] + ' -Djava.io.tmpdir=$tmpDir ' + kwargs.get('ram_pool_mem') + ' -jar ' + exe_config['gatk4'] +
           ' -T HaplotypeCaller -R ' + ref_config['ref'] + ' -I $inBam -L $coords -nct ' + str(int(kwargs.get('packing_cores')) * 2) +
           ' --dbsnp ' + ref_config['dbSnpVcf'] + ' -o $outVcf ' + kwargs.get('app_parameters') + ' >> $logFile 2>&1\n\n'

             '# TODO - integrate this back in\n'
             '#rm -r $tmpDir\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_BwaMem(app_name, **kwargs):
    """ Need to think about how to handle maxcores with bwa
    Perhaps could use all of them... need to try that now but test other
    options later... Using bamUtil bam2fastq now...

    Currently not removing the tmp dir used by novosort... remember this
    still needs to be flexible to novosort vs samtools"""

    # String literal to fix backslash issues

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'

        'set -e\n\n'

        'inBam=$1\n'
        'outBam=$2\n'
        'RGname=$3\n'
        'logFile=$4\n'
        'ID=$5\n'
        'dir=$6\n\n'
        
        'export PATH={env_PATH}\n'
        'export LD_LIBRARY_PATH={env_LD_LIBRARY_PATH}\n\n'
        
        # 'tmpDir=$(pwd)/${{ID}}/NovoSortBwa\n'
        'tmpDir=$(pwd)/${{ID}}/SambambaBwa\n'
        'mkdir -p -v $tmpDir\n\n'
        
        '{hostname_info}\n\n'
        
        '# Get read group string... could make this cleaner\n'
        'readGroup=$({exe_samtools} view -H $inBam 2>> $logFile | grep "@RG"| grep $RGname | '
            'sed "s:\\\t:\\t:g" | sed "s:\\t:\\\\\\\\t:g")\n\n'
        
        'echo Read group: $RGname >> $logFile\n\n'
        '# Will default to PE... is wc -l > 0 then a PE run will be initiated\n'
        'numPairedReads=$({exe_samtools} view -b -r $RGname -f 0x1 $inBam | head -25000 | wc -l)\n\n'
        
        'if [ "$numPairedReads" -gt "0" ]; then\n'
        '\techo File $inBam appears to contain PAIRED END fastq data... >> $logFile\n'
        '\techo Extracting and aligning PAIRED END data... >> $logFile\n\n'
        
        '\tfastq1=${{ID}}_1.fastq\n'
        '\tfastq2=${{ID}}_2.fastq\n\n'
        
        '\t# Paired end data... rm existing and make named pipes\n'
        '\trm -f $fastq1\n'
        '\trm -f $fastq2\n\n'
        
        '\tmkfifo $fastq1\n'
        '\tmkfifo $fastq2\n\n'
        
        '\t# Unpaired fastq will be discarded into /dev/null\n'
        '\t{exe_samtools} view -b -r $RGname $inBam 2>> $logFile | {exe_bamutil} bam2FastQ --in -.bam --noeof '
            '--firstOut $fastq1 --secondOut $fastq2 --unpairedOut /dev/null 2>> $logFile &\n\n'
        
        '\t# Aln PE -M by default for Picard compatibility\n'
        # '\t{exe_bwa} mem {app_parameters} -M -t {max_cores} -R "$readGroup" {ref_ref} $fastq1 $fastq2 2>> $logFile | '
        #     '{exe_samtools} view -b - 2>> $logFile | {exe_novosort} --threads {max_cores_div_4} --ram {max_mem_div_2}M '
        #     '--tmpcompression 6 --tmpdir $tmpDir --output $outBam --index - 2>> $logFile\n\n'
        '\t{exe_bwa} mem {app_parameters} -M -t {max_cores} -R "$readGroup" {ref_ref} $fastq1 $fastq2 2>> $logFile | '
            '{exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        '\t# remove fifo variables/objects\n'
        '\trm $fastq1\n'
        '\trm $fastq2\n\n'
        'else\n'
        '\t#Will be single end\n'
        '\techo File $inBam appears to contain SINGLE END fastq data... >> $logFile\n'
        '\techo Extracting and aligning SINGLE END data... >> $logFile\n\n'
        
        '\tfastq=${{ID}}.fastq\n\n'
        
        '\t# Single end data... make named pipes\n'
        '\trm -f $fastq\n'
        '\tmkfifo $fastq\n\n'
        
        '\t# end 1 and end 2 fastq will be discarded into /dev/null\n'
        '\t{exe_samtools} view -b -r $RGname $inBam 2>> $logFile | {exe_bamutil} bam2FastQ --in -.bam --noeof '
            '--firstOut /dev/null --secondOut /dev/null --unpairedOut $fastq 2>> $logFile &\n\n'
        
        # '\t{exe_bwa} mem {app_parameters} -M -t {max_cores} -R "$readGroup" {ref_ref} $fastq 2>> $logFile | '
        #     '{exe_samtools} view -b - 2>> $logFile | {exe_novosort} --threads {max_cores_div_4} --ram {max_mem_div_2}M '
        #     '--tmpcompression 6 --tmpdir $tmpDir --output $outBam --index - 2>> $logFile\n\n'
        '\t{exe_bwa} mem {app_parameters} -M -t {max_cores} -R "$readGroup" {ref_ref} $fastq 2>> $logFile | '
            '{exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        '\t# remove fifo variables/objects\n'
        '\trm $fastq\n\n'
        
        'fi\n\n'
        
        '{eof_check}\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            eof_check=eof_check('outBam'),
            exe_samtools=exe_config['samtools'],
            exe_bamutil=exe_config['bamutil'],
            exe_bwa=exe_config['bwa'],
            # exe_novosort=exe_config['novosort'],
            exe_sambamba=exe_config['sambamba'],
            ref_ref=ref_config['ref'],
            max_cores_div_4=int(kwargs.get('max_cores') / 4),
            max_mem_div_2=int(kwargs.get('max_mem') / 2),
            **kwargs
        ),
        executable=True
    )


def compose_DellyPaired(app_name, **kwargs):
    """ Could multi-thread this with the statically linked parallel
    version of Delly. It parallelizes by samples so num threads = 2

    Parallel var set... just need the parallel statically linked binary"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'outVcf=$5\n'
           'logFile=$6\n'
           'ID=$7\n'
           'dir=$8\n'
           'analysisType=$9\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           'export OMP_NUM_THREADS=2\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['outVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Initialize delly output file... if no struct vars Delly does\n'
           '# not appear to produce a vcf\n'
           'echo no_mapped_reads > $outVcf\n\n'

           '# Call with delly\n'
           + exe_config['delly'] + ' -g ' + ref_config['ref'] + ' -o $outVcf ' + kwargs.get('app_parameters') +
           ' -t $analysisType $inTumor $inNormal >> $logFile 2>&1\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_PlatypusPaired(app_name, **kwargs):
    """ Fill this in

    LD_LIBRARY_PATH necessary for Beagle"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'outVcf=$5\n'
           'logFile=$6\n'
           'ID=$7\n'
           'dir=$8\n'
           'coords=$9\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n'
           'export LD_LIBRARY_PATH=' + kwargs.get('env_LD_LIBRARY_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['outVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['python'] + ' ' + exe_config[
               'platypus'] + ' callVariants --nCPU ' + kwargs.get('packing_cores') + ' --output $outVcf '
                                                                          '--refFile ' + ref_config[
               'ref'] + ' --regions $coords ' + kwargs.get('app_parameters') + ' --bamFiles $inTumor $inNormal >> $logFile 2>&1\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_Mutect(app_name, **kwargs):
    """ Need to be sure this is the proper way to specify coords in mutect.
    Determine if multi-threading can work for mutect and if the memory set here
    is appropriate"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'outVcf=$5\n'
           'logFile=$6\n'
           'ID=$7\n'
           'dir=$8\n'
           'coords=$9\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['outVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['java-jdk'] + ' ' + kwargs.get('gc_flag') + ' ' + kwargs.get('java_mem') + ' -jar ' + exe_config['mutect'] +
           ' --analysis_type MuTect --reference_sequence ' + ref_config['ref'] +
           ' --cosmic ' + ref_config['cosmic'] + ' --dbsnp ' + ref_config['dbSnpVcf'] +
           ' -L $coords --input_file:normal $inNormal --input_file:tumor $inTumor'
           ' --vcf $outVcf --coverage_file ${ID}.coverage.wig.txt >> $logFile 2>&1\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_ScalpelPaired(app_name, **kwargs):
    """Currently written to only return variants that are determined to
    be somatic by scalpel (i.e. will not give germline variants"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'outVcf=$5\n'
           'logFile=$6\n'
           'ID=$7\n'
           'dir=$8\n'
           'coords=$9\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['outVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['scalpel'] + ' --somatic --normal $inNormal --tumor '
                                  '$inTumor --bed $coords --ref ' + ref_config['ref'] + ' --numprocs ' + str(
        int(kwargs.get('packing_cores')) * 2) +
           ' ' + kwargs.get('app_parameters') + ' > $outVcf 2>> $logFile\n\n'

          '# Move output to proper location\n'
          'mv ./outdir/main/somatic.*.indel.vcf $outVcf\n\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_MpileupPaired(app_name, **kwargs):
    ''' Uses the multi-allelic caller by default '''

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'outVcf=$5\n'
           'logFile=$6\n'
           'ID=$7\n'
           'dir=$8\n'
           'coords=$9\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['outVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['outVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# Genotype\n'
           + exe_config['samtools'] + ' mpileup -r $coords -u ' + kwargs.get('app_parameters') + ' -f '
           + ref_config['ref'] + ' $inTumorIn $inNormal | ' + exe_config['bcftools'] +
           ' call -m -O v 2>> $logFile > $outVcf')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_Varscan(app_name, **kwargs):
    ''' Will automatically call snps and indels. They will be cat into the
    same file. in addtion, mpileup with default params is used to generate
    the pileup files '''

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')
    tmp = '/tmp/' if kwargs.get('worker_has_tmp') else ''

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'snvVcf=$5\n'
           'indelVcf=$6\n'
           'logFile=$7\n'
           'ID=$8\n'
           'dir=$9\n'
           'coords=${10}\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['snvVcf', 'indelVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['snvVcf', 'indelVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           '# create names for each pileup\n'
           'tPileup=' + tmp + '${ID}.tumor.pileup\n'
          'nPileup=' + tmp + '${ID}.normal.pileup\n\n'

             '# Commands will be executed simultaneously\n'
           + exe_config['samtools'] + ' mpileup -r $coords -f ' + ref_config['ref'] + ' $inTumor 2>> $logFile > $tPileup &\n'

           + exe_config['samtools'] + ' mpileup -r $coords -f ' + ref_config['ref'] + ' $inNormal 2>> $logFile > $nPileup\n\n'

            '# Check if either pileup is empty\n'
            'if [ -s $tPileup ]\n'
            'then\n'
            '\techo $tPileup is NOT of zero size >> $logFile\n'
            'else\n'
            '\techo $tPileup is of zero size...exiting >> $logFile\n'
            '\techo no_mapped_reads >> $snvVcf\n'
            '\techo no_mapped_reads >> $indelVcf\n'
            '\texit 0\n'
            'fi\n\n'
    
            'if [ -s $nPileup ]\n'
            'then\n'
            '\techo $nPileup is NOT of zero size >> $logFile\n'
            'else\n'
            '\techo $nPileup is of zero size...exiting >> $logFile\n'
            '\techo no_mapped_reads >> $snvVcf\n'
            '\techo no_mapped_reads >> $indelVcf\n'
            '\texit 0\n'
            'fi\n\n'

            '# Genotype - outfile will be local\n'
           + exe_config['java-jdk'] + ' -jar ' + exe_config['varscan'] + ' somatic ' + kwargs.get('app_parameters') +
           ' $nPileup $tPileup $ID 2>> $logFile\n\n'

           '# Move to the proper vcf files\n'
           'cp ${ID}.snp $snvVcf 2>> $logFile\n'
           'cp ${ID}.indel $indelVcf 2>> $logFile\n'

           '# rm pileup files\n'
           'rm -f $tPileup\n'
           'rm -f $nPileup\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_SamtoolsExtractRg(app_name, **kwargs):
    """ Fill this in """

    exe_config = kwargs.get('exe_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           '## Will get RG ID from outfile\n'
           'outBam=$2\n'
           'readGroupStr=$3\n'
           'logFile=$4\n'
           'ID=$5\n'
           'dir=$6\n'
           'RGname=$7\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           'RGID=$(basename $outBam | rev | cut -f 2 -d "." | rev)\n\n'

           'echo RGname: $RGname >> $logFile\n\n'

           '# get RG header info...\n'
           'echo $(' + exe_config['samtools'] + ' view -H $inBam 2>> $logFile | grep ^@RG | grep $RGname | '
             'sed "s:\\t:\\t:g" | sed "s:\\t:\\t:g" | sed "s: :_:g") > $readGroupStr 2>> $logFile\n'

             '# extract read group then add proper header\n'
           + exe_config['samtools'] + ' view -b -r $RGname $inBam > $outBam 2>> $logFile\n\n'

               '#Check EOF\n'
           + eof_check('outBam'))

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_BamutilPerBaseCoverage(app_name, **kwargs):
    """ Make this more flexible later... for now just have the cov stats
    being written to temp, then gzip back """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inBam=$1\n'
           'perBaseCov=$2\n'
           'logFile=$3\n'
           'ID=$4\n'
           'dir=$5\n'


           'export PATH=' + kwargs.get('env_PATH') + '\n\n'
           'export LD_LIBRARY_PATH=' + kwargs.get('env_LD_LIBRARY_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           'tmpPerBaseCov=${ID}.perBaseCov.tmp\n\n'

           '# remove and then create named pipe\n'
           'rm -f $tmpPerBaseCov\n'
           'mkfifo $tmpPerBaseCov\n\n'

           '# Generate per base coverage and stream into cut\n'
           + exe_config['bamutil'] + ' stats --cBaseQC $tmpPerBaseCov --regionsList ' + ref_config[
               'regions'] + ' --in $inBam 2>> $logFile &\n\n'

            'cut -f 1-3,11,16-17 $tmpPerBaseCov 2>> $logFile | gzip > $perBaseCov 2>> $logFile\n\n'

            'rm $tmpPerBaseCov\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_Strelka(app_name, **kwargs):
    """ need to print and pass strelka config file...

    Might need to run on a per chrom basis (not region)"""

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    write_strelka_config(
        config_path=os.path.join(kwargs.get('out_dir'), 'strelkaConfig.ini'),
        parameters=kwargs.get('app_parameters')
    )

    wrapper = ('#!/bin/bash\n\n'

           'set -e\n\n'

           'inTumor=$1\n'
           'inTumorIndex=$2\n'
           'inNormal=$3\n'
           'inNormalIndex=$4\n'
           'snvVcf=$5\n'
           'indelVcf=$6\n'
           'config=$7\n'
           'logFile=$8\n'
           'ID=$9\n'
           'dir=${10}\n\n'

           'export PATH=' + kwargs.get('env_PATH') + '\n\n'

           + hostname_info() + '\n\n'

           + no_mapped_reads_check('inTumor', ['snvVcf', 'indelVcf']) + '\n\n'

           + no_mapped_reads_check('inNormal', ['snvVcf', 'indelVcf']) + '\n\n'

           + skip_unknown_chr() + '\n\n'

           'outDir=./${ID}_strelkaAnalysis\n'
           'rm -rf $outDir\n\n'

           '#--output-dir=$outDir\n'

           'echo outDir: $outDir >> $logFile\n'
           'echo WORK: $(pwd) >> $logFile\n'
           'echo config: $config >> $logFile\n\n'

           '# Using default (./strelkaAnalysis)  output dir\n' +
           exe_config['python'] + ' ' + exe_config['strelka'] + ' --normalBam=$inNormal --tumorBam=$inTumor --referenceFasta=' + ref_config['ref'] +
           ' --config=$config --runDir=$outDir 2>> $logFile\n\n'

           'echo About to run Strelka... >> $logFile\n\n'

           'cd $outDir\n'
           'make -j ' + str(int(kwargs.get('packing_cores')) * 2) + ' 2>> $logFile\n\n'

             '# copy the results to expected output location\n'
             'cp results/passed.somatic.snvs.vcf $snvVcf 2>> $logFile\n'
             'cp results/passed.somatic.indels.vcf $indelVcf 2>> $logFile\n')

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper,
        executable=True
    )


def compose_Novoalign(app_name, **kwargs):
    """
    Wrapper for Novoalign
    """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        'set -e\n\n'
        
        'inBam=$1\n'
        'outBam=$2\n'
        'readGroupStr=$3\n'
        'logFile=$4\n'
        'ID=$5\n'
        'dir=$6\n\n'
        
        'export PATH={env_PATH}\n\n'
        
        '{hostname_info}\n\n'
        
        '# Expected output here is ${{ID}}_1.fastq and ${{ID}}_2.fastq if PE\n'
        '# If SE the expected output is ${{ID}}.fastq\n'
        '# the # in -o will get replaced by _1 and _2\n'
        '{exe_bam2fastq} --force -o ${{ID}}#.fastq $inBam >> $logFile 2>&1\n\n'
        
        '\treadGroup=$(sed "s: :\\\t:g" $readGroupStr) # NEEDS TO BE TESTED\n\n'
        
        '### Checks for PE output... will align SE vs PE accordingly\n'
        'alignPrefix=${{ID}}.bwa.tmp\n'
        'if [ $(find . -name *${{ID}}_1.fastq) ]; then\n\n'
        
        '\t{exe_novoalign} -d {ref_novoindex} -f ${{ID}}_1.fastq ${{ID}}_2.fastq -F ILMFQ 2>> $logFile | '
            '{exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        'else\n'
        
        '\t{exe_novoalign} -d {ref_novoindex} -f ${{ID}}.fastq -F ILMFQ 2>> $logFile | '
            '{exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        'fi\n\n'
        
        '{eof_check}\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            eof_check=eof_check('outBam'),
            exe_bam2fastq=exe_config['bam2fastq'],
            exe_novoalign=exe_config['novoalign'],
            exe_samtools=exe_config['samtools'],
            exe_sambamba=exe_config['sambamba'],
            ref_novoindex=ref_config['novoindex'],
            max_cores_div_4=int(kwargs.get('max_cores') / 4),
            max_mem_div_2=int(kwargs.get('max_mem') / 2),
            **kwargs
        ),
        executable=True
    )


def compose_Bowtie2(app_name, **kwargs):
    """
    Wrapper for bowtie2
    """

    exe_config = kwargs.get('exe_config')
    ref_config = kwargs.get('ref_config')

    wrapper = (
        '#!/bin/bash\n\n'
        
        'set -e\n\n'
        
        'inBam=$1\n'
        'outBam=$2\n'
        'readGroupStr=$3\n'
        'logFile=$4\n'
        'ID=$5\n'
        'dir=$6\n\n'
        
        'export PATH={env_PATH}\n\n'
        
        '{hostname_info}\n\n'
        
        '# Expected output here is ${{ID}}_1.fastq and ${{ID}}_2.fastq if PE\n'
        '# If SE the expected output is ${{ID}}.fastq\n'
        '# the # in -o will get replaced by _1 and _2\n'
        '{exe_bam2fastq} --force -o ${{ID}}#.fastq $inBam >> $logFile 2>&1\n\n'
        
        '\treadGroup=$(sed "s: :\\\t:g" $readGroupStr) # NEEDS TO BE TESTED\n\n'
        
        '### Checks for PE output... will align SE vs PE accordingly\n'
        'alignPrefix=${{ID}}.bwa.tmp\n'
        'if [ $(find . -name *${{ID}}_1.fastq) ]; then\n\n'
        
        
        '\t{exe_bowtie2} -q -x {ref_bowtie2} -1 ${{ID}}_1.fastq -2 ${{ID}}_2.fastq -p {max_cores} 2>> $logFile | '
            '{exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        'else\n'
        
        '\t{exe_bowtie2} -q -x {ref_bowtie2} -1 ${{ID}}_1.fastq -p {max_cores} 2>> $logFile | '
            '{exe_samtools} view -b - 2>> $logFile | {exe_sambamba} sort --nthreads={max_cores_div_4} '
            '--memory-limit={max_mem_div_2}M --tmpdir=$tmpDir --out=$outBam /dev/stdin 2>> $logFile\n'
        '\t{exe_sambamba} index --nthreads={max_cores_div_4} $outBam\n\n'
        
        'fi\n\n'
        
        '{eof_check}\n'
    )

    write_wrapper(
        filepath=os.path.join(kwargs.get('wrapper_dir'), app_name + '.sh'),
        contents=wrapper.format(
            hostname_info=hostname_info(),
            eof_check=eof_check('outBam'),
            exe_bam2fastq=exe_config['bam2fastq'],
            exe_bowtie2=exe_config['bowtie2'],
            exe_samtools=exe_config['samtools'],
            exe_sambamba=exe_config['sambamba'],
            ref_bowtie2=ref_config['bowtie2'],
            max_cores_div_4=int(kwargs.get('max_cores') / 4),
            max_mem_div_2=int(kwargs.get('max_mem') / 2),
            **kwargs
        ),
        executable=True
    )


################################
# Print helper functions
################################
def write_wrapper(filepath, contents, executable=False):
    # Write wrapper contents out to a file
    with open(filepath, 'w') as wrapper_file:
        wrapper_file.write(contents + '\n')

    # If this wrapper needs to be executable, set the execution bits
    if executable:
        os.chmod(filepath, os.stat(filepath).st_mode | EXECUTABLE_BITS)


def write_strelka_config(config_path, parameters):
    with open(config_path, 'w') as strelka_config:
        # Write out header
        strelka_config.write('[user]\n')

        # Write out key value pairs
        extra_args = list()
        for key, value in six.iteritems(parameters):
            if value:
                strelka_config.write('{key} = {value}\n'.format(key=key, value=value))
            else:
                extra_args.append(key)

        # Write out extra arguments (keys without values)
        strelka_config.write('extraStrelkaArguments = {extra_args}\n'.format(
            extra_args=' '.join(extra_args)
        ))
