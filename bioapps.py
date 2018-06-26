#!/usr/bin/env python3

from execution import dfk
# Here are some conventions we will use
# 1. Any string variable holding a filepath will be prefixed by f_
# 2. Any string variable holding a dirpath will be prefixed by d_

from parsl import *

AppPaths = { 'BwaMem' : '/share/swiftseq/run/wrappers/BwaMem.sh',
             'BwaAln' : '/share/swiftseq/run/wrappers/BwaAln.sh',
             'RgMergeSort' : '/share/swiftseq/run/wrappers/RgMergeSort.sh',
             'PicardMarkDuplicates' : '/share/swiftseq/run/wrappers/PicardMarkDuplicates.sh',
             'PlatypusGerm' : '/share/swiftseq/run/wrappers/PlatypusGerm.sh',
             'IndexBam' : '/share/swiftseq/run/wrappers/IndexBam.sh'
           }

_AppPaths = { 'BwaMem' : 'echo',
              'BwaAln' : 'echo',
              'RgMergeSort' : 'echo',
              'PicardMarkDuplicates' : 'echo',
              'PlatypusGerm' : 'echo',
              'IndexBam' : 'echo'
          }

@App('bash', dfk, cache=True)
def Mosaik(f_inbam=None, f_readGroupStr=None, sampleID=None, d_dir=None,
           wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
           outputs=[], stdout=None, stderr=None, mock=False):
    '''
    outputs = [file logFile, file outBam, file outBamBai]
    '''
    if mock == True:
        return 'echo "export PATH={wrapperDir}:$PATH; Mosaik {f_inbam} {outputs[1]} {outputs[0]} {sampleID} {d_dir}"';
    else:
        return '''export PATH={wrapperDir}:$PATH; 
        Mosaik {f_inbam} {outputs[1]} {outputs[0]} {sampleID} {d_dir}''';


# bwaMem (does Bam2Fastq)
@App('bash', dfk, cache=True)
def BwaMem(inBam, RGname, sampleID, dirpath, outputs=[],
           wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
           stdout=None, stderr=None, mock=False):
    if mock == True:
        return 'echo "export PATH={wrapperDir}:$PATH; BwaMem.sh {0} {outputs[0]} {1} {outputs[1]} {2} {3};"'
    else:
        return '''export PATH={wrapperDir}:$PATH;
        BwaMem.sh {0} {outputs[0]} {1} {outputs[2]} {2} {3};'''

@App('bash', dfk, cache=True)
def RgMergeSort (sampleID, dirpath, inputs=[], outputs=[],
                 wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
                 stdout=None, stderr=None, mock=False):
    '''
    inputs : RGalnBams
    outputs : [alnSampleContigBamFile, alnSampleBamLog, alnSampleContigBams....]
    '''

    inBams = ' '.join([i.filename for i in inputs])
    if mock == True:
        return 'echo "export PATH={wrapperDir}:$PATH; RgMergeSort.sh {outputs[0]} {outputs[1]} {0} %s "' % inBams
    else:
        return '''export PATH={wrapperDir}:$PATH; 
        RgMergeSort.sh {outputs[0]} {outputs[1]} {0} %s ''' % inBams

@App('bash', dfk, cache=True)
def PicardMarkDuplicates (inBam, sampleID, dirpath, inputs=[], outputs=[],
                          wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
                          stdout=None, stderr=None, mock=False):
    '''
    outputs = [file logFile, file outBam, file outBamMetrics]
    '''
    if mock == True:
        return 'echo "export PATH={wrapperDir}:$PATH; PicardMarkDuplicates.sh {0} {outputs[1]} {outputs[0]} {outputs[2]} {1} {2}"'
    else:
        return '''export PATH={wrapperDir}:$PATH; 
        PicardMarkDuplicates.sh {0} {outputs[1]} {outputs[0]} {outputs[2]} {1} {2}'''



@App('bash', dfk, cache=True)
def PlatypusGerm (inBam,inBamIndex, sampleID, dirpath, coords, outputs=[],
                  wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
                  stdout=None, stderr=None, mock=False):
    '''
    outputs = [file logFile, file outVcf]
    '''
    if mock == True:
        return 'echo "export PATH={wrapperDir}:$PATH; PlatypusGerm.sh {0} {1} {outputs[1]} {outputs[0]} {2} {3} {4};"'
    else:
        return '''export PATH={wrapperDir}:$PATH;
        PlatypusGerm.sh {0} {1} {outputs[1]} {outputs[0]} {2} {3} {4}; '''

@App('bash', dfk, cache=True)
def IndexBam (inBam, outputs=[], stdout=None, stderr=None,
              wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
              mock=False):
    '''
    outputs = [file logFile, file outIndex]
    '''
    if mock == True:
        return 'echo "export PATH={wrapperDir}:$PATH; IndexBam.sh {0} {outputs[1]} {outputs[0]};"'
    else:
        return '''export PATH={wrapperDir}:$PATH; 
        IndexBam.sh {0} {outputs[1]} {outputs[0]};'''

'''
### mergeSort for scatter-gathered contigs
app (file logFile, file outBam, file outBamBai) ContigMergeSort (file[string] inBams, string sampleID, string dir) {
ContigMergeSort filename(outBam) filename(logFile) sampleID dir filenames(inBams);
}
'''

@App('bash', dfk, cache=True)
def ContigMergeSort (sampleID, dirpath, inputs=[], outputs=[],
                     wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
                     stdout=None, stderr=None, mock=False):
    '''
    outputs = [file logFile, file outBam, file outBamBai]
    '''

    inBams = ' '.join(inputs)

    if mock == True:
        return '''echo "export PATH={wrapperDir}:$PATH; ContigMergeSort.sh {outputs[1]}  \
        {outputs[0]} \
        {0} \
        {1} \
        %s "''' % inBams

    else:
        return '''export PATH={wrapperDir}:$PATH; ContigMergeSort.sh {outputs[1]}  \
        {outputs[0]} \
        {0} \
        {1} \
        %s ''' % inBams

@App('bash', dfk, cache=True)
def ConcatVcf (sampleID, dirpath, inputs=[], outputs=[],
               wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
               stdout=None, stderr=None, mock=False):
    '''
### concat vcf files
app (file logFile, file outVcf) ConcatVcf (file [auto] vcfFiles, string sampleID, string dir) {
    ConcatVcf filename(outVcf) filename(logFile) sampleID dir filenames(vcfFiles);
}

    outputs = [file logFile, file outIndex]
    '''
    vcfs = ' '.join([i.filename for i in inputs])

    if mock == True:
        return '''echo "export PATH={wrapperDir}:$PATH; ConcatVcf.sh {outputs[1]} \
        {outputs[0]} \
        {0} \
        {1} \
        %s"
        ''' % vcfs

    else:
        return '''export PATH={wrapperDir}:$PATH; ConcatVcf.sh {outputs[1]} \
        {outputs[0]} \
        {0} \
        {1} \
        %s
        ''' % vcfs

@App('bash', dfk, cache=True)
def SamtoolsFlagstat (genoMergeBam, sampleID, sampleDir, outputs=[],
                      wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
                      stdout=None, stderr=None, mock=False):
    '''
    outputs = [file flagstatLog, file flagstat]
    SamtoolsFlagstat filename(inBam) filename(outStats) filename(logFile) sampleID dir;
    '''

    if mock == True:
        return '''echo "export PATH={wrapperDir}:$PATH; SamtoolsFlagstat.sh {0} {outputs[1]} \
        {outputs[0]} \
        {1} \
        {2}"'''

    else:
        return '''export PATH={wrapperDir}:$PATH; SamtoolsFlagstat.sh {0} {outputs[1]} \
        {outputs[0]} \
        {1} \
        {2}'''

@App('bash', dfk, cache=True)
def BamutilPerBaseCoverage(genoMergeBam, sampleID, sampleDir, outputs=[],
                           wrapperDir="/home/ubuntu/SwiftSeq/test_run/wrapper",
                           stdout=None, stderr=None, mock=False):
    '''
    outputs = [file flagstatLog, file flagstat]
    BamutilPerBaseCoverage filename(inBam) filename(outCov) filename(logFile) sampleID dir;
    '''

    if mock == True:
        return '''echo "export PATH={wrapperDir}:$PATH; BamutilPerBaseCoverage.sh {0} {outputs[1]} \
        {outputs[0]} \
        {1} \
        {2}"'''

    else:
        return '''echo "export PATH={wrapperDir}:$PATH; BamutilPerBaseCoverage.sh {0} {outputs[1]} {outputs[0]} {1} {2}"
export PATH={wrapperDir}:$PATH; BamutilPerBaseCoverage.sh {0} {outputs[1]} {outputs[0]} {1} {2}
'''



'''
### Obtain index
app (file logFile, file outIndex) IndexBam (file inBam) {
        IndexBam filename(inBam) filename(outIndex) filename(logFile);
}



# NOT CURRENTLY FUNCTIONAL wrapper needs adjustment mosaikAlnBam2FastqWrapper
app (file logFile, file outBam, file outBamBai) Mosaik (file inBam, file readGroupStr, string sampleID, string dir) {
        Mosaik filename(inBam) filename(outBam) filename(logFile) sampleID dir;
}

# bwaAln (does Bam2Fastq)
app (file logFile, file outBam, file outBamBai) BwaAln (file inBam, file readGroupStr, string sampleID, string dir) {
        BwaAln filename(inBam) filename(outBam) filename(readGroupStr) filename(logFile) sampleID dir;
}


# mergeSort for read group files
app (file logFile, file [] outBams, file sampleContigs) RgMergeSort (file [] inBam, string sampleID, string dir) {
        RgMergeSort filename(sampleContigs) filename(logFile) sampleID dir filenames(inBam);
}

# Base quality recalibration
app (file logFile, file outBam, file outBamGrp) GatkBqsr (file inBam, string sampleID, string dir) {
        GatkBqsr filename(inBam) filename(outBam) filename(logFile) filename(outBamGrp) sampleID dir;
}


# flagstat
app (file logFile, file outStats) SamtoolsFlagstat (file inBam, string sampleID, string dir) {
        SamtoolsFlagstat filename(inBam) filename(outStats) filename(logFile) sampleID dir;
}

# flagstat
app (file logFile, file outCov) BamutilPerBaseCoverage (file inBam, string sampleID, string dir) {
        BamutilPerBaseCoverage filename(inBam) filename(outCov) filename(logFile) sampleID dir;
}

# getCoverage
app (file logFile, file coverage, file DoC) BedtoolsGenomeCoverage (file inBam, string sampleID, string dir) {
        BedtoolsGenomeCoverage filename(inBam) filename(coverage) filename(DoC) filename(logFile) sampleID dir;
}
'''
