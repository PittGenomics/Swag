#!/usr/bin/env python3

import argparse
import os
import logging
import csv

import bioapps as bio


def readData(filename):
   if os.path.exists(filename):
      try:
         with open(filename, 'r') as f:
            return [i.strip() for i in f.readlines()]
      except IOError as e:
         logging.error("Caught IOError reading file:%s %s" % (filename, e))
   else:
      logging.error("File doesn't exist :%s" % filename)

def readcsv(filename, headers=None, delimiter='|'):
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
   print(samples)
