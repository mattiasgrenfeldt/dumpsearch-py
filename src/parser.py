import os, progressbar, re
import os.path as path
import parseformat

class Parser(object):
    EMAIL_REGEX = b"[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+[.])+[a-zA-Z0-9-]+"

    def __init__(self, parseFormat, outFileName):
        self.chunkSize = int(1e6)
        self.refillThreshold = self.chunkSize//10
        self.outFile = open(outFileName, "ab")
        self.parseFormat = parseFormat

    def __del__(self):
        self.outFile.close()

    def readChunk(self, file):
        return file.read(self.chunkSize)

    def parseFile(self, fileName, dumpName, junkFolder):
        print("[*] Parsing: %s" % fileName)
        file = open(fileName, "rb")
        junkFileName = "%s.junk" % path.join(junkFolder, path.basename(path.abspath(fileName)))
        junkFile = open(junkFileName, "wb")
        fileSize = os.stat(fileName).st_size
        bar = progressbar.ProgressBar(max_value=fileSize)
        barCounter = 0

        buff = self.readChunk(file)

        buffPos = buff.find(self.parseFormat.prefixJunk) + len(self.parseFormat.prefixJunk)
        suffixJunk = self.parseFormat.suffixJunk if self.parseFormat.suffixJunk != b"" else b"\x00"*10
        suffixPos = buff.find(suffixJunk, buffPos)

        emailError = False
        lineError = False

        fmt = self.parseFormat.format
        dumpName = dumpName.encode()
        while len(buff) and buffPos != suffixPos:
            endOfLinePos = buff.find(self.parseFormat.lineDelimiter, buffPos)
            if endOfLinePos == -1:
                bar.finish()
                print("[WARN] Can't find next end of line. Stopping parsing.")
                file.close()
                junkFile.close()
                return False

            line = buff[buffPos:endOfLinePos]
            values = line.split(self.parseFormat.delimiter)
            if len(values) != len(self.parseFormat.format):
                lineError = True
                junkFile.write(b"%s\n" % line)
            else:
                info = {k:v for (k,v) in zip(self.parseFormat.format.decode(), values)}
                info['d'] = dumpName
                if 'e' in info and info['e'] != b'' and re.fullmatch(Parser.EMAIL_REGEX, info['e'].strip()) == None:
                    emailError = True
                    junkFile.write(b"%s\n" % line)
                else:
                    self.outFile.write(b':'.join([info.get(x, b"").strip() for x in parseformat.ParseFormat.PARAMS]) + b"\n")

            buffPos = endOfLinePos + len(self.parseFormat.lineDelimiter)

            if len(buff) - buffPos < self.refillThreshold:
                barCounter += buffPos
                bar.update(barCounter)
                buff = buff[buffPos:] + self.readChunk(file)
                buffPos = 0
                suffixPos = buff.find(suffixJunk)
        
        bar.finish()
        file.close()
        if junkFile.tell() == 0:
            junkFile.close()
            os.unlink(junkFileName)
        else:
            junkFile.close()
        if lineError:
            print("[WARN] Line errors occured, check junk file.")
        if emailError:
            print("[WARN] Some emails didn't look like emails, check junk file.")
        return True

    def parseFolder(self, folderName, dumpName, junkFolder, ext='.txt'):
        files = os.listdir(folderName)
        files = [f for f in files if f.endswith(ext)]
        print("[*] Parsing %d files." % len(files))
        errorFiles = []
        for f in files:
            if not self.parseFile(path.join(folderName, f), dumpName, junkFolder):
                errorFiles.append(f)
        if len(errorFiles):
            print("[ERROR] Problems were found while parsing the following files:")
            print(errorFiles)
