import re, json

class ParseFormat(object):
    def __init__(self, fileName, PARAMS, JUNK_PARAM):
        with open(fileName, "rb") as f:
            parseObject = json.loads(f.read())
        self.prefixJunk = parseObject.get("prefixjunk", "").encode()
        self.suffixJunk = parseObject.get("suffixjunk", "").encode()
        if self.suffixJunk == b"":
            self.suffixJunk = b"\x00"*5
        
        f = parseObject["parseformat"]
        positions = [x.start() for x in list(re.finditer("(^|[^%])%[" + PARAMS + JUNK_PARAM + "]", f))]
        positions = [x + 1 if x != 0 else x for x in positions]
        self.formatIsVar = []
        self.format = []
        
        lastPos = 0
        for p in positions:
            self.format.append(f[lastPos:p].encode())
            self.formatIsVar.append(False)
            self.format.append(f[p:p+2].encode())
            self.formatIsVar.append(True)
            lastPos = p + 2
        self.format.append(f[lastPos:].encode())
        self.formatIsVar.append(False)
        if self.format[0] == b"":
            self.format = self.format[1:]
            self.formatIsVar = self.formatIsVar[1:]
        if not self.formatIsVar[0]:
            self.format = ["%" + JUNK_PARAM] + self.format
            self.formatIsVar = [True] + self.format

    def __str__(self):
        return b"".join(self.format).decode().strip()
