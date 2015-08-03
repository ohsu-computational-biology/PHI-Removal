"""
stripPHI.py - removes PHI from svs files stored in the input directory, saving them as tiles or fullsize images in the destination directory
"""

# import everything
import argparse # for parsing arguments
import shutil # for doing file tree operations
import subprocess # for running command line commands
from math import log10 # for computation (see line 37)
from os import path, walk, mkdir, remove # some filesystem functions
import multiprocessing

def convert(datatuple): # which makes main conversion function
    """
    convert: converts a file into a directory containing its tiles
    Arguments:
        filename: the name of the file to be converted (absolute path, without extension)
        ext_from: the file extension of the original file
        ext_to: the file extension that the converted tiles should have
        vips_path: the location of the vips binary (if vips is a command line program, this should just be 'vips')
        tile_width: the desired width of the tiles
        tile_height: the desired height of the tiles
        interactivity: the desired behavior of the program, 2 for more interactivity, 0 for silence, 1 for default
        fast_mode: True if fast mode is enabled, False otherwise - fast mode creates a .v intermediate file, which can be very large (for example, a 24K x 24K pixel image had a intermediate file size of )
        noverwrite: True if overwriting is not enabled
    Returns: 
        Nothing
    Effects:
        If interactivity is enabled, asks for confirmation on tile size
        Adds a directory containing tiled images into the destination directory
        Tiled images are to be saved as {0}-{1}.ext_to
        {0} represents the tile's x-position (0 leftmost, increasing to the right), and {1} represents the tile's y-position (0 topmost, increasing downwards)
        The values for {0} and {1} will be filled out with 0's in the front to make tile names alphabetical (for instance, 02 will appear before 13 rather than 2 appearing after 13)
    """
    filename,vips_path,ext_from,ext_to,tile_height,tile_width,interactivity,fast_mode,noverwrite=datatuple

    oldname = filename+'.'+ext_from # get the original filename
    tw,th = tile_width, tile_height
    
    if tile_width and tile_height:
    
        if noverwrite and path.exists(filename): # not overwriting existing directories
            if interactivity:
                print "Not overwriting: " + filename
            return
        mkdir(filename) # make the directory to contain tiles
        
        if fast_mode:
            command = vips_path + ' openslideload ' + oldname + ' ' + filename + '.v' # make intermediate file
            subprocess.call([command],shell = True)
            oldname=filename+'.v' # future operations now operate on intermediate file instead
        
        proc = subprocess.Popen([vips_path + " im_printdesc " + oldname], stdout=subprocess.PIPE, shell=True) # run the vips im_printdesc command, which returns metadata
        (out, err) = proc.communicate() # get the output of the command
        metadata =  out.split('\n') # metadata contains dimension data
        (width, height) = (0,0)
        for line in metadata: # look for width and height
            if not width and line.startswith('width: '):
                width = int(line.split()[1])
            elif not height and line.startswith('height: '):
                height = int(line.split()[1])
        
        if interactivity > 1: # Confirmation if extra interactivity is desired
            cont = False
            while (not cont):
                input = raw_input("Tile " + oldname + " into " + str(width//tw) + " wide x " + str(height//th) + " tall = " + str((width//tw)*(height//th)) + " tiles? (y/n/exit)")
                if not (input in 'yY'):
                    if input.lower() == "exit":
                        return
                    else: # allows resetting of tile size
                        tw = input("Input new tile width:")
                        th = input("Input new tile height:")
                        if tw <= 0 or th <= 0:
                            print "Invalid dimensions"
                else:
                    cont = True
        
        xsize = int(1+log10((width-1)//tw)) # the maximum number of digits for a x value for a file - will use to make filenames ordered logically
        ysize = int(1+log10((height-1)//th)) # the same for a y value
        
        concnum = 100 # number of extract_area calls to be processed at a time
        command = ''
        curcount = 0
        
        # tiling procedure
        for x in xrange((width-1)//tw): # make all full width tiles
            xstart = x*tw # the leftmost column to be in the current tile
            for y in xrange((height-1)//th): # full height tiles
                if interactivity:
                    print x, y
                ystart = y*th # the topmost row to be in the current tile
                name = (xsize-len(str(x)))*'0' + str(x) + '-' + (ysize-len(str(y)))*'0'+str(y) + '.' + ext_to # save the name of the tile
                curcount += 1
                command += vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(tw) + ' ' + str(th) + ' ;' # create a vips command to process the current tile
                if curcount >= concnum:
                    subprocess.call([command], shell = True) # call the vips command
                    command = ''
                    curcount = 0
            if height%th != 0: # if there is a remaining partial tile on the bottom of this column, perform the above procedure again for the partial tiles
                ystart += th
                name = (xsize-len(str(x)))*'0' + str(x) + '-' + str((height-1)//th) + '.' + ext_to
                curcount += 1
                command += vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(tw) + ' ' + str(height%th) + ' ;'
                if curcount >= concnum:
                    subprocess.call([command], shell = True)
                    command = ''
                    curcount = 0
                
        if width%tw != 0: # process leftover partial tiles on the right
            xstart += tw
            for y in xrange((height-1)//th):
                ystart = y*th
                name = str((width-1)//tw) + '-' + (ysize-len(str(y)))*'0'+str(y) + '.' + ext_to
                curcount += 1
                command += vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(width%tw) + ' ' + str(th) + ' ;'
                if curcount >= concnum:
                    subprocess.call([command], shell = True)
                    command = ''
                    curcount = 0
            if height%th != 0:
                ystart += th
                name = str((width-1)//tw) + '-' + str((height-1)//th) + '.' + ext_to
                command += vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(width%tw) + ' ' + str(height%th) + ' ;'
                if interactivity:
                    print command
                if curcount >= concnum:
                    subprocess.call([command], shell = True)
                    command = ''
                    curcount = 0
        if command != '':
            subprocess.call([command], shell = True) # runs any remaining operations
        if fast_mode:
            remove(oldname) # remove temporary file
    else:
        if noverwrite and path.isfile(filename + '.' + ext_to): # not overwriting existing files
            if interactivity:
                print "Not overwriting: " + filename + '.' + ext_to
            return
            
        if interactivity > 1:
            input = raw_input("Save " + oldname + " to " + filename + '.' + ext_to + "? (y/n)")
            if not input in 'yY':
                return
                
        if ext_to == 'png':
            command = vips_path + " pngsave " + oldname + ' ' + filename + '.' + ext_to
            if interactivity:
                print command
                command += ' --vips-progress'
            subprocess.call([command], shell = True)
            
        elif ext_to == 'tiff' or ext_to == 'tif':
            command = vips_path + " tiffsave " + oldname + ' ' + filename + '.' + ext_to
            if interactivity:
                print command
                command += ' --vips-progress'
            subprocess.call([command], shell = True)
    
    
def main():
    """
    main: sets up command line arguments, then goes through the origin directory to find all files to be processed, then runs the convert command on these
    Arguments: none, but some arguments do come from the command line (see parser.add_argument help text)
    Returns: nothing
    Effects: Makes a new directory to contain tiled image data from the origin directory
    """
    parser = argparse.ArgumentParser(description='Get inputs for the stripPHI script.') # set arguments
    parser.add_argument('source',help='The directory to be searched. Please use absolute path (the one that starts with /.')
    parser.add_argument('dest', help="The directory to contain the processed images. Please use absolute path. Input 'nopath' if the files are to be processed in place")
    parser.add_argument('-v', '--vips_path', default='vips',help='The location of vips')
    parser.add_argument('-f','--extension_from',default='svs',help='Extension to be converted from')
    parser.add_argument('-t','--extension_to',default='png',help='Extension to be converted to')
    parser.add_argument('-tw','--tile_width',default=0,type=int,help='Width of the tiles')
    parser.add_argument('-th','--tile_height', default=0,type=int,help='Height of the tiles')
    parser.add_argument('-q','--quick',action='store_true',help='Enables quick mode - creates a very large intermediate file to speed tiling operations')
    parser.add_argument('-i','--interactive',action='store_true',help='Enable interactivity - prompts for more verification')
    parser.add_argument('-s','--silent',action='store_true',help='Enable silence')
    parser.add_argument('-r','--recursive',action='store_true',help='Recursively process directory')
    parser.add_argument('-n','--no_overwrite',action='store_true',help='Do not overwrite existing files.')
    args = parser.parse_args()

    #process some arguments
    valid_read_exts = set(['svs'])
    #set(['png','tiff','jpeg','jpg','jfif','ppm','pgm','pbm','pfm','csv','exr','hdr','bmp','gif','hdf','jp2','jpf','jpx','j2c','j2k','pcx','pnm','ras','xwd','cur','ico','fits','fts','fit','webp','svs','tif','vms','vmu','ndpi','scn','mrxs','svslide','bif','v']) # prevent issues with reading files
    valid_write_exts = set(['png','tiff','tif','jpg','jpeg'])#,'pbm','pgm','ppm']) # and with writing them
    if not args.extension_from.lower() in valid_read_exts:
        print "Extension not valid - use only extension name, using only letters"
        exit(1)
    elif not args.extension_to.lower() in valid_write_exts:
        print "Extension not valid - use only extension name, using only letters"
        exit(1)
    elif args.tile_width<0:
        print "Please supply a valid (non-negative) tile_width."
        exit(1)
    elif args.tile_height<0:
        print "Please supply a valid (non-negative) tile_width."
        exit(1)
    interactivity = 1
    if args.silent:
        interactivity = 0
    if args.interactive:
        interactivity = 2
                
    if args.dest != 'nopath': # if a backup is desired
        if path.isdir(args.dest): # WARNING - deletes the destination folder entirely
            if interactivity:
                input = raw_input("Are you sure you want to remove " + args.dest + '? (y/n)')
                if not (input in 'yY'):
                    print "Exiting"
                    exit(0)
            shutil.rmtree(args.dest)
        shutil.copytree(args.source, args.dest) # backup into destination folder
        processfolder = args.dest
    else:
        processfolder = args.source # otherwise, just process in place
    
    filenames = []
        
    for object in walk(processfolder): # process in destination folder - original folder goes unmodified
        folder, subfolder, filelist = object
        for file in filelist: # loop through all files in the directory
            name, exten = path.splitext(path.basename(file)) # look at each extension
            if exten == '.'+args.extension_from: # if the extension indicates the desired filetype
                if folder == processfolder: # run convert command
                    filename = folder+name
                else:
                    if args.recursive: # if not recursive, don't process the file
                        filename=folder+path.sep+name
                    else:
                        filename=None
                if filename:
                    filenames.append((filename,args.vips_path,args.extension_from.lower(),args.extension_to.lower(),args.tile_height,args.tile_width,interactivity,args.quick,args.no_overwrite))
    
    count=multiprocessing.cpu_count()
    pool=multiprocessing.Pool(processes=count)
    pool.map(convert,filenames)
    pool.close()
    
if __name__ == '__main__':
    main()
