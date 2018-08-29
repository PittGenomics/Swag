"""
The modules and classes in swag.parsl have to do with writing out parsl code.
"""


def printParslApps(FH):
    '''All Parsl scripts will contain all possible apps '''

    Str = ('####################\n'
           '#### Parsl Apps ####\n'
           '####################\n'

           '# NOT CURRENTLY FUNCTIONAL wrapper needs adjustment mosaikAlnBam2FastqWrapper\n'
           'app (file logFile, file outBam, file outBamBai) Mosaik (file inBam, file readGroupStr, string sampleID, string dir) {\n'
           '\tMosaik filename(inBam) filename(outBam) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '# bwaAln (does Bam2Fastq)\n'
           'app (file logFile, file outBam, file outBamBai) BwaAln (file inBam, file readGroupStr, string sampleID, string dir) {\n'
           '\tBwaAln filename(inBam) filename(outBam) filename(readGroupStr) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '# bwaMem (does Bam2Fastq)\n'
           'app (file logFile, file outBam, file outBamBai) BwaMem (file inBam, string RGname, string sampleID, string dir) {\n'
           '\tBwaMem filename(inBam) filename(outBam) RGname filename(logFile) sampleID dir;\n'
           '}\n\n'

           '# mergeSort for read group files\n'
           'app (file logFile, file [] outBams, file sampleContigs) RgMergeSort (file [] inBam, string sampleID, string dir) {\n'
           '\tRgMergeSort filename(sampleContigs) filename(logFile) sampleID dir filenames(inBam);\n'
           '}\n\n'

           '# Base quality recalibration\n'
           'app (file logFile, file outBam, file outBamGrp) GatkBqsr (file inBam, string sampleID, string dir) {\n'
           '\tGatkBqsr filename(inBam) filename(outBam) filename(logFile) filename(outBamGrp) sampleID dir;\n'
           '}\n\n'

           '# Mark duplicates\n'
           'app (file logFile, file outBam, file outBamMetrics) PicardMarkDuplicates (file inBam, string sampleID, string dir) {\n'
           '\tPicardMarkDuplicates filename(inBam) filename(outBam) filename(logFile) filename(outBamMetrics) sampleID dir;\n'
           '}\n\n'

           '# flagstat\n'
           'app (file logFile, file outStats) SamtoolsFlagstat (file inBam, string sampleID, string dir) {\n'
           '\tSamtoolsFlagstat filename(inBam) filename(outStats) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '# flagstat\n'
           'app (file logFile, file outCov) BamutilPerBaseCoverage (file inBam, string sampleID, string dir) {\n'
           '\tBamutilPerBaseCoverage filename(inBam) filename(outCov) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '# getCoverage\n'
           'app (file logFile, file coverage, file DoC) BedtoolsGenomeCoverage (file inBam, string sampleID, string dir) {\n'
           '\tBedtoolsGenomeCoverage filename(inBam) filename(coverage) filename(DoC) filename(logFile) sampleID dir;\n'
           '}\n\n'


           '###########################\n'
           '### Scatter-gather apps ###\n'
           '###########################\n'
           '### Indel realingment\n'
           'app (file logFile, file outBam) GatkIndelRealnment (file inBam, string sampleID, string dir, string contigName) {\n'
           '\tGatkIndelRealnment filename(inBam) filename(outBam) filename(logFile) sampleID dir contigName;\n'
           '}\n\n'

           '### Base quality recalibration - create grp\n'
           'app (file logFile, file outBamGrp) GatkBqsrGrp (file inBam, string sampleID, string dir) {\n'
           '\tGatkBqsrGrp filename(inBam) filename(outBamGrp) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '### Base quality recalibration - print reads to bam\n'
           'app (file logFile, file outBam) GatkBqsrPrint (file inBam, file inGrp, string sampleID, string dir) {\n'
           '\tGatkBqsrPrint filename(inBam) filename(outBam) filename(inGrp) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '### mergeSort for scatter-gathered contigs\n'
           'app (file logFile, file outBam, file outBamBai) ContigMergeSort (file[string] inBams, string sampleID, string dir) {\n'
           '\tContigMergeSort filename(outBam) filename(logFile) sampleID dir filenames(inBams);\n'
           '}\n\n'

           '### merge grp files\n'
           'app (file logFile, file outGrp) MergeGrp (file [] grpFiles, string sampleID, string dir) {\n'
           '\tMergeGrp filename(outGrp) filename(logFile) sampleID dir filenames(grpFiles);\n'
           '}\n\n'

           '### HaplotypeCaller\n'
           'app (file logFile, file outVcf) HaplotypeCaller (file inBam, file inBamIndex, string sampleID, string dir, string coords) {\n'
           '\tHaplotypeCaller filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir coords;\n'
           '}\n\n'

           '### Platypus Caller\n'
           'app (file logFile, file outVcf) PlatypusGerm (file inBam, file inBamIndex, string sampleID, string dir, string coords) {\n'
           '\tPlatypusGerm filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir coords;\n'
           '}\n\n'

           '### concat vcf files\n'
           'app (file logFile, file outVcf) ConcatVcf (file [auto] vcfFiles, string sampleID, string dir) {\n'
           '\tConcatVcf filename(outVcf) filename(logFile) sampleID dir filenames(vcfFiles);\n'
           '}\n\n'

           '### Break into contigs\n'
           'app (file logFile, file outBam) SamtoolsParseContig (file inBam, file inBamIndex, string sampleID, string dir, string contigName) {\n'
           '\tSamtoolsParseContig filename(inBam) filename(inBamIndex) filename(outBam) filename(logFile) sampleID dir contigName;\n'
           '}\n\n'

           '### Annotate with snpEff\n'
           'app (file logFile, file outVcf) SnpEff (file inVcf, string sampleID, string dir) {\n'
           '\tSnpEff filename(inVcf) filename(outVcf) filename(logFile) sampleID dir;\n'
           '}\n\n'

           '### Extract the RG\n'
           'app (file logFile, file readGroupStr, file outBam) SamtoolsExtractRg (file inBam, string RGID, string dir, string RGname) {\n'
           '\tSamtoolsExtractRg filename(inBam) filename(outBam) filename(readGroupStr) filename(logFile) RGID dir RGname;\n'
           '}\n\n'

           '### Delly Caller\n'
           'app (file logFile, file outVcf) DellyGerm (file inBam, file inBamIndex, string sampleID, string dir, string analysisType) {\n'
           '\tDellyGerm filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir analysisType;\n'
           '}\n\n'

           '### mpileup Tumor vs Normal genotyping\n'
           'app (file logFile, file outVcf) MpileupPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tMpileupPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Delly Tumor vs Normal genotyping\n'
           'app (file logFile, file outVcf) DellyPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tDellyPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Mutect Tumor vs Normal genotyping\n'
           'app (file logFile, file outVcf) Mutect (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tMutect filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Caveman Tumor vs Normal genotyping\n'
           'app (file logFile, file outVcf) Caveman (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tCaveman filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Platypus Tumor vs Normal genotyping\n'
           'app (file logFile, file outVcf) PlatypusPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tPlatypusPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Scalpel Tumor vs Normal indel genotyping\n'
           'app (file logFile, file outVcf) ScalpelPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tScalpelPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Scalpel germline indel caller\n'
           'app (file logFile, file outVcf) ScalpelGerm (file inBam, file inBamIndex, string sampleID, string dir, string coords) {\n'
           '\tScalpelGerm filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir coords;\n'
           '}\n\n'

           '### Obtain index\n'
           'app (file logFile, file outIndex) IndexBam (file inBam) {\n'
           '\tIndexBam filename(inBam) filename(outIndex) filename(logFile);\n'
           '}\n\n'

           '### Varscan Tumor vs Normal genotyping\n'
           'app (file logFile, file snvVcf, file indelVcf) Varscan (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {\n'
           '\tVarscan filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(snvVcf) filename(indelVcf) filename(logFile) runID dir coords;\n'
           '}\n\n'

           '### Strelka Tumor vs Normal genotyping\n'
           'app (file logFile, file snvVcf, file indelVcf) Strelka (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, file config, string runID, string dir) {\n'
           '\tStrelka filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(snvVcf) filename(indelVcf) filename(config) filename(logFile) runID dir;\n'
           '}\n\n')

    FH.write(Str)

def printCustomStructs(FH, paired):
    """ These same structs will be printed for each Parsl script"""

    if paired:
        sample = ('type Sample {\n'
                  '\tstring ID;\n'
                  '\tstring sampleDir;\n'
                  '\tstring dir;\n'
                  '\tstring filepath;\n'
                  '}\n\n')

    else:  # if germline
        sample = ('type Sample {\n'
                  '\tstring ID;\n'
                  '\tstring dir;\n'
                  '}\n\n')

    Str = ('##################\n'
           '# Custom Structs #\n'
           '##################\n'

           '# ID is the name of the samples stripped of .bam\n'
           '# dir is the path to samples analysis directory\n'
           '# sampleDir is the name of directory that holds the input file (typically bam)\n\n'

           'type file;\n\n'

           'type Patient {\n'
           '\tstring patient;\n'
           '\tstring dir;\n'
           '}\n\n'

           + sample +

           '# Will use an associative array for contigs\n'
           'type PairedSample {\n'
           '\tfile[string] contigBams;\n'
           '\tfile[string] contigBamsIndex;\n'
           '\tfile wholeBam;\n'
           '\tfile wholeBamIndex;\n'
           '\tstring ID;\n'
           '\tstring dir;\n'
           '\tstring sampleDir;\n'
           '}\n\n')

    FH.write(Str)
