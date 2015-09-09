# PHI-Removal
Removes PHI from .svs files

Latest revision: 7/23/15
Matthew Jagielski: jagielsk@ohsu.edu

Summary
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
