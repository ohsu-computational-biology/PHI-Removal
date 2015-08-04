"""
comparefastqout.py: compares the output file from running fastqcount.py with an expected output file generated from injectspikes.py
Matthew Jagielski - jagielsk@ohsu.edu
"""

import argparse
import injectspikes, fastqcount

def compare(correctpath,testpath):
    """
    compare: compares the expected and actual files
    Arguments:
        correctpath - the expected output path
        testpath - the actual output file
    Returns: boolean - True if the files are the same up to ordering, False if not
    Effects: if the files are not the same, the position of the first difference will be printed
    """
    with open(correctpath) as correctfile: # open both files
        with open(testpath) as testfile:
            correctspikes = [('','',0)] # initialize
            testspikes = correctspikes[:]
            for correctline in correctfile:
                correctline=correctline.strip().split(',')
                testline=testfile.readline().strip().split(',')
                
                if correctline[2]==correctspikes[0][2]: # build up a list of spikes with the same counts
                    correctspikes.append(correctline)
                    testspikes.append(testline)
                    
                else:
                    if sorted(correctspikes, key=lambda tup: tup[1])!=sorted(testspikes, key=lambda tup: tup[1]): # sort to check for equivalence
                        print("Error", correctspikes)
                        return False
                    correctspikes=[correctline]
                    testspikes=[testline]
    return True
    
def main():
    parser = argparse.ArgumentParser(description='Get inputs for the FASTQ modifying script.') # set arguments
    parser.add_argument('correct', help = 'The file containing the correct spike distributions.')
    parser.add_argument('test', help = 'The file to be checked for correctness.')
    args=parser.parse_args()

    if compare(args.correct,args.test):
        print("woo") # Success!

if __name__=='__main__':
    main()