from os import path
import argparse
from random import randint

def rewrite_fastq(basename,spikeli):
    occli = [0]*len(spikeli)
    fails = 0
    with open(basename+'.fastq') as readfile:
        with open(basename+'mod.fastq','w') as newfastq:
            for i,line in enumerate(readfile):
                if i%10000==0:
                    print i
                curline=line
                if i%4==1 and randint(0,21)>20:
                    spikeno=randint(0,len(spikeli)-1)
                    occli[spikeno]+=1
                    indno = randint(10,len(line)-1)
                    curline=curline[:indno]+spikeli[spikeno][1]+curline[indno+len(spikeli[spikeno][1]):]
                elif i%4==1:
                    fails+=1
                if not curline.endswith('\n'):
                    curline+='\n'
                newfastq.write(curline)
    with open(basename+'xout.txt','w') as expout:
        expout.write(','.join(['0','',str(fails)])+'\n')
        occsorted=sorted(enumerate(occli),key=lambda pair: -pair[1])
        for spikevals in occsorted:
            expout.write(','.join([spikeli[spikevals[0]][0],spikeli[spikevals[0]][1],str(spikevals[1])])+'\n')
        
        
def parse_spikes(path):
    spikeli = []
    with open(path) as spikefile:
        for line in spikefile:
            vals=line.split()
            spikeli.append((vals[0],vals[1]))
    return spikeli

def main():
    parser = argparse.ArgumentParser(description='Get inputs for the FASTQ modifying script.') # set arguments
    parser.add_argument('spikes', help = 'The file containing spike data.')
    parser.add_argument('source', help = 'The file to be modified.')
    args=parser.parse_args()
    
    spikeli = parse_spikes(args.spikes)
    
    assert (path.isfile(args.source))
    name, exten = path.splitext(path.basename(args.source)) # only want to deal with fastq files
    if exten.lower() == '.fastq': # if the extension indicates the desired filetype
        spikedict = rewrite_fastq(name,spikeli)    

if __name__=='__main__':
    main()