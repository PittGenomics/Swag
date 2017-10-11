import os

from swiftseq.core import SwiftSeqStrings
from swiftseq.swift import printSwiftApps, printCustomStructs
from swiftseq.swift.syntax import *

def germline_swift(workflow, workDir, contigsFile, outDir):
    ''' ggggg '''

    ########################################################################
    # Stand alone testing - need to be specified via run or config
    ########################################################################
    # !# Will need to ensure these are the proper names and naming conventions we need
    # Maybe merge these for germline and tumor normal pairs

    # Write out swift script
    swift_script_path = os.path.join(workDir, SwiftSeqStrings.swift_script_filename)
    with open(swift_script_path, 'w') as swift_script:
        ########################################################################
        ## Print out Swift syntax for apps and custom structs
        ########################################################################
        # print the apps to swift file
        printSwiftApps(swift_script)
        # write custom structs to file
        # False indicates a germline run
        printCustomStructs(swift_script, paired=False)

        ########################################################################
        ## Set up w/ sample for loop
        ########################################################################
        # Will occur in all runs (alignment, geno, or both)
        printSetup(
            swift_script,
            tabCount=0,
            contigsFile=contigsFile,
            sampleDataFile=os.path.join(outDir, SwiftSeqStrings.patient_out_filename)  # May not be needed in germline
        )

        ########################################################################
        ## Aligment
        ########################################################################
        # inBam will be passed to split by contig if alignment is not needed
        inBam = printPreAlignment(
            swift_script,
            tabCount=1,
            RGfiles=SwiftSeqStrings.readgroups_out_filename,
            alignment=workflow.has_alignment
        )

        if workflow.has_alignment:
            ## Aln read groups & merge-sort
            printAlignment(
                swift_script,
                tabCount=1,
                alignerApp=workflow.aligner,
                mergesortApp=SwiftSeqStrings.generate_sort_app
            )
            contigSplitBam = SwiftSeqStrings.contig_split_bam  # Default bam name post-alignment
        else:
            contigSplitBam = inBam

        ########################################################################
        ##   Handle contigs
        ########################################################################
        if workflow.has_gatk:
            printGrpFilenames(swift_script, tabCount=1)  # tab count of 1

        # For each caller print the auto increment array to hold vcfs
        if workflow.has_genotyping:
            for genotyper in workflow.genotypers:
                printVcfArray(swift_script, tabCount=1, genotyper=genotyper)  # tab count of 1

        if workflow.has_struct_vars:
            for structVarCaller in workflow.struct_var_callers:
                printVcfArray(swift_script, tabCount=1, genotyper=structVarCaller)  # tab count of 1

        # Dup removal optional for non-alignment cases
        has_rm_dup = workflow.has_alignment

        ########################################################################
        ## Split into contig & rm dup per chr
        ########################################################################
        # This step will always occur
        # The difference will be if dup removal is performed
        genoBam = printContigSetup(
            swift_script,
            tabCount=1,
            inputBam=contigSplitBam,
            inputBamIndex=contigSplitBam + 'Index',
            rmDup=has_rm_dup
        )

        ########################################################################
        ## GATK Post-processing
        ########################################################################
        # These steps will occur in a block
        # Will update the name of the genoBam if gatk performed
        if workflow.has_gatk:
            genoBam = printGatkAppCalls(
                swift_script,
                tabCount=2,
                inputBam=genoBam
            )

        ########################################################################
        ## Single sample coordinate genotyping
        ########################################################################
        if workflow.has_genotyping:
            printSingleSampleGeno(
                swift_script,
                tabCount=2,
                genotypers=workflow.genotypers,
                refDir=os.path.join(workDir, outDir, SwiftSeqStrings.analysis_reference_dir),
                genoBam=genoBam,
                genoBamIndex=genoBam + 'Bai'
            )

        ########################################################################
        # Structural variant calling
        ########################################################################
        # Step flexible even if Delly only supported
        if workflow.has_struct_vars:
            printDellyApp(
                swift_script,
                tabCount=2,
                genoBam=genoBam,
                genoBamIndex=genoBam + 'Bai'
            )

        ########################################################################
        # Assign contig bams to arrays
        ########################################################################
        printGermBamArrayAssignment(
            swift_script,
            tabCount=2,
            contig='contigName',
            genoBam=genoBam,
            genoBamIndex=genoBam + 'Bai'
        )
        closeBracket(
            swift_script,
            tabCount=1,
            comment='# End of contig'
        )

        ########################################################################
        ## Reduce bam steps
        ########################################################################
        # All reduce steps look for the no_mapped_reads flag within each wrapper

        # Create the command that will print the grp reduce call if GATK required
        if workflow.has_gatk:
            printReduceGrpAppCall(swift_script, tabCount=1)

        # Merge contigs and save the output bam variable name
        if workflow.has_alignment:
            QCBam = printContigMergeSort(
                swift_script,
                tabCount=1,
                bamArrayName='contigBams',
                name='geno',
                sampleDir='sample.dir',
                sampleID='sample.ID'
            )
        else:
            # if only genotyping do QC on the input bam
            QCBam = inBam

        ########################################################################
        ## Reduce vcf steps
        ########################################################################
        # All vcfs will be merged here

        if workflow.has_genotyping:
            for genotyper in workflow.genotypers:
                printReduceVcfApp(
                    swift_script,
                    tabCount=1,
                    genotyper=genotyper,
                    sampleDir='sample.dir',
                    sampleID='sample.ID'
                )

        if workflow.has_struct_vars:
            for structVarCaller in workflow.struct_var_callers:
                print(structVarCaller)

                # Will perform translocations analysis prior to the merge
                if structVarCaller == 'DellyGerm':
                    printGermDellyTransApp(
                        swift_script,
                        tabCount=1,
                        mergedBam=QCBam,
                        mergedBamIndex=QCBam + 'Index'
                    )

                printReduceVcfApp(
                    swift_script,
                    tabCount=1,
                    genotyper=structVarCaller,
                    sampleDir='sample.dir',
                    sampleID='sample.ID'
                )

        ########################################################################
        ## Merged geno bam operations
        ########################################################################
        ## Quality control
        printQualityControl(
            swift_script,
            tabCount=1,
            QCBam=QCBam,
            sampleDir='sample.dir',
            sampleID='sample.ID',
            apps=workflow.bam_quality_control_apps
        )
        closeBracket(
            swift_script,
            tabCount=0,
            comment='# End of sample'
        )  # This is the end of the sample

    return swift_script_path


### This will be necessary for ASCAT (not necessarily) and tranlocations
### with Delly

### TO-DO - handle indexes in the cases of no alignment

def tumor_normal_swift(workflow, workDir, contigsFileFp, outDir):
    ''' Perhaps break this up at some point '''

    ##########################################################################
    # Stand alone testing - These will need to be specified via run or config
    ##########################################################################
    # !# Will need to ensure these are the proper names and naming conventions we need
    # Maybe merge these for germline and tumor normal pairs

    swift_script_path = os.path.join(workDir, SwiftSeqStrings.swift_script_filename)
    with open(swift_script_path, 'w') as swift_script:
        ########################################################################
        ## Print out Swift syntax
        ########################################################################
        # print the apps to swift file
        printSwiftApps(swift_script)
        # write custom structs to file
        # True indicates a paired run
        printCustomStructs(swift_script, paired=True)

        # Map Strelka config
        if 'Strelka' in workflow.genotypers:
            swift_script.write(
                'file strelkaConfig <single_file_mapper; file="{out_dir}/strelkaConfig.ini">;\n\n'.format(
                    out_dir=outDir
                )
            )
            """
            Shouldn't this output be done where the rest of the printing scripts are?
            """

        printPairedSetup(
            swift_script,
            tabCount=0,
            contigsFile=contigsFileFp,
            patientDataFile=os.path.join(workDir, outDir, SwiftSeqStrings.patient_out_filename),
            sampleDataFile=SwiftSeqStrings.sample_out_filename
        )

        ########################################################################
        ## Aligment
        ########################################################################
        # inBam will be passed to split by contig if alignment is not needed
        inBam = printPreAlignment(
            swift_script,
            tabCount=3,
            RGfiles=SwiftSeqStrings.readgroups_out_filename,
            alignment=workflow.has_alignment
        )

        if workflow.has_alignment:
            ## Aln read groups & merge-sort
            printAlignment(
                swift_script,
                tabCount=3,
                alignerApp=workflow.aligner,
                mergesortApp=SwiftSeqStrings.generate_sort_app
            )
            contigSplitBam = SwiftSeqStrings.contig_split_bam  # Default bam name post-alignment
        else:
            contigSplitBam = inBam

        ########################################################################
        ##   Handle contigs
        ########################################################################
        if workflow.has_gatk:
            printGrpFilenames(swift_script, tabCount=3)  # tab count of 1

        # Dup removal optional for non-alignment cases
        has_rm_dup = workflow.has_alignment

        ########################################################################
        ## Split into contig & rm dup per chr
        ########################################################################
        # This step will always occur
        # The difference will be if dup removal is performed
        ##!!!! If not alignement index inbam !!! ###
        genoBam = printContigSetup(
            swift_script,
            tabCount=3,
            inputBam=contigSplitBam,
            inputBamIndex=contigSplitBam + 'Index',
            rmDup=has_rm_dup
        )

        ########################################################################
        ## GATK Post-processing
        ########################################################################
        # These steps will occur in a block
        # Will update the name of the genoBam if gatk performed
        if workflow.has_gatk:
            genoBam = printGatkAppCalls(
                swift_script,
                tabCount=4,
                inputBam=genoBam
            )

        ########################################################################
        # Assign contig bams to arrays
        ########################################################################
        printPairedBamArrayAssignment(
            swift_script,
            tabCount=4,
            contig='contigName',
            genoBam=genoBam
        )
        closeBracket(
            swift_script,
            tabCount=3,
            comment='# End of contigs'
        )

        ########################################################################
        ## Reduce bam steps - Sample level operation
        ########################################################################
        # All reduce steps look for the no_mapped_reads flag within each wrapper

        # Create the command that will print the grp reduce call if GATK required
        if workflow.has_gatk:
            printReduceGrpAppCall(swift_script, tabCount=3)

        # !# This will be a disparity between germline and tumor-normal
        # !# Is germ conting merge sort ok here???

        # Should occur regardless of genotyping or not
        QCBam = printPairedContigMergeSort(
            swift_script,
            tabCount=3,
            name='geno',
            sampleDir='sample.dir',
            sampleID='sample.ID'
        )

        # Do QC here - shouldn't this use QCBam?
        # if bamQualityCOntrolApps is empty it will print nothing to the Swift script
        printQualityControl(
            swift_script,
            tabCount=3,
            QCBam='pairedSampleData.wholeBam',
            sampleDir='sample.dir',
            sampleID='sample.ID',
            apps=workflow.bam_quality_control_apps
        )

        printAssignPairedData(swift_script, tabCount=3)

        closeBracket(swift_script, tabCount=2, comment='# End of sample')
        closeBracket(swift_script, tabCount=1, comment='# End of tissue')

        ##########################
        ## Do paired genotyping
        ##########################
        if workflow.has_genotyping:
            printPairedGeno(
                swift_script,
                tabCount=1,
                pairedAnalysisDir=SwiftSeqStrings.paired_analysis_dir,
                refDir=os.path.join(workDir, outDir, SwiftSeqStrings.analysis_reference_dir),
                genotypers=workflow.genotypers,
                structVarCallers=workflow.struct_var_callers
        )

        closeBracket(swift_script, tabCount=0, comment='# End of patient/individual')

    return swift_script_path
