import json

class ParseFormat(object):
    PARAMS = "euphstflmd"
    JUNK_PARAM = 'J'

    def __init__(self, formatDict):
        self.prefixJunk = formatDict.get("prefixjunk", "").encode()
        self.suffixJunk = formatDict.get("suffixjunk", "").encode()
        self.delimiter = formatDict.get("delimiter", "").encode()
        self.lineDelimiter = formatDict.get("linedelimiter", "").encode()
        self.format = formatDict.get("parseformat", "").encode()

    def toJSON(self):
        data = {
            "prefixjunk" : self.prefixJunk.decode(),
            "suffixjunk" : self.suffixJunk.decode(),
            "delimiter" : self.delimiter.decode(),
            "linedelimiter" : self.lineDelimiter.decode(),
            "parseformat" : self.format.decode()
        }
        return data


    def saveToFile(self, fileName):
        with open(fileName, 'wb') as f:
            f.write(json.dumps(self.toJSON()).encode())

    @staticmethod
    def loadFromFile(fileName):
        with open(fileName, "rb") as f:
            formatDict = json.loads(f.read())
        return ParseFormat(formatDict)

    def __str__(self):
        return self.delimiter.decode().join(list(self.format.decode()))
