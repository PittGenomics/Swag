import logging
import os

from swag.core import SwagStrings
from swag.util import read_data
import swag.parsl.apps
######################
# COMMENTS / To-do
######################
# Currently all files will remain in their respective directories - can
# subset this by analysis type at a later date
# All of these functions could be cleaned up and proper comments added

logger = logging.getLogger(__name__)

def printGrpFilenames(FH, tabCount):
    ''' fff '''

    tabs = tabCount * '\t'
    Str = (tabs + 'file mergedGrp <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp")>;\n' +
           tabs + 'file mergeGrpLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp.log")>;\n' +
           tabs + 'file grpFiles [];\n\n')

    FH.write(Str)
    return


def printGatkAppCalls(FH, tabCount, inputBam):
    ''' fff '''

    tabs = tabCount * '\t'

    Str = (tabs + '# Re-align around putative indels\n' +
           tabs + 'file indelRealnBam <single_file_mapper; file=strcat(sample.dir,"/",contigID,".indelRealn.bam")>;\n' +
           tabs + 'file indelRealnLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,".indelRealn.log")>;\n' +
           tabs + '(indelRealnLog,indelRealnBam) = GatkIndelRealnment (' + inputBam + ',contigID,sample.dir,contigName);\n\n' +

           tabs + '# BQSR mk grp table\n' +
           tabs + 'file bqRecalGrp <single_file_mapper; file=strcat(sample.dir,"/",contigID,".contig.grp")>;\n' +
           tabs + 'file bqRecalGrpLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,".contig.grp.log")>;\n' +
           tabs + '(bqRecalGrpLog,bqRecalGrp) = GatkBqsrGrp (indelRealnBam,contigID,sample.dir);\n\n' +

           tabs + '# will be merged into a single grp\n' +
           tabs + 'grpFiles[idx] = bqRecalGrp;\n\n' +

           tabs + '###################################################################\n' +
           tabs + '#### These steps will not execute until the single grp is made ####\n' +
           tabs + '#### This will happen outside of this for loop with mergeGrp   ####\n' +
           tabs + '###################################################################\n\n' +

           tabs + '# Apply recalibration\n' +
           tabs + '# Use merged grp created outside of this for loop\n' +
           tabs + 'file bqsrContigBam <single_file_mapper; file=strcat(sample.dir,"/",contigID,".bqsr.bam")>;\n' +
           tabs + 'file bqsrContigBamLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,".bqsr.log")>;\n' +
           tabs + '(bqsrContigBamLog,bqsrContigBam) = GatkBsqrPrint (indelRealnBam,mergedGrp,contigID,sample.dir);\n\n')

    FH.write(Str)
    return 'bqsrContigBam'


def printReduceGrpAppCall(FH, tabCount):
    ''' fff '''

    tabs = tabCount * '\t'

    Str = (tabs + '# Reduce GRP tables\n' +
           tabs + '### Steps in above loop are dependent on this app ###\n' +
           tabs + '(mergeGrpLog,mergedGrp) = MergeGrp (grpFiles,sample.ID,sample.dir);\n\n')

    FH.write(Str)
    return


def printVcfArray(FH, tabCount, genotyper):
    ''' ffff '''

    tabs = tabCount * '\t'
    Str = tabs + 'file[auto] ' + genotyper + 'ContigVcfs;\n'

    FH.write(Str)
    return


def printDualVcfArray(FH, tabCount, genotyper):
    ''' ffff '''

    tabs = tabCount * '\t'
    Str = (tabs + 'file[auto] ' + genotyper + 'SnvContigVcfs;\n' +
           tabs + 'file[auto] ' + genotyper + 'IndelContigVcfs;\n')

    FH.write(Str)
    return



def printReduceVcfApp(FH, tabCount, genotyper, sampleDir, sampleID):
    ''' ddd '''

    tabs = tabCount * '\t'

    Str = (tabs + '# Cat together the ' + genotyper + ' contig vcf files\n' +
           tabs + 'file ' + genotyper + 'MergedVcf <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".merged.' + genotyper + '.vcf")>;\n' +
           tabs + 'file ' + genotyper + 'MergedVcfLog <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".merged.' + genotyper + '.log")>;\n' +
           tabs + '(' + genotyper + 'MergedVcfLog,' + genotyper + 'MergedVcf) = ConcatVcf (' + genotyper + 'ContigVcfs,' + sampleID + ',' + sampleDir + ');\n\n')

    FH.write(Str)
    return


def printDualReduceVcfApp(FH, tabCount, genotyper, sampleDir, sampleID):
    ''' ddd '''

    tabs = tabCount * '\t'

    Str = (tabs + '# Cat together the ' + genotyper + ' snv contig vcf files\n' +
           tabs + 'file ' + genotyper + 'SnvMergedVcf <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".merged.' + genotyper + '.snv.vcf")>;\n' +
           tabs + 'file ' + genotyper + 'SnvMergedVcfLog <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".merged.' + genotyper + '.snv.log")>;\n' +
           tabs + '(' + genotyper + 'SnvMergedVcfLog,' + genotyper + 'SnvMergedVcf) = ConcatVcf (' + genotyper + 'SnvContigVcfs,' + sampleID + ',' + sampleDir + ');\n\n' +

           tabs + '# Cat together the ' + genotyper + ' indel contig vcf files\n' +
           tabs + 'file ' + genotyper + 'IndelMergedVcf <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".merged.' + genotyper + '.indel.vcf")>;\n' +
           tabs + 'file ' + genotyper + 'IndelMergedVcfLog <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".merged.' + genotyper + '.indel.log")>;\n' +
           tabs + '(' + genotyper + 'IndelMergedVcfLog,' + genotyper + 'IndelMergedVcf) = ConcatVcf (' + genotyper + 'IndelContigVcfs,' + sampleID + ',' + sampleDir + ');\n\n')

    FH.write(Str)
    return


def printDellyApp(FH, tabCount, genoBam, genoBamIndex):
    ''' Still need to determine how translocations are handled

    May have to run TRA on the bam in its entirety

    Not sure this is functioing in the germline sense'''

    tabs = tabCount * '\t'

    Str = (tabs + '### Delly\n' +
           tabs + '# dellyAnalysisTypes does not need to be defined in this loop\n' +
           tabs + 'string dellyAnalysisTypes [] = ["DEL", "DUP", "INV"];\n' +
           tabs + 'file[auto] dellyContigTypeVcfs;\n' +
           tabs + 'foreach analysisType in dellyAnalysisTypes {\n\n' +

           tabs + '\t' + 'file dellyContigTypeVcf <single_file_mapper; file=strcat(sample.dir,"/",contigID,".",analysisType,".delly.vcf")>;\n' +
           tabs + '\t' + 'file dellyContigTypeVcfLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,".",analysisType,".delly.log")>;\n' +
           tabs + '\t' + '(dellyContigTypeVcfLog,dellyContigTypeVcf) = DellyGerm (' + genoBam + ',' + genoBamIndex + ',contigID,sample.dir,analysisType);\n\n' +

           tabs + '\t' + 'dellyContigTypeVcfs << dellyContigTypeVcf;\n' +
           tabs + '} # End Delly analysis type\n\n' +
           tabs + '# Merge analysis type Delly vcfs\n' +
           tabs + 'file dellyContigVcf <single_file_mapper; file=strcat(sample.dir,"/",contigID,".delly.vcf")>;\n' +
           tabs + 'file dellyContigVcfLog <single_file_mapper; file=strcat(sample.dir,"/",contigID,".delly.log")>;\n' +
           tabs + '(dellyContigVcfLog,dellyContigVcf) = ConcatVcf (dellyContigTypeVcfs,sample.ID,sample.dir);\n\n' +

           tabs + '# Add to contig list of vcfs\n' +
           tabs + 'DellyGermContigVcfs << dellyContigVcf;\n\n')

    FH.write(Str)
    return



def align(in_bam, work_dir, aligner_app, mergesort_app, sample_id, sample_dir):
    ## Align read groups and merge-sort
    sample_RGs = read_data(os.path.join(sample_dir, SwagStrings.readgroups_out_filename))
    RG_IDs = read_data(os.path.join(sample_dir, SwagStrings.readgroups_ids_out_filename))
    RG_align_bams = [] # RG bams to be used by mergesort

    for sample_RG, RG_ID in zip(sample_RGs, RG_IDs):
        label = sample_RG.rsplit('/', 1)[1].strip('.bam')

        RG_align_bam = os.path.abspath(os.path.join(sample_dir, "{}.aln.bam".format(label)))
        RG_align_log = os.path.abspath(os.path.join(sample_dir, "{}.aln.log".format(label)))
        RG_align_bai = os.path.abspath(os.path.join(sample_dir, "{}.aln.bam.bai".format(label)))
        future = aligner_app(
            work_dir,
            in_bam,
            RG_ID,
            sample_id,
            sample_dir,
            outputs=[RG_align_bam, RG_align_log, RG_align_bai],
        )

        RG_align_bams.append(future.outputs[0])

    alnSampleBamLog = os.path.abspath(os.path.join(sample_dir, '{}.RGmerge.log'.format(sample_id)))
    alnSampleContigBamFile = os.path.abspath(os.path.join(sample_dir, "sampleContigs.txt"))
    alnSampleContigBams = read_data(alnSampleContigBamFile)

    futures = mergesort_app(
        work_dir,
        sample_id,
        sample_dir,
        inputs=RG_align_bams,
        outputs=[alnSampleContigBamFile, alnSampleBamLog] + alnSampleContigBams,
        stdout=alnSampleBamLog + '.stdout',
        stderr=alnSampleBamLog + '.stderr'
    )

    return futures.outputs[2:]

def perform_quality_control(work_dir, bam, sample_dir, sample_id, app_names):
    apps = [getattr(swag.parsl.apps, a) for a in app_names]
    for app in apps:
        app(work_dir, bam, sample_id, sample_dir)

def single_sample_genotype(work_dir, genotyper, contig, segment, ref_dir, bam, bam_index, sample_dir, sample_id):
    contig_id = "{}.{}".format(sample_id, contig)
    coords = "{}:{}".format(contig, segment)

    contig_vcf = "{}/{}.{}_{}.{}.vcf".format(sample_dir, contig_id, contig, segment, genotyper)
    contig_vcf_log = "{}/{}.{}_{}.{}.log".format(sample_dir, contig_id, contig, segment, genotyper)

    app = getattr(swag.parsl.apps, genotyper)
    future = app(
        work_dir,
        sample_id,
        sample_dir,
        bam,
        bam_index,
        coords,
        outputs=[contig_vcf, contig_vcf_log]
    )
    return  future.outputs[0]

def printGermBamArrayAssignment(FH, tabCount, contig, genoBam, genoBamIndex):
    ''' ddd '''

    tabs = tabCount * '\t'

    Str = (tabs + '# get dir for genoBam... should convert file path to str\n' +
           tabs + 'string contigIndexStr = @' + genoBam + ';\n' +
           tabs + 'file ' + genoBam + 'Bai <single_file_mapper; file=strcat(contigIndexStr,".bai")>;\n' +
           tabs + 'file ' + genoBam + 'BaiLog <single_file_mapper; file=strcat(contigIndexStr,".bai.log")>;\n' +
           tabs + '(' + genoBam + 'BaiLog,' + genoBam + 'Bai) = IndexBam (' + genoBam + ');\n\n' +

           tabs + 'contigBams[' + contig + '] = ' + genoBam + ';\n' +
           tabs + 'contigBamsIndex[' + contig + '] = ' + genoBamIndex + ';\n\n')

    FH.write(Str)
    return


########################################################################
# Functions specific to tumor-normal pairs
########################################################################

def printPairedSetup(FH, tabCount, contigsFile, patientDataFile, sampleDataFile):
    '''hh '''

    tabs = tabCount * '\t'

    Str = (tabs + 'string tissues [] = ["tumor", "normal"];\n' +
           tabs + 'string genomeContigs [] = readData("' + contigsFile + '");\n\n' +

           tabs + '# Just the id with the directory, all files in that directory belong to the same sample\n' +
           tabs + 'Patient patients [] = readData("' + patientDataFile + '");\n' +
           tabs + 'foreach patient in patients {\n' +
           tabs + (1 * '\t') + '# Initialize array of structs per patient\n' +
           tabs + (1 * '\t') + '# Will now be indexed with sampleIndex\n' +
           tabs + (1 * '\t') + 'PairedSample tumorArray [];\n' +
           tabs + (1 * '\t') + 'PairedSample normalArray [];\n' +
           tabs + (1 * '\t') + 'foreach tissue in tissues {\n' +
           tabs + (2 * '\t') + '# Get samples for particular tissue\n' +
           tabs + (
               2 * '\t') + 'Sample samples [] = readData(strcat(patient.dir,"/",tissue,"/' + sampleDataFile + '"));\n' +
           tabs + (2 * '\t') + 'foreach sample, sampleIndex in samples {\n\n' +

           tabs + (3 * '\t') + '##################################\n' +
           tabs + (3 * '\t') + '# Initialize PairedSample struct #\n' +
           tabs + (3 * '\t') + '# Populate with sample metadata  #\n' +
           tabs + (3 * '\t') + '##################################\n' +
           tabs + (3 * '\t') + '# bam contigs will be appended to pairedSampleData.contigBams\n' +
           tabs + (3 * '\t') + 'PairedSample pairedSampleData;\n' +
           tabs + (3 * '\t') + 'pairedSampleData.ID = sample.ID;\n' +
           tabs + (3 * '\t') + 'pairedSampleData.dir = sample.dir;\n' +
           tabs + (3 * '\t') + 'pairedSampleData.sampleDir = sample.sampleDir;\n\n')

    FH.write(Str)
    return


def printPairedBamArrayAssignment(FH, tabCount, contig, genoBam):
    '''Do indexing here ... could be changed to speed up tasks on clouds '''

    tabs = tabCount * '\t'

    Str = (tabs + '# get dir for genoBam... should convert file path to str\n' +
           tabs + 'string contigIndexStr = @' + genoBam + ';\n' +
           tabs + 'file ' + genoBam + 'Bai <single_file_mapper; file=strcat(contigIndexStr,".bai")>;\n' +
           tabs + 'file ' + genoBam + 'BaiLog <single_file_mapper; file=strcat(contigIndexStr,".bai.log")>;\n' +
           tabs + '(' + genoBam + 'BaiLog,' + genoBam + 'Bai) = IndexBam (' + genoBam + ');\n\n' +

           tabs + 'contigBamsIndex[' + contig + '] = ' + genoBam + 'Bai;\n' +
           tabs + 'contigBams[' + contig + '] = ' + genoBam + ';\n\n')

    FH.write(Str)
    return


def printPairedDellyTransApp(FH, tabCount, mergedTumorBam, mergedTumorBamIndex, mergedNormalBam, mergedNormalBamIndex):
    ''' Still need to determine how translocations are handled

    Have to run TRA on the bam in its entirety '''

    tabs = tabCount * '\t'

    Str = (tabs + '### Delly\n' +
           tabs + '# dellyAnalysisTypes does not need to be defined in this loop\n' +
           tabs + 'string traAnalysis = "TRA";\n' +
           tabs + 'file dellyTransVcf <single_file_mapper; file=strcat(outDir,"/",patient.patient,".",traAnalysis,".delly.vcf")>;\n' +
           tabs + 'file dellyTransVcfLog <single_file_mapper; file=strcat(outDir,"/",patient.patient,".",traAnalysis,".delly.log")>;\n' +
           tabs + '(dellyTransVcfLog,dellyTransVcf) = DellyPaired (' + mergedTumorBam + ',' + mergedTumorBamIndex + ',' + mergedNormalBam + ',' + mergedNormalBamIndex + ',patient.patient,outDir,traAnalysis);\n\n' +

           tabs + '# Add translocation vcf to contig vcfs\n' +
           tabs + 'DellyPairedContigVcfs << dellyTransVcf;\n\n')

    FH.write(Str)
    return


def printGermDellyTransApp(FH, tabCount, mergedBam, mergedBamIndex):
    ''' Still need to determine how translocations are handled

    Have to run TRA on the bam in its entirety '''

    tabs = tabCount * '\t'

    Str = (tabs + '### Delly\n' +
           tabs + '# dellyAnalysisTypes does not need to be defined in this loop\n' +
           tabs + 'string traAnalysis = "TRA";\n' +
           tabs + 'file dellyTransVcf <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".",traAnalysis,".delly.vcf")>;\n' +
           tabs + 'file dellyTransVcfLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".",traAnalysis,".delly.log")>;\n' +
           tabs + '(dellyTransVcfLog,dellyTransVcf) = DellyGerm (' + mergedBam + ',' + mergedBamIndex + ',sample.ID,sample.dir,traAnalysis);\n\n' +

           tabs + '# Add translocation vcf to contig vcfs\n' +
           tabs + 'DellyGermContigVcfs << dellyTransVcf;\n\n')

    FH.write(Str)
    return


def printPairedDellyContigApp(FH, tabCount):
    ''' With translocations have to run TRA on the bam in its entirety '''

    tabs = tabCount * '\t'

    Str = (tabs + '### Delly\n' +
           tabs + '# dellyAnalysisTypes does not need to be defined in this loop\n' +
           tabs + 'string dellyAnalysisTypes [] = ["DEL", "DUP", "INV"];\n' +
           tabs + 'file[auto] dellyContigTypeVcfs;\n' +
           tabs + 'foreach analysisType in dellyAnalysisTypes {\n\n' +

           tabs + (
               1 * '\t') + 'file dellyContigTypeVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".",analysisType,".delly.vcf")>;\n' +
           tabs + (
               1 * '\t') + 'file dellyContigTypeVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,".",analysisType,".delly.log")>;\n' +
           tabs + (
               1 * '\t') + '(dellyContigTypeVcfLog,dellyContigTypeVcf) = DellyPaired (tumorSample.contigBams[contigName],tumorSample.contigBamsIndex[contigName],normalSample.contigBams[contigName],normalSample.contigBamsIndex[contigName],contigID,outDir,analysisType);\n\n' +

           tabs + (1 * '\t') + 'dellyContigTypeVcfs << dellyContigTypeVcf;\n' +
           tabs + '} # End Delly analysis type\n\n' +
           tabs + '# Merge analysis type Delly vcfs\n' +
           tabs + 'file dellyContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".delly.vcf")>;\n' +
           tabs + 'file dellyContigVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,".delly.log")>;\n' +
           tabs + '(dellyContigVcfLog,dellyContigVcf) = ConcatVcf (dellyContigTypeVcfs,contigID,outDir);\n\n' +

           tabs + '# Add to contig list of vcfs\n' +
           tabs + 'DellyPairedContigVcfs << dellyContigVcf;\n\n')

    FH.write(Str)
    return


def printPairedGenotyperApp(FH, tabCount, genotyper):
    ''' These apps coccur by contig segment... the by contig apps will be specified elsewhere
    (similar to Delly with SVs)'''

    tabs = tabCount * '\t'

    # Strelka should never be passed to this function since it is per contig!
    dualOutputGenotypers = getDualOutputGenotypers()

    if genotyper in dualOutputGenotypers:

        Str = (
            tabs + 'file ' + genotyper + 'SnvContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,segmentSuffix,".' + genotyper + '.snv.vcf")>;\n' +
            tabs + 'file ' + genotyper + 'IndelContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,segmentSuffix,".' + genotyper + '.indel.vcf")>;\n' +
            tabs + 'file ' + genotyper + 'ContigVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,segmentSuffix,".' + genotyper + '.log")>;\n' +
            tabs + '(' + genotyper + 'ContigVcfLog,' + genotyper + 'SnvContigVcf,' + genotyper + 'IndelContigVcf) = ' + genotyper + ' (tumorSample.contigBams[contigName],tumorSample.contigBamsIndex[contigName],normalSample.contigBams[contigName],normalSample.contigBamsIndex[contigName],contigID,outDir,coords);\n\n' +

            tabs + '# Append contig vcfs to array\n' +
            tabs + genotyper + 'SnvContigVcfs << ' + genotyper + 'SnvContigVcf;\n' +
            tabs + genotyper + 'IndelContigVcfs << ' + genotyper + 'IndelContigVcf;\n\n')
    else:

        Str = (
            tabs + 'file ' + genotyper + 'ContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,segmentSuffix,".' + genotyper + '.vcf")>;\n' +
            tabs + 'file ' + genotyper + 'ContigVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,segmentSuffix,".' + genotyper + '.log")>;\n' +
            tabs + '(' + genotyper + 'ContigVcfLog,' + genotyper + 'ContigVcf) = ' + genotyper + ' (tumorSample.contigBams[contigName],tumorSample.contigBamsIndex[contigName],normalSample.contigBams[contigName],normalSample.contigBamsIndex[contigName],contigID,outDir,coords);\n\n' +

            tabs + '# Append contig vcfs to array\n' +
            tabs + genotyper + 'ContigVcfs << ' + genotyper + 'ContigVcf;\n\n')

    FH.write(Str)
    return


def printPairedGenotyperContigApp(FH, tabCount, genotyper):
    ''' These apps coccur by CONTIG... '''

    tabs = tabCount * '\t'

    # Strelka not included since it is not run by contig segment
    dualOutputGenotypers = getDualOutputGenotypers()

    if genotyper in dualOutputGenotypers:

        # Strelka config needs to be passed in... will be defined as a file at the beginning of workflow
        if genotyper == 'Strelka':
            Str = (
                tabs + 'file ' + genotyper + 'SnvContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.snv.vcf")>;\n' +
                tabs + 'file ' + genotyper + 'IndelContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.indel.vcf")>;\n' +
                tabs + 'file ' + genotyper + 'ContigVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.log")>;\n' +
                tabs + '(' + genotyper + 'ContigVcfLog,' + genotyper + 'SnvContigVcf,' + genotyper + 'IndelContigVcf) = ' + genotyper + ' (tumorSample.contigBams[contigName],tumorSample.contigBamsIndex[contigName],normalSample.contigBams[contigName],normalSample.contigBamsIndex[contigName],strelkaConfig,contigID,outDir);\n\n' +

                tabs + '# Append contig vcfs to array\n' +
                tabs + genotyper + 'SnvContigVcfs << ' + genotyper + 'SnvContigVcf;\n' +
                tabs + genotyper + 'IndelContigVcfs << ' + genotyper + 'IndelContigVcf;\n\n')

        else:
            Str = (
                tabs + 'file ' + genotyper + 'SnvContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.snv.vcf")>;\n' +
                tabs + 'file ' + genotyper + 'IndelContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.indel.vcf")>;\n' +
                tabs + 'file ' + genotyper + 'ContigVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.log")>;\n' +
                tabs + '(' + genotyper + 'ContigVcfLog,' + genotyper + 'SnvContigVcf,' + genotyper + 'IndelContigVcf) = ' + genotyper + ' (tumorSample.contigBams[contigName],tumorSample.contigBamsIndex[contigName],normalSample.contigBams[contigName],normalSample.contigBamsIndex[contigName],contigID,outDir);\n\n' +

                tabs + '# Append contig vcfs to array\n' +
                tabs + genotyper + 'SnvContigVcfs << ' + genotyper + 'SnvContigVcf;\n' +
                tabs + genotyper + 'IndelContigVcfs << ' + genotyper + 'IndelContigVcf;\n\n')
    else:

        Str = (
            tabs + 'file ' + genotyper + 'ContigVcf <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.vcf")>;\n' +
            tabs + 'file ' + genotyper + 'ContigVcfLog <single_file_mapper; file=strcat(outDir,"/",contigID,".' + genotyper + '.log")>;\n' +
            tabs + '(' + genotyper + 'ContigVcfLog,' + genotyper + 'ContigVcf) = ' + genotyper + ' (tumorSample.contigBams[contigName],tumorSample.contigBamsIndex[contigName],normalSample.contigBams[contigName],normalSample.contigBamsIndex[contigName],contigID,outDir);\n\n' +

            tabs + '# Append contig vcfs to array\n' +
            tabs + genotyper + 'ContigVcfs << ' + genotyper + 'ContigVcf;\n\n')

    FH.write(Str)
    return


def printAssignPairedData(FH, tabCount):
    ''' ddd '''

    tabs = tabCount * '\t'

    Str = (tabs + '# Assign struct to struct array based on the tissue\n' +
           tabs + 'if(tissue == "tumor") {\n' +
           tabs + (1 * '\t') + 'tumorArray[sampleIndex] = pairedSampleData;\n' +
           tabs + '} else {\n' +
           tabs + (1 * '\t') + '# Will be normal\n' +
           tabs + (1 * '\t') + 'normalArray[sampleIndex] = pairedSampleData;\n' +
           tabs + '}\n\n')

    FH.write(Str)
    return


def printPairedContigMergeSort(FH, tabCount, name, sampleDir, sampleID):
    ''' Merge-sort and assign to struct ... any merge-sort app should return both the
    merge-sorted bam as well as the index'''

    tabs = tabCount * '\t'

    Str = (tabs + 'pairedSampleData.contigBamsIndex = contigBamsIndex;\n' +
           tabs + 'pairedSampleData.contigBams = contigBams;\n\n' +

           tabs + '# Mergesort the ' + name + ' contig bams\n' +
           tabs + 'file ' + name + 'MergeBamIndex <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".' + name + '.merged.bam.bai")>;\n' +
           tabs + 'file ' + name + 'MergeBam <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".' + name + '.merged.bam")>;\n' +
           tabs + 'file ' + name + 'MergeLog <single_file_mapper; file=strcat(' + sampleDir + ',"/",' + sampleID + ',".' + name + '.merged.log")>;\n' +
           tabs + '(' + name + 'MergeLog,' + name + 'MergeBam,' + name + 'MergeBamIndex) = ContigMergeSort (contigBams,' + sampleID + ',' + sampleDir + ');\n\n' +

           tabs + 'pairedSampleData.wholeBamIndex = ' + name + 'MergeBamIndex;\n' +
           tabs + 'pairedSampleData.wholeBam = ' + name + 'MergeBam;\n\n')

    FH.write(Str)
    return (name + 'MergeBam')


########################################################################
# Paired contig/genotyping functions
########################################################################
# !# This code needs to be cleaned up and clarified


def printPairedGenoContigs(FH, tabCount, pairedAnalysisDir, refDir, genotypers, structVarCallers):
    ''' sss '''

    # genotypers that create a snv and indel vcf
    dualOutputGenotypers = getDualOutputGenotypers()
    contigGenotypers = getContigGenotypers()

    tabs = tabCount * '\t'

    Str = ('\n' + tabs + 'foreach contigName in genomeContigs {\n' +
           tabs + (1 * '\t') + 'string contigID = strcat(patient.patient, ".", contigName);\n' +
           tabs + (1 * '\t') + '# read in segment strings for the desired contig\n' +
           tabs + (
               1 * '\t') + 'string contigSegments [] = readData(strcat("' + refDir + '/contig_segments_", contigName, ".txt"));\n\n' +

           tabs + (1 * '\t') + 'foreach contigSegment in contigSegments {\n' +
           tabs + (
               2 * '\t') + '# Need to be sure the coords argument works for all of the software we will be using\n' +
           tabs + (2 * '\t') + 'string coords = strcat(contigName,":",contigSegment);\n' +
           tabs + (2 * '\t') + 'string segmentSuffix = strcat(".",contigName,"_",contigSegment);\n\n' +

           tabs + (2 * '\t') + '# Create output files & perform genotyping\n\n')

    FH.write(Str)

    # If genotyping is not to be performed it will just be an empty array
    for genotyper in genotypers:
        if genotyper not in contigGenotypers:
            printPairedGenotyperApp(FH, tabCount + 2, genotyper)  # bam names are assumed in the app

    closeBracket(FH, tabCount + 1, '# End segment')  # close segment

    ###############
    # PER CONTIG
    ###############
    # SV per contig/chromosome
    # If structVar is not to be performed it will just be an empty array
    for structVarCaller in structVarCallers:
        printPairedDellyContigApp(FH, tabCount + 1)  # bam names are assumed

    for genotyper in genotypers:
        if genotyper in contigGenotypers:
            printPairedGenotyperContigApp(FH, tabCount + 1, genotyper)  # bam names are assumed in the app

    closeBracket(FH, tabCount, '# End contig')

    return


def printPairedGeno(FH, tabCount, pairedAnalysisDir, refDir, genotypers, structVarCallers):
    ''' Will need to add in struct var here as well... at least with Delly
    Will need to reduce and annotate in this function also'''

    # genotypers that create a snv and indel vcf
    dualOutputGenotypers = getDualOutputGenotypers()

    # tuple
    printPairedGenoSetup(FH, tabCount, pairedAnalysisDir, refDir)  # tumor, normal, and vars for contig loop
    mergedTumorBam = 'tumorSample.wholeBam'
    mergedNormalBam = 'normalSample.wholeBam'
    mergedTumorBamIndex = 'tumorSample.wholeBamIndex'
    mergedNormalBamIndex = 'normalSample.wholeBamIndex'

    # Instantiate vcf arrays
    # If genotyping is not to be performed it will just be an empty array
    for genotyper in genotypers:
        # if indel and snvs
        if genotyper in dualOutputGenotypers:
            printDualVcfArray(FH, tabCount + 2, genotyper)
        else:
            printVcfArray(FH, tabCount + 2, genotyper)

    for structVarCaller in structVarCallers:
        printVcfArray(FH, tabCount + 2, structVarCaller)

    # Will close segment and contig
    printPairedGenoContigs(FH, tabCount + 2, pairedAnalysisDir, refDir, genotypers, structVarCallers)

    # Full bam for all samples now a part of the struct
    # Do delly translocation, append to vcf array, and merge
    if structVarCallers != []:
        printPairedDellyTransApp(FH, tabCount + 2, mergedTumorBam, mergedTumorBamIndex, mergedNormalBam,
                                 mergedNormalBamIndex)

    # All vcfs will be merged here
    for genotyper in genotypers:
        # if indel and snvs
        if genotyper in dualOutputGenotypers:
            printDualReduceVcfApp(FH, tabCount + 2, genotyper, 'outDir', 'patient.patient')
        else:
            printReduceVcfApp(FH, tabCount + 2, genotyper, 'outDir', 'patient.patient')

    for structVarCaller in structVarCallers:
        printReduceVcfApp(FH, tabCount + 2, structVarCaller, 'outDir', 'patient.patient')

    closeBracket(FH, tabCount + 1, '# end normal')

    closeBracket(FH, tabCount, '# end tumor')


def printPairedGenoSetup(FH, tabCount, pairedAnalysisDir, refDir):
    ''' Eventually need to itertate over samples and access files via an ID
    hash using the PairedSample struct'''

    tabs = tabCount * '\t'

    Str = (tabs + 'foreach tumorSample in tumorArray {\n\n' +
           tabs + (1 * '\t') + 'foreach normalSample in normalArray {\n\n' +
           tabs + (2 * '\t') + '# vcf array for the pair\n' +
           tabs + (2 * '\t') + 'string outDir = strcat(patient.dir, "' + \
           pairedAnalysisDir + '/", tumorSample.sampleDir, "___", normalSample.sampleDir, "/");\n' +
           tabs + (2 * '\t') + 'tracef("%s",outDir);\n\n')

    FH.write(Str)


def getDualOutputGenotypers():
    """ ggggg"""

    return ['Strelka', 'Varscan']


def getContigGenotypers():
    """ ggggg"""

    return ['Strelka']
