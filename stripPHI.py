# import everything
import argparse # for parsing arguments
import shutil # for doing file tree operations
import subprocess # for running command line commands
from math import log10 # for computation (see line 37)
from os import path, walk, mkdir # some filesystem functions

def convert(filename,ext_from,ext_to,vips_path,tile_width,tile_height):
    """
    convert: converts a file into a directory containing its tiles
    Arguments:
        filename: the name of the file to be converted (absolute path, without extension)
        ext_from: the file extension of the original file
        ext_to: the file extension that the converted tiles should have
        vips_path: the location of the vips binary (if vips is a command line program, this should just be 'vips')
        tile_width: the desired width of the tiles
        tile_height: the desired height of the tiles
    Returns: 
        Nothing
    Effects:
        Adds a directory containing tiled images into the destination directory
        Tiled images are to be saved as {0}-{1}.ext_to
        {0} represents the tile's x-position (0 leftmost, increasing to the right), and {1} represents the tile's y-position (0 topmost, increasing downwards)
        The values for {0} and {1} will be filled out with 0's in the front to make tile names alphabetical (for instance, 02 will appear before 13 rather than 2 appearing after 13)
    """
    
    oldname=filename+'.'+ext_from # get the original filename
    mkdir(filename) # make the directory to contain tiles
    
    proc = subprocess.Popen([vips_path + " im_printdesc " + oldname], stdout=subprocess.PIPE, shell=True) # run the vips im_printdesc command, which returns metadata
    (out, err) = proc.communicate() # get the output of the command
    metadata =  out.split('\n')[1:3] # we only want lines 2 and 3, which contain dimension data

    width = int(metadata[0].split()[1]) # get image dimensions
    height = int(metadata[1].split()[1])
    
    xsize = int(1+log10((width-1)//tile_width)) # the maximum number of digits for a x value for a file - will use to make filenames ordered logically
    ysize = int(1+log10((height-1)//tile_height)) # the same for a y value
    
    # tiling procedure
    for x in xrange((width-1)//tile_width): # make all full width tiles
        xstart = x*tile_width # the leftmost column to be in the current tile
        for y in xrange((height-1)//tile_height): # full height tiles
            print x, y
            ystart = y*tile_height # the topmost row to be in the current tile
            name = (xsize-len(str(x)))*'0' + str(x) + '-' + (ysize-len(str(y)))*'0'+str(y) + '.' + ext_to # save the name of the tile
            command = vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(tile_width) + ' ' + str(tile_height) # create a vips command to process the current tile
            #print command # 
            subprocess.call([command], shell=True) # call the vips command
        if height%tile_height!=0: # if there is a remaining partial tile on the bottom of this column, perform the above procedure again for the partial tiles
            ystart+=tile_height
            name = (xsize-len(str(x)))*'0' + str(x) + '-' + str((height-1)//tile_height) + '.' + ext_to
            command = vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(tile_width) + ' ' + str(height%tile_height)
            #print command #
            subprocess.call([command], shell=True)
            
    if width%tile_width!=0: # process leftover partial tiles on the right
        xstart+=tile_width
        for y in xrange((height-1)//tile_height):
            ystart = y*tile_height
            name = str((width-1)//tile_width) + '-' + (ysize-len(str(y)))*'0'+str(y) + '.' + ext_to
            command = vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(width%tile_width) + ' ' + str(tile_height)
            #print command # 
            subprocess.call([command], shell=True)
        if height%tile_height!=0:
            ystart+=tile_height
            name = str((width-1)//tile_width) + '-' + str((height-1)//tile_height) + '.' + ext_to
            command = vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(width%tile_width) + ' ' + str(height%tile_height)
            print command #
            subprocess.call([command], shell=True)

def main():
    """
    main: sets up command line arguments, then goes through the origin directory to find all files to be processed, then runs the convert command on these
    Arguments: none, but some arguments do come from the command line (see parser.add_argument help text)
    Returns: nothing
    Effects: Makes a new directory to contain tiled image data from the origin directory
    """
    parser = argparse.ArgumentParser(description='Get inputs for the stripPHI script.') # set arguments
    parser.add_argument('source',help='The directory to be searched.')
    parser.add_argument('dest', help='The directory to contain the processed images.')
    parser.add_argument('-v', '--vips_path', default='vips',help='The location of vips')
    parser.add_argument('-f','--extension_from',default='svs',help='Extension to be converted from')
    parser.add_argument('-t','--extension_to',default='png',help='Extension to be converted to')
    parser.add_argument('-tw','--tile_width',default=256,help='Width of the tiles')
    parser.add_argument('-th','--tile_height', default=256,help='Height of the tiles')
    args = parser.parse_args()

    valid_read_exts = set(['png','tiff','jpeg','jpg','jfif','ppm','pgm','pbm','pfm','csv','exr','hdr','bmp','gif','hdf','jp2','jpf','jpx','j2c','j2k','pcx','pnm','ras','xwd','cur','ico','fits','fts','fit','webp','svs','tif','vms','vmu','ndpi','scn','mrxs','svslide','bif','v']) # prevent issues with reading files
    valid_write_exts = set(['png','tiff','tif','jpg','jpeg','pbm','pgm','ppm']) # and with writing them
    if not args.extension_from.lower() in valid_read_exts:
        print "Extension not valid - use only extension name, using only letters"
        exit(1)
    elif not args.extension_to.lower() in valid_write_exts:
        print "Extension not valid - use only extension name, using only letters"
        exit(1)
        
    if path.isdir(args.dest): # WARNING - deletes the destination folder entirely
        input = raw_input("Are you sure you want to remove " + args.dest + '? (y/n)')
        if not (input in 'yY'):
            print "Exiting"
            exit(0)
        shutil.rmtree(args.dest)
    shutil.copytree(args.source, args.dest) # backup into destination folder
    for object in walk(args.dest): # process in destination folder - original folder goes unmodified
        folder, subfolder, filelist = object
        for file in filelist: # loop through all files in the directory
            name, exten = path.splitext(path.basename(file)) # look at each extension
            if exten=='.'+args.extension_from: # if the extension indicates the desired filetype
                if folder==args.dest: # run convert command
                    convert(folder+name,args.dest,args.extension_from,args.extension_to,args.vips_path,args.tile_height,args.tile_width)
                else:
                    convert(folder+path.sep+name,args.dest,args.extension_from,args.extension_to,args.vips_path,args.tile_height,args.tile_width)
    
if __name__ == '__main__':
    main()
