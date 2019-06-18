import json, pymongo
import exporter

# Add emailprefix and emaildomain
SEARCHABLE_FIELDS = ["email", "domain", "username", "password", "hash", "firstname", "lastname", "phone", "dumpsource"]

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

    def search(self, field, value, n=1, offset=0, useRegex=False, useJson=False):
        if field not in SEARCHABLE_FIELDS:
            print("[ERROR] Unknown search field %s" % field)
            return (0, [])
        searchObject = {field: value}
        if useRegex:
            searchObject = {field: {"$regex": value}}
        elif useJson:
            print(value)
            searchObject = json.loads(value)
        nDocs = self.collection.count_documents(searchObject, limit=int(1e5))
        if nDocs == 0:
            return (0, [])
        res = self.collection.find(searchObject)
        return (nDocs, res[offset:offset + n])

    def buildIndexes(self):
        print("[*] Building DB indexes. This will take a long time if they haven't been built yet. Go get a coffee.")
        indexSizes = self.db.command("collStats", self.collectionName)["indexSizes"]
        for f in FIELDS:
            if f + "_1" not in indexSizes:
                print("Creating index:", f)
                self.collection.create_index(f, partialFilterExpression={f:{"$exists": True}})

    def deleteIndexes(self):
        self.collection.drop_indexes()

    def exportEntry(self, entry):
        self.collection.insert_one(entry)

    def exportEntries(self, entryList):
        if len(entryList):
            self.collection.insert_many(entryList)
        