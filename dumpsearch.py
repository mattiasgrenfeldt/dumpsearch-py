#!/usr/bin/env python3
import sys, json, os, progressbar, argparse

# Outformat: %e:%n:%p:%h:%s:%t:%f:%l:%m:%d\n
PARAMS = "enphstflmdJ"

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

class ParseFormat(object):
    def __init__(self, fileName):
        with open(fileName, "rb") as f:
            parseObject = json.loads(f.read())
        self.prefixJunk = parseObject.get("prefixjunk", "").encode()
        self.suffixJunk = parseObject.get("suffixjunk", "").encode()
        if self.suffixJunk == b"":
            self.suffixJunk = b"\x00"*5
        
        f = parseObject["parseformat"]
        self.formatIsVar = []
        self.format = []
        i = 0
        while i < len(f):
            if f[i] == '%':
                if i == len(f)-1:
                    print("[ERROR] Parse format can't end in %. Did you mean %%?")
                    sys.exit(1)
                elif f[i+1] == '%':
                    i += 1
                else:
                    if f[:i] != "":
                        self.format.append(f[:i].replace("%%", '%').encode())
                        self.formatIsVar.append(False)
                    assert f[i+1] in PARAMS, "[ERROR] Uknown parse format paramter: %s" % f[i:i+2]
                    self.format.append(f[i:i+2].encode())
                    self.formatIsVar.append(True)
                    f = f[i+2:]
                    i = 0
                    continue
            i += 1
        if f != "":
            self.format.append(f.replace("%%", '%').encode())
            self.formatIsVar.append(False)
        assert not self.formatIsVar[-1], "[ERROR] Parse format must end in delimeter. Did you want '\\n' at the end?"

    def __str__(self):
        return b"".join(self.format).decode().strip()

class Parser(object):
    def __init__(self, formatFileName, outFileName):
        self.chunkSize = int(1e6)
        self.outFile = open(outFileName, "ab")
        self.parseFormat = ParseFormat(formatFileName)

    def __del__(self):
        self.outFile.close()

    def readChunk(self, file):
        return file.read(self.chunkSize)

    # Outformat: %e:%n:%p:%h:%s:%t:%f:%l:%m:%d\n
    def parseFile(self, fileName, dump):
        print("[*] Parsing: %s" % fileName)
        file = open(fileName, "rb")
        fileSize = os.stat(fileName).st_size
        bar = progressbar.ProgressBar(max_value=fileSize)
        barCounter = 0

        buff = self.readChunk(file)
        buffPos = buff.find(self.parseFormat.prefixJunk) + len(self.parseFormat.prefixJunk)
        suffixPos = buff.find(self.parseFormat.suffixJunk, buffPos)

        fmt = self.parseFormat.format
        while len(buff) and buffPos != suffixPos:
            info = {"d":dump.encode()}

            startIndex = 0
            if not self.parseFormat.formatIsVar[0]:
                startIndex = 1
                buffPos = buff.find(fmt[0], buffPos) + len(fmt[0])

            for i in range(startIndex, len(fmt), 2):
                delimPos = buff.find(fmt[i+1], buffPos)
                info[chr(fmt[i][1])] = buff[buffPos:delimPos]
                buffPos = delimPos + len(fmt[i+1])

            self.outFile.write(b':'.join([info.get(x, b"") for x in PARAMS[:-1]]) + b"\n")

            if len(buff) - buffPos < self.chunkSize//10:
                barCounter += buffPos
                bar.update(barCounter)
                buff = buff[buffPos:] + self.readChunk(file)
                buffPos = 0
                suffixPos = buff.find(self.parseFormat.suffixJunk)

    def parseFolder(self, folderName, dump, ext='.txt'):
        files = os.listdir(folderName)
        files = [f for f in files if f.endswith(ext)]
        print("[*] Parsing %d files." % len(files))
        for f in files:
            self.parseFile(os.path.join(folderName, f), dump)

def main():
    parser = argparse.ArgumentParser(description='Parse and search through datadumps.')
    parser.add_argument('formatfile', help="File containing parser format.")
    parser.add_argument('inpath', help="Path to either a file or a folder of files to parse.")
    parser.add_argument('outfile')
    parser.add_argument('dumpname')
    parser.add_argument('--ext', help="Extension of dump files in folder. Default: .txt")
    args = parser.parse_args()
    print(args)

    p = Parser(args.formatfile, args.outfile)
    print("Format:", p.parseFormat)

    if os.path.isfile(args.inpath):
        p.parseFile(args.inpath, args.dumpname)
    elif os.path.isdir(args.inpath):
        p.parseFolder(args.inpath, args.dumpname)
    else:
        print("Uknown inpath:", args.inpath)
        sys.exit(1)
    del p
    print("Done.")

if __name__ == '__main__':
    main()
