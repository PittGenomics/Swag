#!/usr/bin/env python3

from execution import dfk
# Here are some conventions we will use
# 1. Any string variable holding a filepath will be prefixed by f_
# 2. Any string variable holding a dirpath will be prefixed by d_

from parsl import *

@App('bash', dfk)
def Mosaik(f_inbam=None, f_readGroupStr=None, sampleID=None, d_dir=None, outputs=[], stdout=None, stderr=None):
    cmd_line = 'sleep 3; echo {f_inbam} {outputs[0]} {sampleID} {d_dir};'

'''
# NOT CURRENTLY FUNCTIONAL wrapper needs adjustment mosaikAlnBam2FastqWrapper
app (file logFile, file outBam, file outBamBai) Mosaik (file inBam, file readGroupStr, string sampleID, string dir) {
	Mosaik filename(inBam) filename(outBam) filename(logFile) sampleID dir;
}

# bwaAln (does Bam2Fastq)
app (file logFile, file outBam, file outBamBai) BwaAln (file inBam, file readGroupStr, string sampleID, string dir) {
	BwaAln filename(inBam) filename(outBam) filename(readGroupStr) filename(logFile) sampleID dir;
}

# bwaMem (does Bam2Fastq)
app (file logFile, file outBam, file outBamBai) BwaMem (file inBam, string RGname, string sampleID, string dir) {
	BwaMem filename(inBam) filename(outBam) RGname filename(logFile) sampleID dir;
}

# mergeSort for read group files
app (file logFile, file [] outBams, file sampleContigs) RgMergeSort (file [] inBam, string sampleID, string dir) {
	RgMergeSort filename(sampleContigs) filename(logFile) sampleID dir filenames(inBam);
}

# Base quality recalibration
app (file logFile, file outBam, file outBamGrp) GatkBqsr (file inBam, string sampleID, string dir) {
	GatkBqsr filename(inBam) filename(outBam) filename(logFile) filename(outBamGrp) sampleID dir;
}

# Mark duplicates
app (file logFile, file outBam, file outBamMetrics) PicardMarkDuplicates (file inBam, string sampleID, string dir) {
	PicardMarkDuplicates filename(inBam) filename(outBam) filename(logFile) filename(outBamMetrics) sampleID dir;
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
