import os, sys

infile = open(sys.argv[1], 'r')

coveredBases = 0
for line in infile:
	temp = line.strip().split('\t')
	genomeSize = (temp[3])
	coveredBases = coveredBases + (long(temp[1]) * long(temp[2]))
	
print coveredBases / float(genomeSize)
