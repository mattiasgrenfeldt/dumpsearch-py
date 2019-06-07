import json
import parseformat

class Exporter(object):

    def exportEntry(self, entry):
        raise NotImplementedError("Implement in subclass")

    def exportEntries(self, entryList):
        raise NotImplementedError("Implement in subclass")

class FileExporter(Exporter):

    def __init__(self, fileName, writeMode="ab"):
        super().__init__()
        self.outFile = open(fileName, writeMode)

    def __del__(self):
        self.outFile.close()

    def exportEntry(self, entry):
        self.outFile.write(b':'.join([entry.get(x, b"").strip() for x in parseformat.PARAMS]) + b"\n")

    def exportEntries(self, entryList):
        for entry in entryList:
            self.exportEntry(entry)


class DBExporter(Exporter):

    def __init__(self, configFileName):
        super().__init__()
        with open(configFileName, "rb") as f:
            config = json.loads(f.read())
        config["port"] = config["port"] if "port" in config else 3306
        config["db"] = config["db"] if "db" in config else "dumpsearch"
        self.config = config
    def buildDB(self):
        print("BUILDING DB")

    def exportEntry(self, entry):
        raise NotImplementedError("Implement in subclass")

    def exportEntries(self, entryList):
        raise NotImplementedError("Implement in subclass")
        