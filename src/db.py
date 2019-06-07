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

    def buildIndexes(self):
        pass

    '''
    | e | **E**mail |
    | u | **U**sername |
    | p | **P**assword |
    | h | **H**ash |
    | s | **S**alt |
    | t | hash**T**ype |
    | f | **F**irstname |
    | l | **L**astname |
    | n | pho**n**e |
    | d | **D**umpsource |
    | J | **J**unk |
    '''
    def exportEntry(self, entry):
        #TODO: Change this
        translation = {
            'e':"email",
            'u':"username",
            'p':"password",
            'h':"hash",
            's':"salt",
            't':"hashtype",
            'f':"firstname",
            'l':"lastname",
            'n':"phone",
            'd':"dumpsource",
        }
        newEntry = {}
        for k,v in translation.items():
            if k in entry:
                newEntry[v] = entry[k].decode()
        self.collection.insert_one(newEntry)

    def exportEntries(self, entryList):
        raise NotImplementedError("Implement in subclass")
        