import json, pymongo
import exporter

class DBConnection(exporter.Exporter):

    def __init__(self, configFileName):
        super().__init__()
        with open(configFileName, "rb") as f:
            config = json.loads(f.read())
        config["port"] = config["port"] if "port" in config else 27017
        self.config = config
        self.client = pymongo.MongoClient(config["ip"], config["port"])
        self.db = self.client["dumpsearch"]
        self.collection = self.db["data"]

    def search():
        pass

    def buildIndexes(self):
        pass

    def exportEntry(self, entry):
        self.collection.insert_one(entry)

    def exportEntries(self, entryList):
        if not len(entryList):
            return
        self.collection.insert_many(entryList)
        