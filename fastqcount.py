"""
fastqcount.py: counts occurrences of specified spikes in a fastq file
"""

# import everything
import argparse # for parsing arguments
from os import path, walk # some filesystem functions
from collections import defaultdict
from random import randint

def parse_reads(path,onechars,multchars,spikedata,spikeli):
    """
    parse_reads: reads the file, then calls process on each read, managing the list of spikes
    Arguments:
        path: the path to the fastq file
        onechars, multchars, spikedata: see the process_spikes docstring for details
        spikeli: the list of spikes, see parse_spikes docstring for details
    Returns:
        spikedict: a dictionary with keys as spikes (SPIKE_ID, SPIKE) and values as counts of the spike
    """
    spikedict={}
    for spike in spikeli:
        spikedict[spike]=0
    spikedict[('0','')]=0 # initialize
    i=0
    with open(path) as genefile:
        while genefile.readline():
            i+=1
            if i%10000==0: # progress marker
                print i
            curread = genefile.readline()
            spikedict[process(curread, onechars,multchars,spikedata,spikeli)]+=1
            genefile.readline()
            genefile.readline() # discard superfluous lines (fastq has reads every 4 lines)
    return spikedict
            
def process(read,onechars,multchars,spikedata,spikeli):
    """
    process: finds spikes in a read
    Arguments:
        read: the read to be searched for spikes
        onechars, multchars, spikedata: see process_spikes docstring for details
        spikeli: the list of spikes, see parse_spikes docstring for details
    Returns:
        spike: the spike found in the read, or a blank spike if no spike exists
    """
    spikelen=34 # spikes have 34 characters - change this if that is wrong
    for i in range(len(read)-spikelen+1):
        requiredchars=True # check that this starting position has all requirred characters
        for charno,char in onechars.items():
            if read[i+charno]!=char:
                requiredchars=False
                break
        if requiredchars: # check to see if there is a spike only if all required characters are present
            for spike in spikeli:
                if read[i:i+spikelen]==spike[1]:
                    return spike
    return ('0','') # the default value

def parse_spikes(path):
    """
    parse_spikes: reads spike configuration file into a list
    Arguments: path - path to the spike configuration file
    Returns: spikeli - the list of spikes in the following format: (SPIKE_ID, SPIKE)
    """
    spikeli = []
    with open(path) as spikefile:
        for line in spikefile:
            vals=line.split()
            spikeli.append((vals[0],vals[1])) # add all spikes to the list as (SPIKE_ID, SPIKE)
    return spikeli
    
def process_spikes(spikeli):
    """
    process_spikes: converts list of spikes into more detailed data about all spikes
    Arguments: spikeli - the list of spikes
    Returns:
        onechars: a dictionary with keys as positions where all spikes contain the same character, and values as the character
        multchars: a list of positions where spikes differ
        spikedata: a list of dictionaries for each position of a spike, which point a character to spikes with that character in that position
    """
    spikedata = ['']*len(spikeli[0][1]) # initialize
    onechars={}
    multchars=[]
    for charno in range(len(spikeli[0][1])):
        spikedata[charno]=defaultdict(set)
        for spike in spikeli:
            spikedata[charno][spike[1][charno]].add(spike) # build the spikedata dictionary for the specified position
        if len(spikedata[charno])==1:
            onechars[charno]=spikedata[charno].keys()[0] # add the single character and position to the dictionary
        else:
            multchars.append(charno)
    return onechars,multchars,spikedata
    
def dist_write(spikedict,path):
    """
    dist_write: writes the spike counts to a file
    Arguments:
        spikedict - the dictionary containing spike counts
        path - the path of the output file
    Returns: nothing
    Effects: creates an output file containing spike counts
    """
    with open(path, 'w') as outfile:
        kvpairs = []
        for key in spikedict:
            kvpairs.append((key, spikedict[key]))
        kvpairs = sorted(kvpairs, key=lambda pair: -pair[1]) # sort spikes in descending order by count
        for pair in kvpairs:
            outline=[pair[0][0],pair[0][1],str(pair[1])]
            outfile.write(','.join(outline)+'\n') # write the sorted list into the file
            
    
def main():
    """
    main: sets up command line arguments, then goes through the origin directory to find all fastq files, then calls parse_reads and then dist_write on the file and what is returned from parse_reads, respectively
    Arguments: none, but some arguments do come from the command line (see parser.add_argument help text)
    Returns: nothing
    Effects: Adds the output files to the origin directory
    """
    parser = argparse.ArgumentParser(description='Get inputs for the FASTQ counting script.') # set arguments
    parser.add_argument('spikes', help = 'The file containing spike data.')
    parser.add_argument('source', help = 'The directory to be searched.')
    args=parser.parse_args()
    
    spikeli = parse_spikes(args.spikes)
    onechars,multchars,spikedata=process_spikes(spikeli) # get the spikes and do some preprocessing
    
    for folder, subfolder, filelist in walk(args.source): # look through source folder for fastq files
        for file in filelist:
            name, exten = path.splitext(path.basename(file))
            if exten.lower() == '.fastq': # processes only fastq files
                if folder == args.source:
                    name = folder+name
                else:
                    name = folder + path.sep + name
                spikedict = parse_reads(name+'.fastq', onechars,multchars,spikedata,spikeli) # get the spike counts
                dist_write(spikedict, name+'.txt') # write the spike counts
    
if __name__=='__main__':
    main()