
=====================================================================================
PHI Removal =========================================================================
=====================================================================================

Removes PHI from .svs files
Latest revision: 7/23/15
Matthew Jagielski: jagielsk@ohsu.edu

stripPHI.py provides a way of converting a directory containing svs files into a directory containing tiles of the main image from the svs files. This removes the PHI contained in the other images also contained in an svs file.

Inputs:

1.	A directory containing images that should have PHI removed (required)
2.	A directory to contain the processed images (required, if this directory already exists you will be prompted to overwrite it completely)
3.	A destination file type – the processed images will have this file type (just the file extension in lowercase, no period, optional – defaults to png, fully supports png, untested for tiff, jpeg)
4.	Tile width – the width of the output tiles (in pixels, optional – defaults to 0, if 0 is provided no tiles will be made – just one image)
5.	Tile height – the height of the output tiles (in pixels, optional - defaults to 0, if 0 is provided no tiles will be made – just one image)

Examples:

1.	python stripPHI.py –h

This will provide a list of available command line options.

2.	python stripPHI.py /path/to/input /path/to/output

This will simply convert every svs file from /input to a png file of the base image from the svs, stored in /output

3.	python stripPHI.py /path/to/input /path/to/output –tw 1024 –th 1024

This will convert every svs file from /input to a directory of png tiles of size 1024x1024 pixels, saved in /output.

4.	python stripPHI.py /path/to/input /path/to/output –t tiff

This will do the same thing as (1), except the files will be in TIFF format. Note that TIFF files cannot be larger than 4GB. This may not work properly, as the TIFF format remains untested.

5.	python stripPHI.py /path/to/input nopath

The nopath argument in place of the destination directory will specify that the conversions are all to be done in place. This is useful if there are a large number of files that are already backed up somewhere, so that copying all the files would take a long time.

Outputs:

A directory containing all files from the original directory

If either tile width or height was specified as 0 (or if either argument was not specified), then in place of each svs file from the original directory called /path/to/input/example.svs, there will be a file called /path/to/output/example.png (or a different extension, if one was specified). 

Otherwise, if neither the width nor height of a tile was set as 0, then in place of each svs file from the original directory called /path/to/input/example.svs, there will be a directory called /path/to/output/example/. In example/, there will be images titled x-y.png, where x is the x position of the tile, and y is the y position of the tile. For example, the upper left tile will be titled 000-000.png, with the tile to its right being titled 001-000.png and the tile below it titled 000-001.png.

Architecture

This solution uses Python to interact with the libvips command line interface. Python checks that arguments provided are valid, then creates the output directory and goes through this new directory and all subdirectories, processing these files. As a result, images from the original directory are unmodified.

The processing step involves determining the dimensions of the base image, then proceeding to tell libvips (which works with the openslide library) to extract regions of the image until the image has been completely tiled.

In order to install libvips with openslide (both are required), a script is available here: https://github.com/lovell/sharp/blob/master/preinstall.sh

If this doesn’t work, instructions are available at their respective download sites (download openslide first – this allows vips to configure itself to accept openslide):
openslide: http://openslide.org/download/
libvips: http://www.vips.ecs.soton.ac.uk/index.php?title=Supported
Openslide 3.4.1 is recommended (>=3.3.0 required)
Vips 8.0.2 is recommended (>=8.0.0 required)

=====================================================================================
FASTQ spike processing ==============================================================
=====================================================================================

Design Document for FASTQ spike counting
Latest revision: 8/18/15
Matthew Jagielski – jagielsk@ohsu.edu
Fastqcount.py and injectspikes.py can be found at:
https://github.com/ohsu-computational-biology/misc_utilities
   
   
Summary – fastqcount.py takes in an inputted spike configuration file and a directory containing FASTQ files, and produces a file with counts of each spike.

Fastq file format: For full explanation, see https://en.wikipedia.org/wiki/FASTQ_format
Each fastq file contains several sequences, documented with four lines –
1.	A sequence identifier starting with @.
2.	The read – the letters for the sequence.
3.	+, potentially followed by the sequence identifier.
4.	Quality values.
The job, then, is to process the second line for each sequence (which there can be many thousands of per file).

Spike configuration file format:
The spike configuration file is a space separated text file with the following format:
SPIKE_ID   SPIKE V J
DM_1   TAAGTCGACAAACAGCCGTGTTGAGGTCGACTTA V1- J1-1
DM_2 TAAGTCGACAAACTCCTAAGCACCCGTCGACTTA V1- J1-2
Each spike has its spike ID before the 34 character string. Each spike has its own line, separated by newline characters. A header line contains all the fields specified in the document.

Inputs:
1.	Spike configuration file
2.	Directory containing FASTQ files
3.	The –r flag specifies that those records containing spikes will be removed in an output fastq file

Examples:	
1.	python fastqcount.py spike_config.txt /path/to/fastqs/
This will read spike_config.txt as the list of spikes, and process all fastq files from /path/to/fastqs/ into spike distributions.
2.	Python fastqcount.py spike_config.txt /path/to/fastqs/ -r
This will do the same thing as 1, except each fastq will have a corresponding fastq file without any spikes.

Outputs:
	A file formatted with comma-separated values with a line for each spike: 
SPIKE_ID, SPIKE, COUNT
The file /path/to/example.fastq will result in a file titled path/to/example.txt.
   
Testing:
injectspikes.py – this adds spikes to random reads in a fastq file, and produces a file in the same layout as the output file of fastqcount.py
Usage:
python injectspikes.py spike_config.txt /path/to/fastqs/
This will process all fastq files in fastqs/:  any /path/to/fastqs/example.fastq will have a corresponding /path/to/fastqs/examplemod.fastq and a /path/to/fastqs/examplexout.txt. 
Run fastqcount.py with examplemod.fastq, and the produced examplemod.txt should be the same as examplexout.txt.
A test suite has also been provided:

Test suite:
The test suite for fastqcount.py is located at /mnt/lustre1/CompBio/fastqtest/ on ExaCloud. The file structure is:
fastqtest
fastqtest/tiny_barcodes.txt – the spike configuration file for testing, containing 3 spikes
fastqtest/injectspikes.py – the file for adding spikes to a fastq, added for convenience
fastqtest/fastqcount.py – the fastq spike counting file

fastqtest/input
fastqtest/input/tiny.fastq – a small test fastq file, containing 10 reads, 5 of them spiked
fastqtest/input/CO506CO477beta10mod.fastq – the larger test file, containing 429811 reads, 19416 of them spiked

fastqtest/expected
fastqtest/expected/tiny.txt – the real counts for the small fastq file
fastqtest/expected/tinyrm.txt – the small fastq file with spiked reads removed
fastqtest/expected/ CO506CO477beta10xout.txt – the real counts for the larger fastq file, generated by injectspikes.py
fastqtest/expected/ CO506CO477beta10modrm.fastq – the large fastq file with spiked reads removed, generated by injectspikes.py

The following will produce files for comparison:
python fastqcount.py tiny_barcodes.txt input/ -r
One can then run diff to compare new files in input/ with files from expected/
Input/tiny.txt and expected/tiny.txt
Input/tinyrm.fastq and expected/tinyrm.fastq 
Input/CO506CO477beta10mod.txt and expected/CO506CO477beta10xout.txt
Input/CO506CO477beta10modrm.fastq and expected//CO506CO477beta10modrm.fastq

Architecture:
Dependencies:
Python modules: argparse, collections, os, and random, all default installed by any version of python 2.7 or newer
Functions:
main() – gets command line arguments, calls parsespikes(), and traverses the directory, calling parsereads() on the fastq files, and finally calling distwrite() using the output from parsereads()

parsespikes(path) – takes the spike configuration file and parses it into a list of spikes
input: path – the path to the spike configuration file
output: spikeli – the list of spikes, stored as tuples: (SPIKE_ID, SPIKE)

parsereads(path, spikeli) – creates a dictionary to store counts, opens the fastq file, and calls process() on each read, incrementing the dictionary value for the spike that is identified by process()
input: path – the path to the fastq file
spikeli – the output from parsespikes, the list of spikes in tuple form
output: spikedict – the dictionary which stores counts of each spike, as well as the count for no spikes

process(read, spikeli) – looks for each spike in the read, returning the first spike that is found in the read
input: read – the read, just the line containing genetic information
spikeli – the output from parsespikes, the list of spikes in tuple form
output: spike – the spike that is identified in the read, which is an empty string if no spike is found

distwrite(spikedict, path) – makes a list out of spikedict, sorts it, and then creates a comma-separated file with each line containing: SPIKE_ID,SPIKE,COUNT
input: spikedict – the dictionary which stores counts of each spike, as well as the count for no spikes
path – the desired path to the output file
output: creates a file containing comma-separated values for each spike

Desired changes:  maybe some analysis of patterns in reads as well
This would consist of a processing step called in parsespikes(), and perhaps some processing step called in parsereads() periodically while reading the file

