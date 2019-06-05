#!/usr/bin/env python3
import sys, ntpath, argparse
import parser as prs
import parseformat, guesser
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

def parse():
    parser = argparse.ArgumentParser(description='Parse datadumps.')
    parser.add_argument('formatfile', help="File containing parser format.")
    parser.add_argument('inpath', help="Path to either a file or a folder of files to parse.")
    parser.add_argument('outfile')
    parser.add_argument('--dumpname', default=None, help="Specify dumpname to be saved in database.")
    parser.add_argument('--ext', default=".txt", help="Extension of dump files in folder. Default: .txt")
    args = parser.parse_args(sys.argv[2:])

    parseFormat = parseformat.ParseFormat.loadFromFile(args.formatfile)
    p = prs.Parser(parseFormat, args.outfile)
    print("Format:", p.parseFormat)
    
    dumpname = args.dumpname if args.dumpname != None else ntpath.basename(ntpath.abspath(args.inpath))

    if ntpath.isfile(args.inpath):
        p.parseFile(args.inpath, dumpname)
    elif ntpath.isdir(args.inpath):
        p.parseFolder(args.inpath, dumpname, args.ext)
    else:
        print("Uknown inpath:", args.inpath)
        sys.exit(1)
    del p

def guess():
    parser = argparse.ArgumentParser(description='Guess parse format.')
    parser.add_argument('dumpfile', help="Path to dumpfile to analyze.")
    parser.add_argument('-f', default=None, help="File to store format in. Should be .json")
    args = parser.parse_args(sys.argv[2:])   

    g = guesser.Guesser()
    fmt = g.guessFormat(args.dumpfile, args.f)
    data = fmt.toJSON()
    print("Guess:")
    print('\n'.join(["%s: %s" % (k, repr(v)) for (k,v) in data.items()]))

def main():
    parser = argparse.ArgumentParser(usage="\nSubcommands:\n\tparse\n\tguess")
    parser.add_argument('command', help="Subcommand to run.")
    args = parser.parse_args(sys.argv[1:2])

    if args.command == "guess":
        guess()
    elif args.command == "parse":
        parse()
    else:
        print("Unknown command")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
