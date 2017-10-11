import os, sys, warnings
from os.path import commonprefix
from os.path import isfile
from subprocess import Popen, PIPE

def mkDir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def mkSymlink(source, destination):
	if not os.path.exists(destination):
		os.symlink(source, destination)
                
def createSymlinkDir(inputDataFilename):
	symdir = dict()
	with open(inputDataFilename) as f:
		headers = next(f)
		# Check headers?
	
		NORMAL = 0
		TUMOR = 1
		SAMPLE_ID = 0
		BAM_FILEPATH = 1
		for line in f:
			indivId, tissueType, sampleId, bamFilePath = line.strip().split('\t')
			if bamFilePath[-4:] != '.bam':
				print bamFilePath + ' is not a .bam file, skipping addition'
				continue
			if indivId not in symdir:
				symdir[indivId] = [dict(), dict()]
			if tissueType == 'normal':
				if sampleId not in symdir[indivId][NORMAL]:
					symdir[indivId][NORMAL][sampleId] = bamFilePath
				else:
					print indivId + ' => normal => ' + sampleId + ' already exists, skipping addition of ' + bamFilePath
					continue
			elif tissueType == 'tumor':
				if sampleId not in symdir[indivId][TUMOR]:
					symdir[indivId][TUMOR][sampleId] = bamFilePath
				else:
					print indivId + ' => tumor => ' + sampleId + ' already exists, skipping addition of ' + bamFilePath
					continue
			else:
				print 'Tissue type was not "normal" or "tumor", skipping addition of ' + bamFilePath
	
		for indivId in symdir.keys():
			for sampleId in symdir[indivId][NORMAL]:
				bamFilePath = symdir[indivId][NORMAL][sampleId]
				bamFile = bamFilePath[bamFilePath.rfind('/') + 1:]
				mkDir(indivId + '/normal/' + sampleId)
				mkSymlink(bamFilePath, indivId + '/normal/' + sampleId + '/' + bamFile)
			for sampleId in symdir[indivId][TUMOR]:
				bamFilePath = symdir[indivId][TUMOR][sampleId]
				bamFile = bamFilePath[bamFilePath.rfind('/') + 1:]
				mkDir(indivId + '/tumor/' + sampleId)
				mkSymlink(bamFilePath, indivId + '/tumor/' + sampleId + '/' + bamFile)


### Run the program with sample data
filename = sys.argv[1]
createSymlinkDir(filename)
