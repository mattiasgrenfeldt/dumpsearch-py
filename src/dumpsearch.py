#!/usr/bin/env python3
import sys, argparse, os, json
import os.path as path
import parseformat, guesser, exporter, db
import parser as prs

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('formatfile', help="File containing parser format.")
    parser.add_argument('inpath', help="Path to either a file or a folder of files to parse.")
    parser.add_argument('-c', "--config", help="DB config file. Default: dbconfig.json")
    parser.add_argument('-o', "--outfile", help="File to export to instead of exporting to DB.")
    parser.add_argument('-d', '--dumpname', default=None, help="Specify dumpname to be saved in database.")
    parser.add_argument('-e', '--ext', default=".txt", help="Extension of dump files in folder. Default: .txt")
    parser.add_argument('-j', '--junkfolder', default="junk", help="Where to dump parsing junk. Default: junk")
    args = parser.parse_args(sys.argv[2:])

    if args.outfile != None and args.config != None:
        print("[ERROR] You have to specify either a DB config file (-c) or an outfile (-o). Not both.")
        sys.exit(1)
    elif args.outfile != None:
        exp = exporter.FileExporter(args.outfile)
    else:
        config = args.config if args.config != None else "dbconfig.json"
        exp = db.DBConnection(config)

    parseFormat = parseformat.ParseFormat.loadFromFile(args.formatfile)
    p = prs.Parser(parseFormat, exp)

    print("Format:", p.parseFormat)
    
    dumpname = args.dumpname if args.dumpname != None else path.basename(path.abspath(args.inpath))
    if dumpname.find("junk") != -1:
        print("[ERROR Junk found in dumpname. Did you really want this? Specify a specific dumpname with -d")
        sys.exit(1)
    try:
        os.mkdir(args.junkfolder)
    except FileExistsError as e:
        pass

    if path.isfile(args.inpath):
        p.parseFile(args.inpath, dumpname, args.junkfolder)
    elif path.isdir(args.inpath):
        p.parseFolder(args.inpath, dumpname, args.junkfolder, args.ext)
    else:
        print("Uknown inpath:", args.inpath)
        sys.exit(1)
    del p
    print("[*] Dumpname:", dumpname)

def guess():
    parser = argparse.ArgumentParser()
    parser.add_argument('dumpfile', help="Path to dumpfile to analyze.")
    parser.add_argument('-f', default=None, help="File to store format in. Should be .json")
    args = parser.parse_args(sys.argv[2:])   

    g = guesser.Guesser()
    fmt = g.guessFormat(args.dumpfile, args.f)
    data = fmt.toJSON()
    print("Guess:")
    print('\n'.join(["%s: %s" % (k, repr(v)) for (k,v) in data.items()]))

def search():
    parser = argparse.ArgumentParser()
    parser.add_argument('field', help="The field to search. Available: %s." % (", ".join(db.FIELDS)))
    parser.add_argument('value', help="The value to search for.")
    parser.add_argument('-c', "--config", default="dbconfig.json", help="DB config file. Default: dbconfig.json")
    parser.add_argument('-n', default="10", help="The number of results to show.")
    parser.add_argument('--offset', default="0", help="The number of entries to skip in beginning of result")
    parser.add_argument('-o', help="File to dump results in.")
    parser.add_argument('--dont-build-indexes', action="store_true", help="Specify to not build indexes.")
    
    parser.add_argument('-r', '--regex', action="store_true", help="Value is a regex string to search with. Prefix searches with ^ will be fast and the rest is slow.")
    parser.add_argument('-j', '--json', action="store_true", help="Field doesn't matter. Value is a json MongoDB search object. For more advanced searches. Will be slow.")

    args = parser.parse_args(sys.argv[2:])

    if args.regex and args.json:
        print("[ERROR] Only one of --regex and --json can be specified.")
        sys.exit(1)

    database = db.DBConnection(args.config)
    if not args.dont_build_indexes:
        database.buildIndexes()

    n = int(args.n)
    offset = int(args.offset)

    res = database.search(args.field, args.value, n, offset, args.regex, args.json)

    print()
    if res[0] == int(1e5):
        print("[*] Found >%d results" % res[0])
    else:
        print("[*] Found %d results" % res[0])
    if args.o != None:
        print("[*] Dumping result[%d:%d] to %s" % (offset, offset + n, args.o))
        with open(args.o, "wb") as f:
            res = list(res[1])
            for i in range(len(res)):
                res[i].pop("_id")
            f.write(json.dumps(res).encode())
    elif res[0] != 0:
        res = list(res[1])
        colwidth = [max([len(res[i][field]) if field in res[i] else 0 for i in range(len(res))]) for field in parseformat.PARAMS_EXTENDED]
        columns = [(max(width, len(field)), field) for (width, field) in zip(colwidth, parseformat.PARAMS_EXTENDED) if width != 0]

        horizontalBorder = "+-" + "-+-".join(["-"*width for (width, _) in columns]) + "-+"
        print("[*] Showing result[%d:%d]" % (offset, offset + n))
        print(horizontalBorder)
        print("| " + " | ".join([col.ljust(width) for (width, col) in columns]) + " |")
        print(horizontalBorder)
        for r in res:
            print("| " + " | ".join([r.get(col, "").ljust(width) for (width, col) in columns]) + " |")
        print(horizontalBorder)
        print("[*] Showing result[%d:%d]" % (offset, offset + n))

def main():
    parser = argparse.ArgumentParser(usage="\nSubcommands:\n\tparse\n\tguess\n\tsearch")
    parser.add_argument('command', help="Subcommand to run.")
    args = parser.parse_args(sys.argv[1:2])

    if args.command == "search":
        search()
    elif args.command == "guess":
        guess()
    elif args.command == "parse":
        parse()
    else:
        print("Unknown command")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
