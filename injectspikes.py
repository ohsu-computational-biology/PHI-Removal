"""
injectspikes.py: randomly adds spikes to a fastq file, resulting in another fastq file and an output file containing spike counts
Matthew Jagielski - jagielsk@ohsu.edu
"""

# import everything
from os import path, walk
import argparse
from random import randint

def rewrite_fastq(basename,spikeli):
    """
    rewrite_fastq: makes the modified fastq file and the spike count file
    Arguments:
        basename - the name of the file without the fastq extension
        spikeli - the list of spikes, see parse_spikes doc for details
    Returns: nothing
    Effects: creates two files: 
        modified fastq - a copy of the original fastq file, just with some randomly added spikes
        expected output file - a text file containing the expected output from fastqcount.py in the same format, although spikes with
            the same counts may be sorted differently, equivalence can be checked with comparefastqout.py
    """
    occli = [0]*len(spikeli) # keep track of occurrences of each spike
    fails = 0 # and the number of reads without spikes added
    with open(basename+'.fastq') as readfile:
        with open(basename+'mod.fastq','w') as newfastq:
            for i,line in enumerate(readfile):
                if i%10000==0: # just some progress notification
                    print i
                curline=line
                
                if i%4==1 and randint(0,21)>20: # 1/20 or so probability of adding a spike, and only on read lines
                    spikeno=randint(0,len(spikeli)-1) # add a random spike
                    occli[spikeno]+=1
                    
                    indno = randint(10,len(line)-len(spikeli[spikeno][1])-1) # choose somewhere to put the spike
                    curline=curline[:indno]+spikeli[spikeno][1]+curline[indno+len(spikeli[spikeno][1]):]
                
                elif i%4==1:
                    fails+=1
                
                newfastq.write(curline) # write the line
                
    with open(basename+'xout.txt','w') as expout: # write the output file
        expout.write(','.join(['0','',str(fails)])+'\n') # the no spike count
        occsorted=sorted(enumerate(occli),key=lambda pair: (-pair[1],spikeli[pair[0]][1])) # sort the spikes according to order of appearance
        for spikevals in occsorted:
            expout.write(','.join([spikeli[spikevals[0]][0],spikeli[spikevals[0]][1],str(spikevals[1])])+'\n') # and write it all into the file
    
    occdict = {}
    occdict[('0','')]=fails
    for i in range(len(spikeli)):
        occdict[spikeli[i]]=occli[i]
    return occdict
        
        
def parse_spikes(path):
    """
    parse_spikes: read the spikes from the spike configuration file into a list
    Arguments: path - the path to the spike configuration file
    Returns: spikeli - the list containing all spikes in the following format: (SPIKE_ID,SPIKE)
    """
    spikeli = []
    with open(path) as spikefile: 
        for line in spikefile:
            vals=line.split()
            spikeli.append((vals[0],vals[1]))
    return spikeli

def main():
    parser = argparse.ArgumentParser(description='Get inputs for the FASTQ modifying script.') # set arguments
    parser.add_argument('spikes', help = 'The file containing spike data.')
    parser.add_argument('source', help = 'The directory to be modified.')
    args=parser.parse_args()
    
    spikeli = parse_spikes(args.spikes) # get the list of spikes
    
    assert (path.exists(args.source))
    for folder, subfolder, filelist in walk(args.source): # look through source folder for fastq files
        for file in filelist:
            name, exten = path.splitext(path.basename(file))
            if exten.lower() == '.fastq': # processes only fastq files
                if folder == args.source:
                    name = folder+name
                else:
                    name = folder + path.sep + name
                spikedict = rewrite_fastq(name,spikeli) # modify the source file

if __name__=='__main__':
    main()