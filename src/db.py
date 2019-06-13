import json, pymongo
import exporter

FIELDS = ["email", "username", "password", "hash", "firstname", "lastname", "phone", "dumpsource"]

class DBConnection(exporter.Exporter):

    def __init__(self, configFileName):
        super().__init__()
        with open(configFileName, "rb") as f:
            config = json.loads(f.read())
        config["port"] = config["port"] if "port" in config else 27017
        self.config = config
        self.client = pymongo.MongoClient(config["ip"], config["port"])
        self.db = self.client["dumpsearch"]
        self.collectionName = "data"
        self.collection = self.db[self.collectionName]

    def search(self, field, value, n=1, offset=0):
        if field not in FIELDS:
            print("[ERROR] Unknown search field %s" % field)
            return (0, [])
        nDocs = self.collection.count_documents({field: value}, limit=int(1e5))
        res = self.collection.find({field: value})
        return (nDocs, res[offset:offset + n])

    def buildIndexes(self):
        print("[*] Building DB indexes. This might take a long time if they haven't been built yet.")
        indexSizes = self.db.command("collStats", self.collectionName)["indexSizes"]
        for f in FIELDS:
            if f + "_1" not in indexSizes:
                print("Creating index:", f)
                self.collection.create_index(f, partialFilterExpression={f:{"$exists": True}})

    def deleteIndexes(self):
        pass

    def exportEntry(self, entry):
        self.collection.insert_one(entry)

    def exportEntries(self, entryList):
        if not len(entryList):
            return
        self.collection.insert_many(entryList)
        