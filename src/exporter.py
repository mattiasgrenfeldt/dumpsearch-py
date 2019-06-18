import parseformat

class Exporter(object):

    def exportEntry(self, entry):
        raise NotImplementedError("Implement in subclass")

    def exportEntries(self, entryList):
        raise NotImplementedError("Implement in subclass")

class FileExporter(Exporter):

    def __init__(self, fileName, writeMode="ab"):
        super().__init__()
        self.params = [parseformat.PARAMS_EXTENDED[0]] + ['domain'] + parseformat.PARAMS_EXTENDED[1:]
        self.outFile = open(fileName, writeMode)

    def __del__(self):
        self.outFile.close()

    def exportEntry(self, entry):
        self.outFile.write(b'\t'.join([entry.get(x, "").strip().encode() for x in self.params]) + b"\n")

    def exportEntries(self, entryList):
        for entry in entryList:
            self.exportEntry(entry)
