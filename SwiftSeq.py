#!/usr/bin/env python3

import argparse
import os
import logging

import bioapps as bio


def readData(filename):
   if os.path.exists(filename):
      try:
         with open(filename, 'r') as f:
            return f.readlines()
      except IOError as e:
         logging.error("Caught IOError reading file:%s %s" % (filename, e))
   else:
      logging.error("File doesn't exist :%s" % filename)
      


if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="swift_seq.log", help="Logfile")
   parser.add_argument("-s", "--samples", default="analysis/individuals.txt", help="Individual samples")
   args   = parser.parse_args()

   logging.basicConfig(filename=args.logfile, level=logging.DEBUG,
                       format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt='%m-%d %H:%M')

   x,_ = bio.Mosaik(f_inbam="1",
                    f_readGroupStr="",
                    sampleID="111",
                    d_dir="./analysis",
                    stdout='outputs/test.out',
                    outputs=["outputs"])
   x.result()
   print(readData('outputs/test.out'))
   
