import os, progressbar
import parseformat

class Parser(object):    
    def __init__(self, parseFormat, outFileName):
        self.chunkSize = int(1e6)
        self.refillThreshold = self.chunkSize//10
        self.outFile = open(outFileName, "ab")
        self.parseFormat = parseFormat

    def __del__(self):
        self.outFile.close()

    def readChunk(self, file):
        return file.read(self.chunkSize)

    def parseFile(self, fileName, dumpName):
        print("[*] Parsing: %s" % fileName)
        file = open(fileName, "rb")
        fileSize = os.stat(fileName).st_size
        bar = progressbar.ProgressBar(max_value=fileSize)
        barCounter = 0

        buff = self.readChunk(file)

        buffPos = buff.find(self.parseFormat.prefixJunk) + len(self.parseFormat.prefixJunk)
        suffixPos = buff.find(self.parseFormat.suffixJunk, buffPos)

        fmt = self.parseFormat.format
        dumpName = dumpName.encode()
        while len(buff) and buffPos != suffixPos:

            endOfLinePos = buff.find(self.parseFormat.lineDelimiter, buffPos)
            if endOfLinePos == -1:
                print("[WARN] Can't find next end of line. Stopping parsing.")
                bar.finish()
                file.close()
                return False

            line = buff[buffPos:endOfLinePos]
            values = line.split(self.parseFormat.delimiter)
            if len(values) != len(self.parseFormat.format):
                print("[ERROR] Line has %d fields, expected %d. Bad line!" % (len(values), len(self.parseFormat.format)))
            else:
                info = {k:v for (k,v) in zip(self.parseFormat.format.decode(), values)}
                info['d'] = dumpName
                self.outFile.write(b':'.join([info.get(x, b"").strip() for x in parseformat.ParseFormat.PARAMS]) + b"\n")

            buffPos = endOfLinePos + len(self.parseFormat.lineDelimiter)

            if len(buff) - buffPos < self.refillThreshold:
                barCounter += buffPos
                bar.update(barCounter)
                buff = buff[buffPos:] + self.readChunk(file)
                buffPos = 0
                suffixPos = buff.find(self.parseFormat.suffixJunk)
        file.close()
        bar.finish()
        return True

    def parseFolder(self, folderName, dump, ext='.txt'):
        files = os.listdir(folderName)
        files = [f for f in files if f.endswith(ext)]
        print("[*] Parsing %d files." % len(files))
        errorFiles = []
        for f in files:
            if not self.parseFile(os.path.join(folderName, f), dump):
                errorFiles.append(f)
        if len(errorFiles):
            print("[ERROR] Problems were found while parsing the following files:")
            print(errorFiles)
