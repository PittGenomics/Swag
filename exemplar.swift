####################
#### Swift Apps ####
####################
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

###########################
### Scatter-gather apps ###
###########################
### Indel realingment
app (file logFile, file outBam) GatkIndelRealnment (file inBam, string sampleID, string dir, string contigName) {
	GatkIndelRealnment filename(inBam) filename(outBam) filename(logFile) sampleID dir contigName;
}

### Base quality recalibration - create grp
app (file logFile, file outBamGrp) GatkBqsrGrp (file inBam, string sampleID, string dir) {
	GatkBqsrGrp filename(inBam) filename(outBamGrp) filename(logFile) sampleID dir;
}

### Base quality recalibration - print reads to bam
app (file logFile, file outBam) GatkBqsrPrint (file inBam, file inGrp, string sampleID, string dir) {
	GatkBqsrPrint filename(inBam) filename(outBam) filename(inGrp) filename(logFile) sampleID dir;
}

### mergeSort for scatter-gathered contigs
app (file logFile, file outBam, file outBamBai) ContigMergeSort (file[string] inBams, string sampleID, string dir) {
	ContigMergeSort filename(outBam) filename(logFile) sampleID dir filenames(inBams);
}

### merge grp files
app (file logFile, file outGrp) MergeGrp (file [] grpFiles, string sampleID, string dir) {
	MergeGrp filename(outGrp) filename(logFile) sampleID dir filenames(grpFiles);
}

### HaplotypeCaller
app (file logFile, file outVcf) HaplotypeCaller (file inBam, file inBamIndex, string sampleID, string dir, string coords) {
	HaplotypeCaller filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir coords;
}

### Platypus Caller
app (file logFile, file outVcf) PlatypusGerm (file inBam, file inBamIndex, string sampleID, string dir, string coords) {
	PlatypusGerm filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir coords;
}

### concat vcf files
app (file logFile, file outVcf) ConcatVcf (file [auto] vcfFiles, string sampleID, string dir) {
	ConcatVcf filename(outVcf) filename(logFile) sampleID dir filenames(vcfFiles);
}

### Break into contigs
app (file logFile, file outBam) SamtoolsParseContig (file inBam, file inBamIndex, string sampleID, string dir, string contigName) {
	SamtoolsParseContig filename(inBam) filename(inBamIndex) filename(outBam) filename(logFile) sampleID dir contigName;
}

### Annotate with snpEff
app (file logFile, file outVcf) SnpEff (file inVcf, string sampleID, string dir) {
	SnpEff filename(inVcf) filename(outVcf) filename(logFile) sampleID dir;
}

### Extract the RG
app (file logFile, file readGroupStr, file outBam) SamtoolsExtractRg (file inBam, string RGID, string dir, string RGname) {
	SamtoolsExtractRg filename(inBam) filename(outBam) filename(readGroupStr) filename(logFile) RGID dir RGname;
}

### Delly Caller
app (file logFile, file outVcf) DellyGerm (file inBam, file inBamIndex, string sampleID, string dir, string analysisType) {
	DellyGerm filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir analysisType;
}

### mpileup Tumor vs Normal genotyping
app (file logFile, file outVcf) MpileupPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	MpileupPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;
}

### Delly Tumor vs Normal genotyping
app (file logFile, file outVcf) DellyPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	DellyPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;
}

### Mutect Tumor vs Normal genotyping
app (file logFile, file outVcf) Mutect (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	Mutect filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;
}

### Caveman Tumor vs Normal genotyping
app (file logFile, file outVcf) Caveman (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	Caveman filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;
}

### Platypus Tumor vs Normal genotyping
app (file logFile, file outVcf) PlatypusPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	PlatypusPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;
}

### Scalpel Tumor vs Normal indel genotyping
app (file logFile, file outVcf) ScalpelPaired (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	ScalpelPaired filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(outVcf) filename(logFile) runID dir coords;
}

### Scalpel germline indel caller
app (file logFile, file outVcf) ScalpelGerm (file inBam, file inBamIndex, string sampleID, string dir, string coords) {
	ScalpelGerm filename(inBam) filename(inBamIndex) filename(outVcf) filename(logFile) sampleID dir coords;
}

### Obtain index
app (file logFile, file outIndex) IndexBam (file inBam) {
	IndexBam filename(inBam) filename(outIndex) filename(logFile);
}

### Varscan Tumor vs Normal genotyping
app (file logFile, file snvVcf, file indelVcf) Varscan (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, string runID, string dir, string coords) {
	Varscan filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(snvVcf) filename(indelVcf) filename(logFile) runID dir coords;
}

### Strelka Tumor vs Normal genotyping
app (file logFile, file snvVcf, file indelVcf) Strelka (file inTumorBam, file inTumorBamIndex, file inNormalBam, file inNormalBamIndex, file config, string runID, string dir) {
	Strelka filename(inTumorBam) filename(inTumorBamIndex) filename(inNormalBam) filename(inNormalBamIndex) filename(snvVcf) filename(indelVcf) filename(config) filename(logFile) runID dir;
}

##################
# Custom Structs #
##################
# ID is the name of the samples stripped of .bam
# dir is the path to samples analysis directory
# sampleDir is the name of directory that holds the input file (typically bam)

type file;

type Patient {
	string patient;
	string dir;
}

type Sample {
	string ID;
	string dir;
}

# Will use an associative array for contigs
type PairedSample {
	file[string] contigBams;
	file[string] contigBamsIndex;
	file wholeBam;
	file wholeBamIndex;
	string ID;
	string dir;
	string sampleDir;
}

string genomeContigs [] = readData("analysis/Reference/contigs.txt");

# Just the id with the directory, all files in that directory belong to the same sample
Sample samples [] = readData(strcat("analysis/individuals.txt"));
foreach sample, sampleIndex in samples {


	# INPUT - Unaligned input files (including read groups)
	file inBam <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam")>;

	## Read group bams
	# reads in the data file containing read group names
	string sampleRGs [] = readData(strcat(sample.dir,"/","RGfiles.txt"));

	# Map all of the read group strings to a file array

	# File array of RG bams to be used by mergesort
	file RGalnBams [];

	foreach sampleRG, idx in sampleRGs {
		# root file name for the RG
		string RGID = strcut(sampleRG, ".*/(.*).bam");
		string RGname = regexp(RGID, strcat(sample.ID, "."), "");

		# Step is necessary because the simple mapper does not take array elements as lvalues
		# Changed this to include sample.dir
		file RGalnBam <single_file_mapper; file=strcat(sample.dir,"/",RGID,".aln.bam")>;
		file RGalnBai <single_file_mapper; file=strcat(sample.dir,"/",RGID,".aln.bam.bai")>;
		file RGalnLog <single_file_mapper; file=strcat(sample.dir,"/",RGID,".aln.log")>;

		# Converting to fastq will occur within the alignment wrapper
		# Allow SwiftSeq to be agnostic about single vs paired-end reads
		(RGalnLog,RGalnBam,RGalnBai) = BwaMem (inBam,RGname,RGID,sample.dir);

		# Map realigned file to an array
		RGalnBams[idx] = RGalnBam;
	}

	# Read in the names of the contig bams... will be abs filepath
	# Needs to start as a string array, then mapped to a file array
	# per swift language constraint...
	file alnSampleContigBamFile <single_file_mapper; file=strcat(sample.dir,"/","sampleContigs.txt")>;
	string alnSampleContigBamsStr [] = readData(strcat(sample.dir,"/","sampleContigs.txt"));
	file alnSampleContigBams [] <array_mapper; files=alnSampleContigBamsStr>;

	tracef("%M", alnSampleContigBams[0]);
	# Mergesort the readgroups from this sample
	file alnSampleBamLog <single_file_mapper;  file=strcat(sample.dir,"/",sample.ID,".RGmerge.log")>;

	(alnSampleBamLog, alnSampleContigBams, alnSampleContigBamFile) = RgMergeSort (RGalnBams, sample.ID, sample.dir);

	file[auto] PlatypusGermContigVcfs;
	file[string] contigBams;
	file[string] contigBamsIndex;

	# Processed (genotyping ready) contig bams will be stored here
	foreach contigName, idx in genomeContigs {
		# id for each contig
		# ".aln" has been removed to improve flexibility
		string contigID = strcat(sample.ID,".",contigName);

		# rm dup
		file contigDupLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,".contig.dup.log")>;
		file contigDupBam <single_file_mapper; file=strcat(sample.dir,"/",contigID,".contig.dup.bam")>;
		file contigDupMetrics <single_file_mapper; file=strcat(sample.dir,"/",contigID,".contig.dup.metrics")>;
		(contigDupLog,contigDupBam,contigDupMetrics) = PicardMarkDuplicates (alnSampleContigBams[idx],contigID,sample.dir);

		string contigSegments [] = readData(strcat("/share/swiftseq/run/analysis/Reference/contig_segments_",contigName,".txt"));
		foreach contigSegment in contigSegments {

			# Get coordinate info
			string coords = strcat(contigName,":",contigSegment);
			string segmentSuffix = strcat(".",contigName,"_",contigSegment);

			file PlatypusGermContigVcf <single_file_mapper; file=strcat(sample.dir,"/",contigID,segmentSuffix,".PlatypusGerm.vcf")>;
			file PlatypusGermContigVcfLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,segmentSuffix,".PlatypusGerm.log")>;
			(PlatypusGermContigVcfLog,PlatypusGermContigVcf) = PlatypusGerm (contigDupBam,contigDupBamBai,contigID,sample.dir,coords);

			# Append contig vcfs to array
			PlatypusGermContigVcfs << PlatypusGermContigVcf;

		}

		# get dir for genoBam... should convert file path to str
		string contigIndexStr = @contigDupBam;
		file contigDupBamBai <single_file_mapper; file=strcat(contigIndexStr,".bai")>;
		file contigDupBamBaiLog <single_file_mapper; file=strcat(contigIndexStr,".bai.log")>;
		(contigDupBamBaiLog,contigDupBamBai) = IndexBam (contigDupBam);

		contigBams[contigName] = contigDupBam;
		contigBamsIndex[contigName] = contigDupBamBai;

	}# End of contig

	# Mergesort the geno contig bams
	file genoMergeBamIndex <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".geno.merged.bam.bai")>;
	file genoMergeBam <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".geno.merged.bam")>;
	file genoMergeLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".geno.merged.log")>;
	(genoMergeLog,genoMergeBam,genoMergeBamIndex) = ContigMergeSort (contigBams,sample.ID,sample.dir);

	# Cat together the PlatypusGerm contig vcf files
	file PlatypusGermMergedVcf <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.PlatypusGerm.vcf")>;
	file PlatypusGermMergedVcfLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.PlatypusGerm.log")>;
	(PlatypusGermMergedVcfLog,PlatypusGermMergedVcf) = ConcatVcf (PlatypusGermContigVcfs,sample.ID,sample.dir);

	# Flagstat on the geno-ready aligned bam (genoMergeBam)
	file flagstatLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.flagstat.log")>;
	file flagstat <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.flagstat")>;
	(flagstatLog,flagstat) = SamtoolsFlagstat (genoMergeBam,sample.ID,sample.dir);

	# Per base coverage on the geno-ready aligned bam (genoMergeBam)
	file perBaseCoverageLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.perBaseCoverage.log")>;
	file perBaseCoverage <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.perBaseCoverage")>;
	(perBaseCoverageLog,perBaseCoverage) = BamutilPerBaseCoverage (genoMergeBam,sample.ID,sample.dir);

}# End of sample

