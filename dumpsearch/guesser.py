import os
import parseformat

class Guesser(object):
    DELIMITERS = ":;,| \t"

    def __init__(self):
        pass
        
    def guessFormat(self, fileName, outFile=None):
        fmt = {}


        pf = parseformat.ParseFormat(fmt)
        if outFile != None:
            pf.saveToFile(outFile)
        return pf

