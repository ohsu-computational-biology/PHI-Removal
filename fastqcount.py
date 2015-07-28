# import everything
import argparse # for parsing arguments
import shutil # for doing file tree operations
import subprocess # for running command line commands
from math import log10 # for computation (see line 37)
from os import path, walk, mkdir, remove # some filesystem functions

def parsereads(path, spikeli):
    spikedict={}
    for spike in spikeli:
        spikedict[spike]=0
    spikedict['']=0
    i=0
    with open(path) as genefile:
        while genefile.readline():
            i+=1
            if i%10000==0:
                print i
            curread = genefile.readline()
            spikedict[process(curread, spikedict, spikeli)]+=1
            genefile.readline()
            genefile.readline()
    return spikedict
            
def process(read,spikeli):
    for spike in spikeli:
        for i in range(len(read)-len(spike[1])+1):
            if spike[1]==read[i:i+len(spike)]:
                return spike
    return ''

def parsespikes(path):
    spikeli = []
    with open(path) as spikefile:
        for line in spikefile:
            vals=line.split()
            spikeli.append((vals[0],vals[1]))
    return spikeli
    
def distwrite(spikedict,path):
    with open(path, 'w') as outfile:
        kvpairs = []
        for key in spikedict:
            kvpairs.append((key, spikedict[key]))
        kvpairs = sorted(kvpairs, key=lambda pair: pair[1])
        for pair in kvpairs:
            outline=[pair[0][0],pair[0][1],str(pair[1])]
            outfile.write(','.join(outline)+'\n')
            
    
def main():
    """
    main: sets up command line arguments, then goes through the origin directory to find all files to be processed, then runs the convert command on these
    Arguments: none, but some arguments do come from the command line (see parser.add_argument help text)
    Returns: nothing
    Effects: Makes a new directory to contain tiled image data from the origin directory
    """
    parser = argparse.ArgumentParser(description='Get inputs for the FASTQ counting script.') # set arguments
    parser.add_argument('spikes', help = 'The file containing spike data.')
    parser.add_argument('source', help = 'The directory to be searched.')
    args=parser.parse_args()
    
    spikeli = parsespikes(args.spikes)
    
    for object in walk(args.source): # process in destination folder - original folder goes unmodified
        folder, subfolder, filelist = object
        for file in filelist: # loop through all files in the directory
            name, exten = path.splitext(path.basename(file)) # look at each extension
            if exten.lower() == '.fastq': # if the extension indicates the desired filetype
                if folder == args.source: # run convert command
                    name = folder+name
                else:
                    name = folder + path.sep + name
                spikedict = parsereads(name+'.fastq', spikeli)    
                distwrite(spikedict, name+'.txt')
    
if __name__=='__main__':
    main()