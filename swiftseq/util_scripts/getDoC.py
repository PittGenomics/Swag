import sys

infile = open(sys.argv[1], 'r')

coveredBases = 0
for line in infile:
    temp = line.strip().split('\t')
    genomeSize = (temp[3])
    coveredBases = coveredBases + (int(temp[1]) * int(temp[2]))

print(coveredBases / float(genomeSize))
