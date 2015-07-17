import argparse
import shutil
import subprocess
from math import log10
from os import path, walk, mkdir

def convert(filename,dest,ext_from,ext_to,vips_path,tile_width,tile_height):
    oldname=filename+'.'+ext_from
    mkdir(filename)
    proc = subprocess.Popen([vips_path + " im_printdesc " + oldname], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    metadata =  out.split('\n')[1:3]

    width = int(metadata[0].split()[1])
    height = int(metadata[1].split()[1])
    
    xsize = int(1+log10((width-1)//tile_width)) # the maximum number of digits for a x value for a file - will use to make filenames ordered logically
    ysize = int(1+log10((height-1)//tile_height)) # the same for a y value
    
    for x in xrange((width-1)//tile_width):
        xstart = x*tile_width
        for y in xrange((height-1)//tile_height):
            print x, y
            ystart = y*tile_height
            name = (xsize-len(str(x)))*'0' + str(x) + '-' + (ysize-len(str(y)))*'0'+str(y) + '.' + ext_to
            command = vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(tile_width) + ' ' + str(tile_height)
            #print command # 
            subprocess.call([command], shell=True)
        if height%tile_height!=0:
            ystart+=tile_height
            name = (xsize-len(str(x)))*'0' + str(x) + '-' + str((height-1)//tile_height) + '.' + ext_to
            command = vips_path + " extract_area " + oldname + ' ' + filename + path.sep + name + ' ' + str(xstart) + ' ' + str(ystart) + ' ' + str(tile_width) + ' ' + str(height%tile_height)
            #print command #
            subprocess.call([command], shell=True)
            
    if width%tile_width!=0:
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
    remove(oldname)

def main():
    parser = argparse.ArgumentParser(description='Get inputs for the stripPHI script.')
    parser.add_argument('source',help='The directory to be searched.')
    parser.add_argument('dest', help='The directory to contain the processed images.')
    parser.add_argument('-v', '--vips_path', default='vips',help='The location of vips')
    parser.add_argument('-f','--extension_from',default='svs',help='Extension to be converted from')
    parser.add_argument('-t','--extension_to',default='png',help='Extension to be converted to')
    parser.add_argument('-tw','--tile_width',default=256,help='Width of the tiles')
    parser.add_argument('-th','--tile_height', default=256,help='Height of the tiles')
    args = parser.parse_args()

    valid_read_exts = set(['png','tiff','jpeg','jpg','jfif','ppm','pgm','pbm','pfm','csv','exr','hdr','bmp','gif','hdf','jp2','jpf','jpx','j2c','j2k','pcx','pnm','ras','xwd','cur','ico','fits','fts','fit','webp','svs','tif','vms','vmu','ndpi','scn','mrxs','svslide','bif','v'])
    valid_write_exts = set(['png','tiff','tif','jpg','jpeg','pbm','pgm','ppm'])
    if not args.extension_from.lower() in valid_read_exts:
        print "Extension not valid - use only extension name, using only letters"
        exit(1)
    elif not args.extension_to.lower() in valid_write_exts:
        print "Extension not valid - use only extension name, using only letters"
        exit(1)
        
    if path.isdir(args.dest): # WARNING - deletes the destination folder entirely
        input = raw_input("Are you sure you want to remove " + args.dest + '? (y/n)')
        if not input in ['y','Y']:
            print "Exiting"
            exit(0)
        shutil.rmtree(args.dest)
    shutil.copytree(args.source, args.dest)
    for object in walk(args.dest):
        folder, subfolder, filelist = object
        for file in filelist: # loop through all files in the directory
            name, exten = path.splitext(path.basename(file)) # look at each extension
            if exten=='.'+args.extension_from: # if the extension is correct
                if folder==args.dest:
                    convert(folder+name,args.dest,args.extension_from,args.extension_to,args.vips_path,args.tile_height,args.tile_width)
                else:
                    convert(folder+path.sep+name,args.dest,args.extension_from,args.extension_to,args.vips_path,args.tile_height,args.tile_width)
    
if __name__ == '__main__':
    main()
