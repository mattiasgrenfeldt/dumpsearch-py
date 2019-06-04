import os, progressbar
import parseformat

class Parser(object):
    PARAMS = "enphstflmd"
    JUNK_PARAM = 'J'
    DELIMITERS = ":;,| \t"
    LINE_DELIMITERS = ["\n", "\r\n"]
    
    def __init__(self, formatFileName, outFileName):
        self.chunkSize = int(1e6)
        self.refillThreshold = self.chunkSize//10
        self.outFile = open(outFileName, "ab")
        self.parseFormat = parseformat.ParseFormat(formatFileName, Parser.PARAMS, Parser.JUNK_PARAM)

    def __del__(self):
        self.outFile.close()

    def readChunk(self, file):
        return file.read(self.chunkSize)

    # Outformat: %e:%n:%p:%h:%s:%t:%f:%l:%m:%d\n
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
            info = {"d":dumpName}

            endOfLinePos = buff.find(fmt[-1], buffPos)
            if endOfLinePos == -1:
                print("[WARN] Can't find next end of line. Stopping parsing.")
                bar.finish()
                return False
            endOfLinePos += len(fmt[-1])

            for i in range(0, len(fmt), 2):
                delim = fmt[i+1]
                delimPos = buff.find(delim, buffPos, endOfLinePos)
                if delimPos == -1:
                    print("[ERROR] Can't find next delimeter. Stopping parsing.")
                    bar.finish()
                    return False
                info[chr(fmt[i][1])] = buff[buffPos:delimPos]
                buffPos = delimPos + len(delim)

            self.outFile.write(b':'.join([info.get(x, b"").strip() for x in Parser.PARAMS]) + b"\n")

            if len(buff) - buffPos < self.refillThreshold:
                barCounter += buffPos
                bar.update(barCounter)
                buff = buff[buffPos:] + self.readChunk(file)
                buffPos = 0
                suffixPos = buff.find(self.parseFormat.suffixJunk)
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
