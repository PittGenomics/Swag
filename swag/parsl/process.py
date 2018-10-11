import collections
import csv
import os

import parsl

from swag.core import SwagStrings
from swag.parsl.syntax import *
from swag.util import read_data
from swag.parsl.apps import *

logger = logging.getLogger(__name__)

def germline(workflow, work_dir, contigs_file, out_dir):
    ########################################################################
    ## Set up w/ sample for loop
    ########################################################################
    # Will occur in all runs (alignment, geno, or both)

    contigs = read_data(contigs_file)
    with open(os.path.join(out_dir, SwagStrings.patient_out_filename)) as f:
        samples = list(csv.DictReader(f, delimiter=' '))

    for sample in samples:
        sample['dir'] = os.path.abspath(sample['dir'])
        ########################################################################
        ## Aligment
        ########################################################################
        # in_bam will be passed to split by contig if alignment is not needed
        # INPUT - Unaligned input files (including read groups)

        in_bam = os.path.join(sample['dir'], "{}.bam".format(sample['ID']))
        contig_split_bam = in_bam

        if workflow.has_alignment:
            contig_split_bam = SwagStrings.contig_split_bam  # Default bam name post-alignment

            alnSampleContigBams = align(
                in_bam=in_bam,
                work_dir=work_dir,
                aligner_app=getattr(swag.parsl.apps, workflow.aligner),
                mergesort_app=getattr(swag.parsl.apps, SwagStrings.generate_sort_app),
                sample_dir=os.path.abspath(sample['dir']),
                sample_id=sample['ID']
            )

        # FIXME broken if `(not workflow.has_alignment)`
        contigBams = []
        contigBamBais = []
        for contig, bam in zip(contigs, alnSampleContigBams):
            if workflow.has_alignment: # Dup removal optional for non-alignment cases
                bam = picard_mark_duplicates(work_dir, bam, contig, sample['ID'], sample['dir'])


            ########################################################################
            ## GATK Post-processing
            ########################################################################
            # These steps will occur in a block
            # Will update the name of the genoBam if gatk performed
            # if workflow.has_gatk:
                 # printGrpFilenames(swift_script, tabCount=1)
                 # Str = (tabs + 'file mergedGrp <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp")>;\n' +
                 #        tabs + 'file mergeGrpLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp.log")>;\n' +
                 #        tabs + 'file grpFiles [];\n\n')

                # genoBam = printGatkAppCalls(
                 #    parsl_script,
                 #    tabCount=2,
                 #    inputBam=genoBam
                # )

            ########################################################################
            ## Single sample coordinate genotyping
            ########################################################################
            # if workflow.has_genotyping:
                # for genotyper in workflow.genotypers:
                #      Str = tabs + 'file[auto] ' + genotyper + 'ContigVcfs;\n'
                # printSingleSampleGeno(
                #     parsl_script,
                #     tabCount=2,
                #     genotypers=workflow.genotypers,
                #     refDir=os.path.join(work_dir, out_dir, SwagStrings.analysis_reference_dir),
                #     genoBam=genoBam,
                #     genoBamIndex=genoBam + 'Bai'
                # )

            ########################################################################
            # Structural variant calling
            ########################################################################
            # Step flexible even if Delly only supported
            # if workflow.has_struct_vars:
                # for structVarCaller in workflow.struct_var_callers:
                #      Str = tabs + 'file[auto] ' + structVarCaller + 'ContigVcfs;\n'
                # printDellyApp(
                #     parsl_script,
                #     tabCount=2,
                #     genoBam=genoBam,
                #     genoBamIndex=genoBam + 'Bai'
                # )


            contigBams.append(bam)
            contigBamBais.append(index_bam(work_dir, bam))

        #########################################################################
        ### Reduce bam steps
        #########################################################################
        ## All reduce steps look for the no_mapped_reads flag within each wrapper

        ## Create the command that will print the grp reduce call if GATK required
        #if workflow.has_gatk:
        #     Str = (tabs + 'file mergedGrp <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp")>;\n' +
        #            tabs + 'file mergeGrpLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp.log")>;\n' +
        #            tabs + 'file grpFiles [];\n\n')
        #    printReduceGrpAppCall(parsl_script, tabCount=1)

        if workflow.has_alignment:
            QCBam, QCBamBai = contig_merge_sort(
                work_dir,
                contigBams,
                sample['dir'],
                sample['ID']
            )
        else:
            # if only genotyping do QC on the input bam
            QCBam = inBam

        QCBam.result()
        QCBamBai.result()

        #########################################################################
        ### Reduce vcf steps
        #########################################################################
        ## All vcfs will be merged here

        #if workflow.has_genotyping:
        #    for genotyper in workflow.genotypers:
        #        printReduceVcfApp(
        #            parsl_script,
        #            tabCount=1,
        #            genotyper=genotyper,
        #            sampleDir='sample.dir',
        #            sampleID='sample.ID'
        #        )

        #if workflow.has_struct_vars:
        #    for structVarCaller in workflow.struct_var_callers:
        #         Str = tabs + 'file[auto] ' + structVarCaller + 'ContigVcfs;\n'
        #    for structVarCaller in workflow.struct_var_callers:
        #        print(structVarCaller)

        #        # Will perform translocations analysis prior to the merge
        #        if structVarCaller == 'DellyGerm':
        #            printGermDellyTransApp(
        #                parsl_script,
        #                tabCount=1,
        #                mergedBam=QCBam,
        #                mergedBamIndex=QCBam + 'Index'
        #            )

        #        printReduceVcfApp(
        #            parsl_script,
        #            tabCount=1,
        #            genotyper=structVarCaller,
        #            sampleDir='sample.dir',
        #            sampleID='sample.ID'
        #        )

        #########################################################################
        ### Merged geno bam operations
        #########################################################################
        ### Quality control
        #printQualityControl(
        #    parsl_script,
        #    tabCount=1,
        #    QCBam=QCBam,
        #    sampleDir='sample.dir',
        #    sampleID='sample.ID',
        #    apps=workflow.bam_quality_control_apps
        #)
        #closeBracket(
        #    parsl_script,
        #    tabCount=0,
        #    comment='# End of sample'
        #)  # This is the end of the sample

        #return parsl_script_path


#### This will be necessary for ASCAT (not necessarily) and tranlocations
#### with Delly

#### TO-DO - handle indexes in the cases of no alignment

def tumor_normal(workflow, work_dir, contigsFileFp, out_dir):
    ''' Perhaps break this up at some point '''

    ###########################################################################
    ## Stand alone testing - These will need to be specified via run or config
    ###########################################################################
    ## !# Will need to ensure these are the proper names and naming conventions we need
    ## Maybe merge these for germline and tumor normal pairs

    #parsl_script_path = os.path.join(work_dir, SwagStrings.parsl_script_filename)
    #with open(parsl_script_path, 'w') as parsl_script:
      #  # Map Strelka config
      #  if 'Strelka' in workflow.genotypers:
      #      parsl_script.write(
      #          'file strelkaConfig <single_file_mapper; file="{out_dir}/strelkaConfig.ini">;\n\n'.format(
      #              out_dir=out_dir
      #          )
      #      )
      #      """
      #      Shouldn't this output be done where the rest of the printing scripts are?
      #      """

      #  printPairedSetup(
      #      parsl_script,
      #      tabCount=0,
      #      contigsFile=contigsFileFp,
      #      patientDataFile=os.path.join(work_dir, out_dir, SwagStrings.patient_out_filename),
      #      sampleDataFile=SwagStrings.sample_out_filename
      #  )

      #  ########################################################################
      #  ## Aligment
      #  ########################################################################
      #  # inBam will be passed to split by contig if alignment is not needed
      #  inBam = printPreAlignment(
      #      parsl_script,
      #      tabCount=3,
      #      RGfiles=SwagStrings.readgroups_out_filename,
      #      alignment=workflow.has_alignment
      #  )

      #  if workflow.has_alignment:
      #      ## Aln read groups & merge-sort
      #      printAlignment(
      #          parsl_script,
      #          tabCount=3,
      #          alignerApp=workflow.aligner,
      #          mergesortApp=SwagStrings.generate_sort_app
      #      )
      #      contigSplitBam = SwagStrings.contig_split_bam  # Default bam name post-alignment
      #  else:
      #      contigSplitBam = inBam

      #  ########################################################################
      #  ##   Handle contigs
      #  ########################################################################
      #  if workflow.has_gatk:
        # Str = (tabs + 'file mergedGrp <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp")>;\n' +
        #        tabs + 'file mergeGrpLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp.log")>;\n' +
        #        tabs + 'file grpFiles [];\n\n')
      #      printGrpFilenames(parsl_script, tabCount=3)  # tab count of 1

      #  # Dup removal optional for non-alignment cases
      #  has_rm_dup = workflow.has_alignment

      #  ########################################################################
      #  ## Split into contig & rm dup per chr
      #  ########################################################################
      #  # This step will always occur
      #  # The difference will be if dup removal is performed
      #  ##!!!! If not alignement index inbam !!! ###
      #  genoBam = printContigSetup(
      #      parsl_script,
      #      tabCount=3,
      #      inputBam=contigSplitBam,
      #      inputBamIndex=contigSplitBam + 'Index',
      #      rmDup=has_rm_dup
      #  )

      #  ########################################################################
      #  ## GATK Post-processing
      #  ########################################################################
      #  # These steps will occur in a block
      #  # Will update the name of the genoBam if gatk performed
      #  if workflow.has_gatk:
        # Str = (tabs + 'file mergedGrp <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp")>;\n' +
        #        tabs + 'file mergeGrpLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp.log")>;\n' +
        #        tabs + 'file grpFiles [];\n\n')
      #      genoBam = printGatkAppCalls(
      #          parsl_script,
      #          tabCount=4,
      #          inputBam=genoBam
      #      )

      #  ########################################################################
      #  # Assign contig bams to arrays
      #  ########################################################################
      #  printPairedBamArrayAssignment(
      #      parsl_script,
      #      tabCount=4,
      #      contig='contigName',
      #      genoBam=genoBam
      #  )
      #  closeBracket(
      #      parsl_script,
      #      tabCount=3,
      #      comment='# End of contigs'
      #  )

      #  ########################################################################
      #  ## Reduce bam steps - Sample level operation
      #  ########################################################################
      #  # All reduce steps look for the no_mapped_reads flag within each wrapper

      #  # Create the command that will print the grp reduce call if GATK required
      #  if workflow.has_gatk:
        # Str = (tabs + 'file mergedGrp <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp")>;\n' +
        #        tabs + 'file mergeGrpLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".merged.grp.log")>;\n' +
        #        tabs + 'file grpFiles [];\n\n')
      #      printReduceGrpAppCall(parsl_script, tabCount=3)

      #  # !# This will be a disparity between germline and tumor-normal
      #  # !# Is germ conting merge sort ok here???

      #  # Should occur regardless of genotyping or not
      #  QCBam = printPairedContigMergeSort(
      #      parsl_script,
      #      tabCount=3,
      #      name='geno',
      #      sampleDir='sample.dir',
      #      sampleID='sample.ID'
      #  )

      #  # Do QC here - shouldn't this use QCBam?
      #  # if bamQualityCOntrolApps is empty it will print nothing to the Parsl script
      #  printQualityControl(
      #      parsl_script,
      #      tabCount=3,
      #      QCBam='pairedSampleData.wholeBam',
      #      sampleDir='sample.dir',
      #      sampleID='sample.ID',
      #      apps=workflow.bam_quality_control_apps
      #  )

      #  printAssignPairedData(parsl_script, tabCount=3)

      #  closeBracket(parsl_script, tabCount=2, comment='# End of sample')
      #  closeBracket(parsl_script, tabCount=1, comment='# End of tissue')

      #  ##########################
      #  ## Do paired genotyping
      #  ##########################
      #  if workflow.has_genotyping:
      #      printPairedGeno(
      #          parsl_script,
      #          tabCount=1,
      #          pairedAnalysisDir=SwagStrings.paired_analysis_dir,
      #          refDir=os.path.join(work_dir, out_dir, SwagStrings.analysis_reference_dir),
      #          genotypers=workflow.genotypers,
      #          structVarCallers=workflow.struct_var_callers
      #  )

      #  closeBracket(parsl_script, tabCount=0, comment='# End of patient/individual')

    #return parsl_script_path
