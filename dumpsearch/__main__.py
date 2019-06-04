#!/usr/bin/env python3
import sys, os, argparse, re
import parser as prs
# Outformat: %e:%n:%p:%h:%s:%t:%f:%l:%m:%d\n

'''
parameters:
email %e
username %n
password %p
hash %h
salt %s
hashtype %t
firstname %f
lastname %l
phone %m
dump %d

other:
birthdate %b
'''

def main():
    parser = argparse.ArgumentParser(description='Parse and search through datadumps.')
    parser.add_argument('formatfile', help="File containing parser format.")
    parser.add_argument('inpath', help="Path to either a file or a folder of files to parse.")
    parser.add_argument('outfile')
    parser.add_argument('dumpname')
    parser.add_argument('--ext', default=".txt", help="Extension of dump files in folder. Default: .txt")
    args = parser.parse_args()

    p = prs.Parser(args.formatfile, args.outfile)
    print("Format:", p.parseFormat)
    
    if os.path.isfile(args.inpath):
        p.parseFile(args.inpath, args.dumpname)
    elif os.path.isdir(args.inpath):
        p.parseFolder(args.inpath, args.dumpname, args.ext)
    else:
        print("Uknown inpath:", args.inpath)
        sys.exit(1)
    del p
    print("Done.")

if __name__ == '__main__':
    main()
