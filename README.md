
# dumpsearch

A tool for parsing and searching through datadumps. Uses MongoDB for storage.

## Install

Install with `pip` using:
```
pip install -r requirements.txt
```
Install with `pipenv` using:
```
pipenv install
```

You also need a MongoDB server. See [here](https://docs.mongodb.com/manual/installation/) for installation instructions.

## Usage

### Guessing

To parse a datadump you need a format file describing the format of the dump. The program can guess the format of the dump given the dump file. It's best to double check if the format is correct before starting to parse.

```
./dumpsearch.py guess dump.txt -f format.json
```

### Parseformat

The format file has the following fields:

| Field           | Sample Value       | Explanation |
| --------------- | ------------------ | ----------- |
| `prefixjunk`    | `"prefixend\n"`    | The last chars before the data starts, `""` if the data starts directly.           |
| `suffixjunk`    | `"suffixstart"`    | The first chars after the data ends, `""` if the data ends at the end of the file. |
| `delimiter`     | `":"`              | Delimiter between dump fields.                                                     |
| `linedelimiter` | `"\n"` or `"\r\n"` | Line endings.                                                                      |
| `parseformat`   | `"ueJJJJJJJJhs"`   | Specifies which fields contain which data.                                         |

The `parseformat` field has the following parameters:

| Parameter | Value |
| --------- | ----- |
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

### Parsing

To parse a dump run:

```
./dumpsearch.py parse format.json dump.txt # Will import to DB specified in dbconfig.json
./dumpsearch.py parse format.json dump.txt -c dbconfig2.json # Will import to DB specified in dbconfig2.json
./dumpsearch.py parse format.json dump.txt -o outfile.txt # Dump to file, not to DB
```

### Searching

To search through the database use:

```
./dumpsearch.py search <field> <value> # Searches in database from dbconfig.json
./dumpsearch.py search <field> <value> -c dbconfig2.json # Searches in database from dbconfig2.json
./dumpsearch.py search username johnDoe
./dumpsearch.py search username ^john.oe -r # Searches using regex
```
