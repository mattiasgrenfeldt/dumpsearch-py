import os, progressbar, re
import os.path as path
import parseformat

EMAIL_REGEX = re.compile("[a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~.]+@([a-zA-Z0-9-]+[.])+[a-zA-Z0-9-]+")

class Parser(object):

    def __init__(self, parseFormat, exporter):
        self.chunkSize = int(5e6)
        self.refillThreshold = self.chunkSize//10
        self.parseFormat = parseFormat
        self.exporter = exporter

    def readChunk(self, file):
        return file.read(self.chunkSize)

    def parseFile(self, fileName, dumpName, junkFolder, doProgBar=True):
        file = open(fileName, "rb")
        junkFileName = "%s.junk" % path.join(junkFolder, path.basename(path.abspath(fileName)))
        junkFile = open(junkFileName, "wb")
        
        if doProgBar:
            print("[*] Parsing: %s" % fileName)
            barCounter = 0
            fileSize = os.stat(fileName).st_size
            bar = progressbar.ProgressBar(max_value=fileSize)

        buff = self.readChunk(file)

        buffPos = buff.find(self.parseFormat.prefixJunk) + len(self.parseFormat.prefixJunk)
        suffixJunk = self.parseFormat.suffixJunk if self.parseFormat.suffixJunk != b"" else b"\x00"*10
        suffixPos = buff.rfind(suffixJunk, buffPos)

        emailError = False
        lineError = False
        fileEmpty = False

        assert all([c in (parseformat.PARAMS + parseformat.JUNK_PARAM) for c in self.parseFormat.format.decode()]), "[ERROR] Unknown parse parameter"

        dataEntries = []

        # optimizations
        lineDelimiter = self.parseFormat.lineDelimiter
        lineDelimiterLen = len(self.parseFormat.lineDelimiter)
        exportEntries = self.exporter.exportEntries
        delimiter = self.parseFormat.delimiter
        formatExtended = self.parseFormat.formatExtended
        formatLen = len(self.parseFormat.format)
        junkWrite = junkFile.write
        regexFullMatch = EMAIL_REGEX.fullmatch

        while buffPos < len(buff) and buffPos != suffixPos:
            endOfLinePos = buff.find(lineDelimiter, buffPos)
            endOfLinePos = endOfLinePos if endOfLinePos != -1 else len(buff)

            line = buff[buffPos:endOfLinePos]
            values = line.split(delimiter)
            if len(values) != formatLen:
                lineError = True
                junkWrite(b"%s\n" % line)
            else:
                try:
                    info = {k:v.decode() for (k,v) in zip(formatExtended, values) if v != b"" and len(v) < 500} # Mongodb won't index fields larger than 1024
                    if 'email' in info and regexFullMatch(info['email'].strip()) == None:
                        emailError = True
                        junkWrite(b"%s\n" % line)
                    else:
                        info.pop("junk", "")
                        info['dumpsource'] = dumpName
                        if 'email' in info:
                            email = info['email']
                            info['domain'] = email[email.find("@") + 1:]
                        dataEntries.append(info)
                except UnicodeDecodeError as e:
                    lineError = True
                    junkWrite(b"%s\n" % line)

            buffPos = endOfLinePos + lineDelimiterLen

            if not fileEmpty and len(buff) - buffPos < self.refillThreshold:
                exportEntries(dataEntries)
                dataEntries = []
                if doProgBar:
                    barCounter += buffPos
                    bar.update(barCounter)
                nextChunk = self.readChunk(file)
                if len(nextChunk) == 0:
                    fileEmpty = True
                buff = buff[buffPos:] + nextChunk
                buffPos = 0
                suffixPos = buff.rfind(suffixJunk)
        
        exportEntries(dataEntries)
        if doProgBar:
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
        return not (emailError or lineError)

    def parseFolder(self, folderName, dumpName, junkFolder, ext='.txt'):
        files = os.listdir(folderName)
        files = [f for f in files if f.endswith(ext)]
        fileSizes = [os.stat(path.join(folderName, f)).st_size for f in files]

        print("[*] Parsing %d files." % len(files))
        bar = progressbar.ProgressBar(max_value=sum(fileSizes)/1e9)
        errorFiles = []
        cumSum = 0
        bar.update(cumSum)
        for (i,f) in enumerate(files):
            if not self.parseFile(path.join(folderName, f), dumpName, junkFolder, False):
                errorFiles.append(f)
            cumSum += fileSizes[i]
            bar.update(cumSum/1e9)
        bar.finish()
        if len(errorFiles):
            print("[ERROR] Problems were found while parsing the following %d files:" % len(errorFiles))
            print(errorFiles)
