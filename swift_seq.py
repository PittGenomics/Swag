#!/usr/bin/env python3

import argparse
import os
import logging
import csv

import bioapps as bio


def readData(filename):
   ''' Helper function to read files
   Args:
   filename : Name of file to read
   
   Returns
   stripped lines from the file
   '''

   if os.path.exists(filename):
      try:
         with open(filename, 'r') as f:
            return [i.strip() for i in f.readlines()]
      except IOError as e:
         logging.error("Caught IOError reading file:%s %s" % (filename, e))
   else:
      logging.error("File doesn't exist :%s" % filename)

def readcsv(filename, headers=None, delimiter='|'):
   ''' Helper function for reading CSV files.
   Args:
   filename : Name of the file

   Kwargs:
   headers : (default=None) Headers as a list of strings
   delimiter : (default='|') Delimited to use to split rows
   
   Returns:
   list of dict rows
   '''

   try :
      f = open(filename, 'r')
      if headers == "implicit":
         headers = f.readline().strip().split(delimiter)
         reader = csv.DictReader(f, delimiter=delimiter, fieldnames=headers)

      elif type(headers) is list :
         reader = csv.DictReader(f, delimiter=delimiter, fieldnames=headers)

      else:
         reader = csv.DictReader(f, delimiter=delimiter)

   except Exception as e:
      print("[ERROR]Caught exception in opening the file:{0}".format(filename))
      print("[ERROR]Reason : {0}".format(e))
      exit(-1)
   return list(reader)

def BwaMem (sample, sampleRG, inBam, mock=False):
   ''' BwaMem : Convenience function that constructs arguments and params for the call to the app function
   Args:
   sample : filename as string
   sampleRG : filename as string
   inBam : filename as string
   
   Returns:
   App_Future, Data_Future (for the bam file)
   ''' 
   # root file name for the RG
   RGID    = sampleRG.rsplit('/', 1)[1].strip('.bam')
   RGname  = RGID.rsplit('.', 1)[1]
   #print("RGID    : ", RGID)
   #print("RGname  : ", RGname)

   RGalnBam  =  "{0}/{1}.aln.bam".format(sample['dir'], RGID)
   RGalnBai  =  "{0}/{1}.aln.bam.bai".format(sample['dir'], RGID)
   RGalnLog  =  "{0}/{1}.aln.log".format(sample['dir'], RGID)
         
   print("Writing stdout to :", '{0}.out.txt'.format(RGID))
   print("Writing stderr to :", '{0}.err.txt'.format(RGID))
   fu_app, fu_data = bio.BwaMem (inBam, RGname, RGID, sample['dir'], 
                                 outputs=[RGalnBam, RGalnBai, RGalnLog],
                                 stdout='{0}.out.txt'.format(RGID), 
                                 stderr='{0}.err.txt'.format(RGID),
                                 mock=mock
                                 )

   # Return the app future and the datafuture for the bam file
   return fu_app, fu_data[0]
   
def RgMergeSort (sample, RGalnBams, mock=False):
   ''' RgMergeSort : Convenience function that constructs arguments and params for the call to the app 
   function
   Args:
   sample : filename as string
   RGalnBams : List of futures of bam files from BwaMem step
   
   Returns:
   App_Future, Data_Future (for the bam file)

   '''
   #print ("Launching RgMergesort for : {0}".format(sample))
   #print ("Sample['dir'] : ", sample['dir'])
   #print ("stdout : ", '{0}/RgMergeSort.stdout'.format(sample['dir']))
   # Mergesort the readgroups from this sample
   alnSampleContigBamFile = "{0}/sampleContigs.txt".format(sample['dir'])
   alnSampleContigBams = readData("{0}/sampleContigs.txt".format(sample['dir']))
      
   #print("alnSampleContigBams[0] :", alnSampleContigBams[0])
   alnSampleBamLog = "{0}/{1}.RGmerge.log".format(sample['dir'], sample['ID'])
      
   app_fu, data_fus = bio.RgMergeSort (sample['ID'], sample['dir'], inputs=RGalnBams,
                                       outputs=[alnSampleContigBamFile,
                                                alnSampleBamLog] + alnSampleContigBams,
                                       mock=mock)

   return app_fu, data_fus


def PicardMarkDuplicates (inBam, sample, contigName, mock=False):
   ''' PicardMarksDuplicates : Convenience function that wraps Picard
   Args:
   sample : sample info
   contigName : Name of contig
   '''

   contigID = "{0}.{1}".format(sample['ID'],contigName)

   contigDupLog = "{0}/{1}.contig.dup.log".format(sample['dir'], contigID)   
   contigDupBam = "{0}/{1}.contig.dup.bam".format(sample['dir'], contigID)
   contigDupMetrics = "{0}/{1}.contig.dup.metrics".format(sample['dir'], contigID)
   
   app_fu, data_fus = bio.PicardMarkDuplicates (inBam,
                                                contigID,
                                                sample['dir'],
                                                outputs=[contigDupLog,
                                                         contigDupBam,
                                                         contigDupMetrics],
                                                mock=mock)

   return app_fu, data_fus


def IndexBam (contigDupBam, mock=False):
   ''' IndexBam : Convenience function that wraps IndexBam
   Args:
   contigDupBam : Name of contigDupBam
   '''

   contigIndexStr = contigDupBam.filepath;
   contigDupBamBai = "{0}.bai".format(contigIndexStr)
   contigDupBamBaiLog = "{0}.bai.log".format(contigIndexStr)

   app_fu, data_fus = bio.IndexBam(contigDupBam, outputs=[contigDupBamBaiLog,
                                                          contigDupBamBai])
   return app_fu, data_fus


def PlatypusGerm (contigName, contigSegment, sample, contigDupBam, contigDupBamBai, mock=False):
   ''' PicardMarksDuplicates : Convenience function that wraps Picard
   Args:
   sample : sample info
   contigName : Name of contig
   '''
   # Get coordinate info
   contigID = "{0}.{1}".format(sample['ID'],contigName)
   coords = "{0}:{1}".format(contigName,contigSegment)
   segmentSuffix = ".{0}_{1}".format(contigName, contigSegment)
   
   PlatypusGermContigVcf = "{0}/{1}{2}.PlatypusGerm.vcf".format(sample["dir"], contigID, segmentSuffix)
   PlatypusGermContigVcfLog = "{0}/{1}{2}.PlatypusGerm.log".format(sample["dir"], contigID, segmentSuffix)
   app_fu, data_fus = bio.PlatypusGerm (contigDupBam,
                                        contigDupBamBai,
                                        contigID,
                                        sample['dir'],
                                        coords,
                                        outputs=[PlatypusGermContigVcfLog,
                                                 PlatypusGermContigVcf],
                                        mock=mock)
   
   return app_fu, data_fus
   
def BamutilPerBaseCoverage (genoMergeBam, sample, mock=False):
   ''' SamtoolsFlagstat : Convenience function that wraps SamtoolsFlagstat
   Args:
   contigDupBam : Name of contigDupBam
   # Per base coverage on the geno-ready aligned bam (genoMergeBam)
   file perBaseCoverageLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.perBaseCoverage.log")>;
   file perBaseCoverage <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.perBaseCoverage")>;
   (perBaseCoverageLog,perBaseCoverage) = BamutilPerBaseCoverage (genoMergeBam,sample.ID,sample.dir);

   '''
   # Per base coverage on the geno-ready aligned bam (genoMergeBam)
   perBaseCoverageLog = "{0}/{1}.bam.perBaseCoverage.log".format(sample['dir'], sample['ID'])
   perBaseCoverage = "{0}/{1}.bam.perBaseCoverage".format(sample['dir'],sample['ID'])
   app_fu, data_fus = BamutilPerBaseCoverage (genoMergeBam,
                                              sample['ID'],
                                              sample['dir'],
                                              outputs=[perBaseCoverageLog,perBaseCoverage],
                                              mock=mock)   
   return app_fu, data_fus


def SamtoolsFlagstat (genoMergeBam, sample, mock=False):
   ''' SamtoolsFlagstat : Convenience function that wraps SamtoolsFlagstat
   Args:
   contigDupBam : Name of contigDupBam

   # Flagstat on the geno-ready aligned bam (genoMergeBam)
   file flagstatLog <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.flagstat.log")>;
   file flagstat <single_file_mapper; file=strcat(sample.dir,"/",sample.ID,".bam.flagstat")>;
   (flagstatLog,flagstat) = SamtoolsFlagstat (genoMergeBam,sample.ID,sample.dir);

   '''
   
   # Flagstat on the geno-ready aligned bam (genoMergeBam)
   flagstatLog = "{0}/{1}.bam.flagstat.log".format(sample['dir'], sample['ID'])
   flagstat = "{0}/{1}.bam.flagstat ".format(sample['dir'], sample['ID'])
   app_fu, data_fus = SamtoolsFlagstat (genoMergeBam,
                                        sample['ID'],
                                        sample['dir'],
                                        outputs=[flagstatLog,flagstat],
                                        mock=mock)

   return app_fu, data_fus

      
def ConcatVcf (PlatypusGermContigVcfs, sample, mock=False):
   ''' ConcatVCF : Convenience function that wraps ConcatVcf
   Args:
   contigDupBam : Name of contigDupBam
   '''
   
   # Cat together the PlatypusGerm contig vcf files

   PlatypusGermMergedVcf = "{0}/{1}.merged.PlatypusGerm.vcf".format(sample['dir'],sample['ID'])
   PlatypusGermMergedVcfLog = "{0}/{1}..merged.PlatypusGerm.log".format(sample['dir'],sample['ID'])

   app_fu, data_fus = bio.ConcatVcf(sample['ID'],
                                    sample['dir'],
                                    inputs=PlatypusGermContigVcfs,
                                    outputs=[PlatypusGermMergedVcfLog,
                                             PlatypusGermMergedVcf],
                                    mock=mock)
   return app_fu, data_fus


      
def ContigMergeSort (contigBams, sample, mock=False):
   ''' IndexBam : Convenience function that wraps IndexBam
   Args:
   contigDupBam : Name of contigDupBam
   '''
   # Mergesort the geno contig bams

   genoMergeBamIndex = "{0}/{1}.geno.merged.bam.bai".format(sample['dir'],sample['ID'])
   genoMergeBam = "{0}/{1}.geno.merged.bam".format(sample['dir'],sample['ID'])
   genoMergeLog = "{0}/{1}.geno.merged.log".format(sample['dir'],sample['ID'])
   
   app_fu, data_fus = bio.ContigMergeSort (sample['ID'],
                                           sample['dir'],
                                           inputs=contigBams.values(),
                                           outputs=[genoMergeLog,
                                                    genoMergeBam,
                                                    genoMergeBamIndex],
                                           mock=mock)
                                           
   return app_fu, data_fus



def run_all(samples, genomeContigs, mock=False):
   ''' run_all is the top level function
   It takes a list of samples, and the genomeContigs as args
   ''' 

   contigBams = {}
   contigBamsIndex = {}
   for sample in samples:
      
      # INPUT - Unaligned input files (including read groups)
      inBam     = "{0}/{1}.bam".format(sample['dir'], sample['ID'])

      # reads in the data file containing read group names
      sampleRGs = readData("{0}/RGfiles.txt".format(sample['dir']))
      
      # File array of RG bams to be used by mergesort
      RGalnBams  = [];      
      for idx, sampleRG  in enumerate(sampleRGs):
         fu_app, fu_bam = BwaMem(sample, sampleRG, inBam, mock=mock)
         # Map realigned file to an array
         RGalnBams.extend([fu_bam])

      # Do MergeSort
      merge_fu, merge_data_fus = RgMergeSort(sample, RGalnBams, mock=mock)

      _,_, *fu_alnSampleContigBams  = merge_data_fus

      print("fu_alnSampleContigBams :", fu_alnSampleContigBams)
      
      PlatypusGermContigVcfs = []
      contigBams = {}
      contigBamsIndex = {}

      # Processed (genotyping ready) contig bams will be stored here      
      for idx, contigName in enumerate(genomeContigs) :
         
         print("inBam: {0} \n ContigName: {1}", fu_alnSampleContigBams[idx], contigName)
         picard_fu, picard_data_fus = PicardMarkDuplicates (fu_alnSampleContigBams[idx],
                                                            sample, 
                                                            contigName,
                                                            mock=mock)
         _, contigDupBam, _ = picard_data_fus

         ref_path = "/share/swiftseq/run/analysis/Reference/contig_segments_{0}.txt"
         contigSegments = readData(ref_path.format(contigName))

         index_fu, index_data_fus = IndexBam (contigDupBam, mock=mock)
         contigDupBamBaiLog, contigDupBamBai = index_data_fus

         for contigSegment in contigSegments :

               
            plat_fu, plat_data_fu = PlatypusGerm(contigName, contigSegment, 
                                                 sample, contigDupBam, 
                                                 contigDupBamBai, mock=mock)
            plat_log, plat_ContigVcfs = plat_data_fu
            PlatypusGermContigVcfs.extend([plat_ContigVcfs])

         contigBams[contigName] = contigDupBam;
         contigBamsIndex[contigName] = contigDupBamBai;

      # End of contig loop      
      cms_fu, cms_data_fu = ContigMergeSort (contigBams, sample, mock=mock)
      
      concat_fu, concat_data_fu = ConcatVcf (PlatypusGermContigVcfs, sample, mock=mock)

      sf_fu, sf_data_fu = SamtoolsFlagstat (cms_data_fu[1], sample, mock=mock)

      bbc_fu, bbc_data_fu = BamutilPerBaseCoverage (cmd_data_fu[1], sample, mock=mock);
   # End of sample loop

   # Done
   for item in RGalnBams:
      print(item.result())



if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="swift_seq.log", help="Logfile")
   parser.add_argument("-s", "--samples", default="analysis/individuals.txt", help="Individual samples")
   parser.add_argument("-g", "--genomeContigs", default="analysis/Reference/contigs.txt",
                       help="Reference genome contigs")
   args   = parser.parse_args()

   logging.basicConfig(filename=args.logfile, level=logging.DEBUG,
                       format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt='%m-%d %H:%M')

   genomeContigs = readData(args.genomeContigs)

   samples = readcsv(args.samples, headers='implicit', delimiter=' ')
   results = run_all(samples, genomeContigs, mock=False)
   print("Done with workflow")

   print(dfk)
