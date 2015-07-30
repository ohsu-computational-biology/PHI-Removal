# import everything
import argparse # for parsing arguments
from os import path, walk # some filesystem functions
from collections import defaultdict
from random import randint

def parse_reads(path,onechars,multchars,spikedata,spikeli):
    spikedict={}
    for spike in spikeli:
        spikedict[spike]=0
    spikedict[('0','')]=0
    i=0
    with open(path) as genefile:
        while genefile.readline():
            i+=1
            if i%10000==0:
                print i
            curread = genefile.readline()
            spikedict[process(curread, onechars,multchars,spikedata,spikeli)]+=1
            genefile.readline()
            genefile.readline()
    return spikedict
            
def process(read,onechars,multchars,spikedict,spikeli):
    spikelen=34
    for i in range(len(read)-spikelen+1):
        requiredchars=True
        for charno,char in onechars.items():
            if read[i+charno]!=char:
                requiredchars=False
        if requiredchars:
            for spike in spikeli:
                if read[i:i+spikelen]==spike[1]:
                    return spike
    return ('0','')

def parse_spikes(path):
    spikeli = []
    with open(path) as spikefile:
        for line in spikefile:
            vals=line.split()
            spikeli.append((vals[0],vals[1]))
    return spikeli
    
def process_spikes(spikeli):
    spikedata = ['']*len(spikeli[0][1])
    onechars={}
    multchars=[]
    for charno in range(len(spikeli[0][1])):
        spikedata[charno]=defaultdict(set)
        for spike in spikeli:
            spikedata[charno][spike[1][charno]].add(spike)
        if len(spikedata[charno])==1:
            onechars[charno]=spikedata[charno].keys()[0]
        else:
            multchars.append(charno)
    return onechars,multchars,spikedata
    
def dist_write(spikedict,path):
    with open(path, 'w') as outfile:
        kvpairs = []
        for key in spikedict:
            kvpairs.append((key, spikedict[key]))
        kvpairs = sorted(kvpairs, key=lambda pair: -pair[1])
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
    
    spikeli = parse_spikes(args.spikes)
    onechars,multchars,spikedata=process_spikes(spikeli)
    
    for object in walk(args.source): # process in destination folder - original folder goes unmodified
        folder, subfolder, filelist = object
        for file in filelist: # loop through all files in the directory
            name, exten = path.splitext(path.basename(file)) # look at each extension
            if exten.lower() == '.fastq': # if the extension indicates the desired filetype
                if folder == args.source: # run convert command
                    name = folder+name
                else:
                    name = folder + path.sep + name
                spikedict = parse_reads(name+'.fastq', onechars,multchars,spikedata,spikeli)    
                dist_write(spikedict, name+'.txt')
    
if __name__=='__main__':
    main()