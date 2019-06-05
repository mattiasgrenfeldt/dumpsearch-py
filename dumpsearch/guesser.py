import os, sys
import parseformat

class Guesser(object):
    DELIMITERS = ":;,| \t"

    def __init__(self):
        pass
        
    def guessFormat(self, fileName, outFile=None):
        fmt = {}
        file = open(fileName, "rb")
        fileSize = os.stat(fileName).st_size
        chunkSize = min(fileSize//10, int(1e5))

        # find linedelimiter
        buff = file.read(chunkSize)
        if chr(buff[buff.find(b"\n")-1]) == '\r':
            fmt["linedelimiter"] = "\r\n"
        else:
            fmt["linedelimiter"] = "\n"
        lineDelim = fmt["linedelimiter"].encode()

        # find delimiter and number of paramters
        file.seek((fileSize - chunkSize)//2)
        buff = file.read(chunkSize)
        buff = buff.split(lineDelim)[1:-1]
        bestDelim = []
        for d in Guesser.DELIMITERS.encode():
            s = 0.0
            for line in buff:
                s += line.count(d)
            bestDelim.append((float(s)/len(buff), d))
        bestDelim.sort()

        delim = chr(bestDelim[-1][1]).encode()
        numOfParams = {}
        for line in buff[1:]:
            count = line.count(delim) + 1
            if count not in numOfParams:
                numOfParams[count] = 0
            numOfParams[count] += 1
        numberOfParamters = max([(v,k) for (k,v) in list(numOfParams.items())])[1]
        if len(numOfParams) != 1:
            print("[WARN] Lines have different number of columns. Using delimiter: %s" % repr(delim))
            print('\n'.join(list(map(repr, numOfParams.items()))))
            print("Using", numberOfParamters, "columns\n")
        fmt["delimiter"] = delim.decode()
        fmt["parseformat"] = "J"*numberOfParamters

        # find prefixjunk
        file.seek(0)
        buff = file.read(chunkSize)
        lines = buff.split(lineDelim)
        for line in lines:
            if self.lineFollowsFormat(line, delim, numberOfParamters):
                linePos = buff.find(line)
                fmt["prefixjunk"] = buff[linePos-10:linePos].decode()
                break

        # find suffixjunk
        file.seek(fileSize - chunkSize)
        buff = file.read(chunkSize)
        lines = buff.split(lineDelim)
        for line in lines[::-1]:
            if self.lineFollowsFormat(line, delim, numberOfParamters):
                linePos = buff.find(line) + len(line) + len(lineDelim)
                fmt["suffixjunk"] = buff[linePos:linePos + 10].decode()
                break

        pf = parseformat.ParseFormat(fmt)
        if outFile != None:
            pf.saveToFile(outFile)
        return pf

    def lineFollowsFormat(self, line, delim, numberOfParamters):
        return (line.count(delim) + 1) == numberOfParamters