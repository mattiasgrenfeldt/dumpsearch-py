import json

class ParseFormat(object):
    PARAMS = "enphstflmd"
    JUNK_PARAM = 'J'

    def __init__(self, formatDict):
        self.prefixJunk = formatDict.get("prefixjunk", "").encode()
        self.suffixJunk = formatDict.get("suffixjunk", "").encode()
        self.delimiter = formatDict.get("delimiter", "").encode()
        self.lineDelimiter = formatDict.get("linedelimiter", "").encode()
        self.format = formatDict.get("parseformat", "").encode()
        if self.suffixJunk == b"":
            self.suffixJunk = b"\x00"*5

    def saveToFile(self, fileName):
        with open(fileName, 'wb') as f:
            data = {
                "prefixjunk" : self.prefixJunk,
                "suffixjunk" : self.suffixJunk,
                "delimiter" : self.delimiter,
                "lineDelimiter" : self.lineDelimiter,
                "parseformat" : self.format
            }
            f.write(json.dumps(data))

    @staticmethod
    def loadFromFile(fileName):
        with open(fileName, "rb") as f:
            formatDict = json.loads(f.read())
        return ParseFormat(formatDict)

    def __str__(self):
        return self.delimiter.decode().join(list(self.format.decode()))
