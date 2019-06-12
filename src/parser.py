import os, progressbar, re
import os.path as path
import parseformat

class Parser(object):
    EMAIL_REGEX = "[a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~.]+@([a-zA-Z0-9-]+[.])+[a-zA-Z0-9-]+"

    def __init__(self, parseFormat, exporter):
        self.chunkSize = int(5e6)
        self.refillThreshold = self.chunkSize//10
        self.parseFormat = parseFormat
        self.exporter = exporter

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
        fileEmpty = False

        assert all([c in (parseformat.PARAMS + parseformat.JUNK_PARAM) for c in self.parseFormat.format.decode()]), "[ERROR] Unknown parse parameter"

        dataEntries = []
        while buffPos < len(buff) and buffPos != suffixPos:
            endOfLinePos = buff.find(self.parseFormat.lineDelimiter, buffPos)
            if endOfLinePos == -1:
                self.exporter.exportEntries(dataEntries)
                print("[WARN] Can't find next end of line. Stopping parsing.")
                break

            line = buff[buffPos:endOfLinePos]
            values = line.split(self.parseFormat.delimiter)
            if len(values) != len(self.parseFormat.format):
                lineError = True
                junkFile.write(b"%s\n" % line)
            else:
                info = {k:v.decode() for (k,v) in zip(self.parseFormat.formatExtended, values)}
                info.pop("junk", "")
                info['dumpsource'] = dumpName
                if 'email' in info and info['email'] != '' and re.fullmatch(Parser.EMAIL_REGEX, info['email'].strip()) == None:
                    emailError = True
                    junkFile.write(b"%s\n" % line)
                else:
                    dataEntries.append(info)

            buffPos = endOfLinePos + len(self.parseFormat.lineDelimiter)

            if not fileEmpty and len(buff) - buffPos < self.refillThreshold:
                self.exporter.exportEntries(dataEntries)
                dataEntries = []
                barCounter += buffPos
                bar.update(barCounter)
                nextChunk = self.readChunk(file)
                if len(nextChunk) == 0:
                    fileEmpty = True
                buff = buff[buffPos:] + nextChunk
                buffPos = 0
                suffixPos = buff.find(suffixJunk)
        
        self.exporter.exportEntries(dataEntries)
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
        print("[*] Parsing %d files." % len(files))
        errorFiles = []
        for (i,f) in enumerate(files):
            print("[*] File %d of %d." % (i, len(files)))
            if not self.parseFile(path.join(folderName, f), dumpName, junkFolder):
                errorFiles.append(f)
        if len(errorFiles):
            print("[ERROR] Problems were found while parsing the following %d files:" % len(errorFiles))
            print(errorFiles)
